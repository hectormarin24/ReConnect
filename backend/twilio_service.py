from fastapi import HTTPException
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioRestException
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client
import mysql.connector

from .database import get_connection
from .encryption import encrypt_secret


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