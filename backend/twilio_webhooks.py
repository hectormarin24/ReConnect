import re

import mysql.connector
from cryptography.fernet import InvalidToken
from fastapi import HTTPException
from starlette.datastructures import FormData
from twilio.request_validator import RequestValidator

from .database import get_connection
from .encryption import decrypt_secret


def validate_twilio_webhook(
    public_url: str,
    form: FormData,
    signature: str,
) -> int:
    invalid_webhook = HTTPException(
        status_code=403,
        detail="Invalid Twilio webhook signature.",
    )

    account_sid = form.get("AccountSid")

    if not signature:
        raise invalid_webhook

    if not isinstance(account_sid, str):
        raise invalid_webhook

    if not re.fullmatch(r"AC[0-9a-fA-F]{32}", account_sid):
        raise invalid_webhook

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, auth_token_encrypted
            FROM twilio_accounts
            WHERE account_sid = %s
            """,
            (account_sid,),
        )

        account = cursor.fetchone()

    except mysql.connector.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to verify the webhook right now.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

    if account is None:
        raise invalid_webhook

    try:
        auth_token = decrypt_secret(account["auth_token_encrypted"])

    except InvalidToken:
        raise HTTPException(
            status_code=503,
            detail="Unable to decrypt the webhook verification credential.",
        ) from None

    validator = RequestValidator(auth_token)

    if not validator.validate(public_url, form, signature):
        raise invalid_webhook

    return account["id"]