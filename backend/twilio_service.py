from fastapi import HTTPException
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioRestException
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client
import mysql.connector
from .message_store import save_outgoing_message
import logging

from .database import get_connection
from .encryption import encrypt_secret, decrypt_secret
from cryptography.fernet import InvalidToken

logger = logging.getLogger(__name__)


def verify_twilio_credentials(account_sid: str, auth_token: str):
    http_client = TwilioHttpClient(timeout=10)

    client = Client(
        account_sid,
        auth_token,
        http_client=http_client,
    )

    try:
        account = client.api.accounts(account_sid).fetch()

    except TwilioRestException as exc:
        if exc.status == 429 or exc.status >= 500:
            raise HTTPException(
                status_code=503,
                detail="Twilio is temporarily unavailable. Try again later.",
            ) from None

        raise HTTPException(
            status_code=400,
            detail="Unable to verify the supplied Twilio account credentials.",
        ) from None

    except RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to reach Twilio. Try again later.",
        ) from None

    finally:
        if http_client.session is not None:
            http_client.session.close()

    if account.status != "active":
        raise HTTPException(
            status_code=400,
            detail="The Twilio account must be active before connecting it.",
        )

    return {
        "account_sid": account.sid,
        "friendly_name": account.friendly_name,
    }

def connect_twilio_account(
    user_id: int,
    label: str,
    account_sid: str,
    auth_token: str,
):
    verified_account = verify_twilio_credentials(
        account_sid,
        auth_token,
    )

    encrypted_token = encrypt_secret(auth_token)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO twilio_accounts
                (user_id, label, account_sid, auth_token_encrypted)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                label,
                verified_account["account_sid"],
                encrypted_token,
            ),
        )

        account_id = cursor.lastrowid

        connection.commit()

        return {
            "id": account_id,
            "label": label,
            "account_sid": verified_account["account_sid"],
            "sms_number": None,
            "whatsapp_number": None,
        }

    except mysql.connector.Error as exc:
        if connection is not None:
            connection.rollback()

        if exc.errno == 1062:
            raise HTTPException(
                status_code=409,
                detail="This Twilio account is already connected.",
            ) from None

        raise HTTPException(
            status_code=500,
            detail="Unable to save the Twilio account.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def list_twilio_accounts(user_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                label,
                account_sid,
                sms_number,
                whatsapp_number
            FROM twilio_accounts
            WHERE user_id = %s
            ORDER BY id
            """,
            (user_id,),
        )

        return cursor.fetchall()

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to load connected Twilio accounts.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def get_owned_twilio_account(user_id: int, account_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                label,
                account_sid,
                auth_token_encrypted,
                sms_number,
                whatsapp_number
            FROM twilio_accounts
            WHERE id = %s
              AND user_id = %s
            """,
            (account_id, user_id),
        )

        account = cursor.fetchone()

        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Twilio connection not found.",
            )

        return account

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to load the Twilio connection.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def list_sms_senders(user_id: int, account_id: int):
    account = get_owned_twilio_account(user_id, account_id)

    try:
        auth_token = decrypt_secret(account["auth_token_encrypted"])

    except InvalidToken:
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt the stored Twilio credentials.",
        ) from None

    http_client = TwilioHttpClient(timeout=10)

    client = Client(
        account["account_sid"],
        auth_token,
        http_client=http_client,
    )

    try:
        numbers = client.incoming_phone_numbers.list(limit=100)

        return [
            {
                "sid": number.sid,
                "phone_number": number.phone_number,
                "friendly_name": number.friendly_name,
            }
            for number in numbers
            if (number.capabilities or {}).get("sms", False)
        ]

    except TwilioRestException as exc:
        if exc.status == 429 or exc.status >= 500:
            raise HTTPException(
                status_code=503,
                detail="Twilio is temporarily unavailable. Try again later.",
            ) from None

        raise HTTPException(
            status_code=502,
            detail="Twilio could not load numbers for this connection.",
        ) from None

    except RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to reach Twilio. Try again later.",
        ) from None

    finally:
        if http_client.session is not None:
            http_client.session.close()

def send_sms(
    user_id: int,
    account_id: int,
    from_number: str,
    to_number: str,
    body: str,
):
    account = get_owned_twilio_account(user_id, account_id)

    try:
        auth_token = decrypt_secret(account["auth_token_encrypted"])

    except InvalidToken:
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt the stored Twilio credentials.",
        ) from None

    http_client = TwilioHttpClient(
        timeout=10,
        max_retries=0,
    )

    client = Client(
        account["account_sid"],
        auth_token,
        http_client=http_client,
    )

    try:
        message = client.messages.create(
            from_=from_number,
            to=to_number,
            body=body,
        )

        history_saved = save_outgoing_message(
            account_id=account["id"],
            channel="sms",
            message=message,
        )

        return {
            "sid": message.sid,
            "status": message.status,
            "history_saved": history_saved,
        }

    except TwilioRestException as exc:
        if exc.status == 429 or exc.status >= 500:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Twilio is temporarily unavailable. "
                    "Check Twilio logs before retrying."
                ),
            ) from None

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Twilio rejected the SMS request.",
                "twilio_code": exc.code,
            },
        ) from None

    except RequestException:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to confirm whether Twilio accepted the message. "
                "Check Twilio logs before retrying."
            ),
        ) from None

    finally:
        if http_client.session is not None:
            http_client.session.close()

def send_sms_batch(
    user_id: int,
    account_id: int,
    messages: list[dict],
):
    get_owned_twilio_account(user_id, account_id)

    results = []

    for item in messages:
        result = {
            "from_number": item["from_number"],
            "to_number": item["to_number"],
        }

        try:
            sent = send_sms(
                user_id=user_id,
                account_id=account_id,
                from_number=item["from_number"],
                to_number=item["to_number"],
                body=item["body"],
            )

            result.update(
                outcome="accepted",
                message=sent,
            )

        except HTTPException as exc:
            detail = exc.detail

            result["outcome"] = (
                "rejected" if exc.status_code < 500 else "unknown"
            )

            if isinstance(detail, dict):
                result["error"] = detail.get(
                    "message",
                    "The message request failed.",
                )
                result["twilio_code"] = detail.get("twilio_code")
            else:
                result["error"] = str(detail)

        except Exception:
            logger.exception(
                "Unexpected SMS batch error for connection %s",
                account_id,
            )

            result.update(
                outcome="unknown",
                error=(
                    "Unable to confirm message submission. "
                    "Check Twilio logs before retrying."
                ),
            )

        results.append(result)

    return {
        "accepted_count": sum(
            result["outcome"] == "accepted"
            for result in results
        ),
        "rejected_count": sum(
            result["outcome"] == "rejected"
            for result in results
        ),
        "unknown_count": sum(
            result["outcome"] == "unknown"
            for result in results
        ),
        "results": results,
    }