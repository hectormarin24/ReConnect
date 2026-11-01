from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .twilio_service import (
    connect_twilio_account,
    list_twilio_accounts,
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
)

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