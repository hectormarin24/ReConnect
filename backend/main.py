from fastapi import Depends, FastAPI, HTTPException, Request, Response, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from .twilio_webhooks import validate_twilio_webhook
import os

import logging

from mysql.connector import Error as MySQLError
from twilio.twiml.messaging_response import MessagingResponse

from .registration import process_registration_message

from .message_store import (
    save_incoming_message,
    list_messages_for_user,
    count_unread_messages,
    mark_message_as_read,
)

from .twilio_service import (
    connect_twilio_account,
    list_twilio_accounts,
    list_sms_senders,
    send_sms,
    send_sms_batch,
    get_owned_twilio_account
)

from .auth import (
    authenticate_user,
    create_user,
    create_session,
    get_current_user,
)

from .schemas import (
    LoginRequest,
    RegisterRequest,
    TwilioAccountConnectRequest,
    TwilioAccountResponse,
    TwilioSmsSenderResponse,
    SmsSendRequest,
    SmsSendResponse,
    TwilioMessageResponse,
    UnreadCountResponse,
    MessageReadResponse,
    BulkSmsSendRequest,
    BulkSmsSendResponse,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="ReConnect Backend")

@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
):
    safe_errors = [
        {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": safe_errors},
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/register")
def register(request: RegisterRequest):
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters.",
        )

    created = create_user(
        request.full_name,
        request.email,
        request.password,
    )

    if not created:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    return {
        "success": True,
        "message": "Account created successfully.",
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = authenticate_user(
        request.email,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = create_session(user["id"])

    return {
        "success": True,
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }

@app.get("/auth/me")
def get_my_account(current_user: dict = Depends(get_current_user)):
    return {
        "user": current_user,
    }

@app.post(
    "/twilio/accounts",
    status_code=201,
    response_model=TwilioAccountResponse,
)
def add_twilio_account(
    request: TwilioAccountConnectRequest,
    current_user: dict = Depends(get_current_user),
):
    return connect_twilio_account(
        user_id=current_user["id"],
        label=request.label,
        account_sid=request.account_sid,
        auth_token=request.auth_token.get_secret_value(),
    )

@app.get(
    "/twilio/accounts",
    response_model=list[TwilioAccountResponse],
)
def get_twilio_accounts(
    current_user: dict = Depends(get_current_user),
):
    return list_twilio_accounts(current_user["id"])

@app.get(
    "/twilio/accounts/{account_id}/sms-senders",
    response_model=list[TwilioSmsSenderResponse],
)
def get_sms_senders(
    account_id: int,
    current_user: dict = Depends(get_current_user),
):
    return list_sms_senders(
        user_id=current_user["id"],
        account_id=account_id,
    )

@app.post(
    "/twilio/accounts/{account_id}/sms",
    status_code=201,
    response_model=SmsSendResponse,
)
def send_account_sms(
    account_id: int,
    request: SmsSendRequest,
    current_user: dict = Depends(get_current_user),
):
    return send_sms(
        user_id=current_user["id"],
        account_id=account_id,
        from_number=request.from_number,
        to_number=request.to_number,
        body=request.body,
    )

@app.post("/webhooks/twilio/incoming")
async def receive_twilio_message(request: Request):
    content_type = (
        request.headers.get("content-type", "")
        .split(";", 1)[0]
        .strip()
        .lower()
    )

    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(
            status_code=415,
            detail="Expected a form-encoded Twilio webhook.",
        )

    base_url = os.getenv("TWILIO_WEBHOOK_BASE_URL", "").rstrip("/")

    if not base_url:
        raise HTTPException(
            status_code=503,
            detail="The public webhook URL is not configured.",
        )

    public_url = f"{base_url}/webhooks/twilio/incoming"

    if request.url.query:
        public_url += f"?{request.url.query}"

    form = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")

    account_id = await run_in_threadpool(
        validate_twilio_webhook,
        public_url,
        form,
        signature,
    )

    message_sid = form.get("MessageSid")
    from_address = form.get("From")
    to_address = form.get("To")
    body = form.get("Body", "")

    required_values = (message_sid, from_address, to_address)

    if not all(
        isinstance(value, str) and value
        for value in required_values
    ):
        raise HTTPException(
            status_code=400,
            detail="MessageSid, From, and To are required.",
        )

    if (
        len(message_sid) != 34
        or len(from_address) > 64
        or len(to_address) > 64
        or not isinstance(body, str)
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid incoming-message fields.",
        )

    channel = (
        "whatsapp"
        if from_address.startswith("whatsapp:")
        else "sms"
    )

    saved = await run_in_threadpool(
        save_incoming_message,
        account_id,
        message_sid,
        channel,
        from_address,
        to_address,
        body,
    )

    if not saved:
        raise HTTPException(
            status_code=503,
            detail="Unable to save the incoming message.",
        )

    if channel != "sms":
        return Response(status_code=204)

    opt_out_type = form.get("OptOutType", "")

    if opt_out_type not in ("", "STOP", "START", "HELP"):
        raise HTTPException(
            status_code=400,
            detail="Invalid OptOutType.",
        )

    try:
        reply = await run_in_threadpool(
            process_registration_message,
            account_id,
            message_sid,
            opt_out_type,
        )

    except (MySQLError, RuntimeError, ValueError) as error:
        logger.error(
            "Registration failed for message %s: %s, database code %s",
            message_sid,
            type(error).__name__,
            getattr(error, "errno", None),
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Registration is temporarily unavailable. "
                "Please retry."
            ),
        ) from None

    response = MessagingResponse()

    if reply:
        response.message(reply)

    return Response(
        content=str(response),
        media_type="application/xml",
    )

@app.get(
    "/twilio/accounts/{account_id}/messages",
    response_model=list[TwilioMessageResponse],
)
def get_message_history(
    account_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    before_id: int | None = Query(default=None, gt=0),
    current_user: dict = Depends(get_current_user),
):
    get_owned_twilio_account(current_user["id"], account_id)

    return list_messages_for_user(
        user_id=current_user["id"],
        account_id=account_id,
        limit=limit,
        before_id=before_id,
    )

@app.get(
    "/notifications/unread-count",
    response_model=UnreadCountResponse,
)
def get_unread_count(
    current_user: dict = Depends(get_current_user),
):
    return {
        "unread_count": count_unread_messages(current_user["id"]),
    }

@app.patch(
    "/twilio/messages/{message_id}/read",
    response_model=MessageReadResponse,
)
def mark_twilio_message_read(
    message_id: int,
    current_user: dict = Depends(get_current_user),
):
    return mark_message_as_read(
        user_id=current_user["id"],
        message_id=message_id,
    )

@app.post(
    "/twilio/accounts/{account_id}/sms/bulk",
    response_model=BulkSmsSendResponse,
)
def send_account_sms_batch(
    account_id: int,
    request: BulkSmsSendRequest,
    current_user: dict = Depends(get_current_user),
):
    return send_sms_batch(
        user_id=current_user["id"],
        account_id=account_id,
        messages=[
            message.model_dump()
            for message in request.messages
        ],
    )