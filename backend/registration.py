import os
import re

from mysql.connector import IntegrityError

from .database import get_connection
from .contacts import (
    get_contact_by_phone,
    get_registration_session,
    start_registration_session,
    save_registration_name,
    complete_registration,
)


STOP_WORDS = {
    "STOP",
    "STOPALL",
    "UNSUBSCRIBE",
    "CANCEL",
    "END",
    "QUIT",
    "REVOKE",
    "OPTOUT",
}

CONTROL_WORDS = STOP_WORDS | {
    "START",
    "UNSTOP",
    "YES",
    "HELP",
    "INFO",
}


def registration_target():
    account = os.getenv(
        "REGISTRATION_TWILIO_ACCOUNT_ID", ""
    ).strip()

    number = os.getenv(
        "REGISTRATION_PHONE_NUMBER", ""
    ).strip()

    if not account.isdecimal() or int(account) < 1:
        raise RuntimeError(
            "Set REGISTRATION_TWILIO_ACCOUNT_ID."
        )

    if not re.fullmatch(r"\+[1-9][0-9]{1,14}", number):
        raise RuntimeError(
            "Set REGISTRATION_PHONE_NUMBER in E.164 format."
        )

    return int(account), number


def handle_registration_message(
    phone: str,
    body: str,
    connection,
) -> str:
    body = body.strip()

    contact = get_contact_by_phone(
        phone,
        connection=connection,
    )

    if contact is not None:
        return "You're already registered with ReConnect."

    session = get_registration_session(
        phone,
        connection=connection,
    )

    if session is None:
        start_registration_session(
            phone,
            connection=connection,
        )

        return "Welcome to ReConnect! What is your full name?"

    if session["stage"] == "awaiting_name":
        try:
            updated = save_registration_name(
                phone,
                body,
                connection=connection,
            )

        except ValueError as error:
            return str(error)

        if not updated:
            raise RuntimeError(
                "Registration changed unexpectedly."
            )

        return "Thank you! What is your email address?"

    if session["stage"] == "awaiting_email":
        try:
            complete_registration(
                phone,
                body,
                connection=connection,
            )

        except ValueError as error:
            return str(error)

        except IntegrityError as error:
            if error.errno != 1062:
                raise

            contact = get_contact_by_phone(
                phone,
                connection=connection,
            )

            if contact is not None:
                return "You're already registered with ReConnect."

            return (
                "That email is already registered. "
                "Please enter a different email address."
            )

        return (
            "You're registered! "
            "Thank you for joining ReConnect."
        )

    raise RuntimeError("Unknown registration stage.")


def process_registration_message(
    account_id: int,
    message_sid: str,
    opt_out_type: str = "",
) -> str:
    target_account, target_number = registration_target()

    # Only the designated Twilio account handles registration.
    if account_id != target_account:
        return ""

    connection = get_connection()
    cursor = None

    try:
        connection.start_transaction(
            isolation_level="READ COMMITTED"
        )

        cursor = connection.cursor(dictionary=True)

        # Lock this message so repeated deliveries cannot process
        # the same message concurrently.
        cursor.execute(
            """
            SELECT id, from_address, to_address, body,
                   registration_reply,
                   registration_processed_at
            FROM twilio_messages
            WHERE twilio_account_id = %s
              AND message_sid = %s
              AND direction = 'inbound'
              AND channel = 'sms'
            FOR UPDATE
            """,
            (account_id, message_sid),
        )

        message = cursor.fetchone()

        if message is None:
            raise ValueError(
                "Incoming SMS message was not found."
            )

        # Other numbers can still use the normal message inbox,
        # but they do not start contact registration.
        if message["to_address"] != target_number:
            connection.commit()
            return ""

        phone = message["from_address"]

        if not re.fullmatch(r"\+[1-9][0-9]{1,14}", phone):
            connection.commit()
            return ""

        # Reuse the reply if this message already changed
        # registration successfully.
        if message["registration_processed_at"] is not None:
            reply = message["registration_reply"]

            if reply is None:
                raise RuntimeError(
                    "Processed message has no saved reply."
                )

            connection.commit()
            return reply

        # Lock one persistent row per sender. This also works
        # before that sender has a registration session.
        cursor.execute(
            """
            INSERT INTO registration_locks (phone)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE phone = phone
            """,
            (phone,),
        )

        keyword = message["body"].strip().upper()
        opt_out_type = opt_out_type.upper()

        if opt_out_type == "STOP" or keyword in STOP_WORDS:
            # Discard unfinished registration, but do not delete
            # an existing completed contact.
            cursor.execute(
                """
                DELETE FROM registration_sessions
                WHERE phone = %s
                """,
                (phone,),
            )

            reply = ""

        elif opt_out_type or keyword in CONTROL_WORDS:
            # Twilio handles these control replies. Do not save
            # the keyword as a name/email or send a second reply.
            reply = ""

        else:
            reply = handle_registration_message(
                phone=phone,
                body=message["body"],
                connection=connection,
            )

        # Save the reply in the same transaction as the
        # registration changes.
        cursor.execute(
            """
            UPDATE twilio_messages
            SET registration_reply = %s,
                registration_processed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (reply, message["id"]),
        )

        connection.commit()
        return reply

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()