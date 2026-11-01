import logging
import mysql.connector
from .database import get_connection
from datetime import timezone
from fastapi import HTTPException


logger = logging.getLogger(__name__)


def save_outgoing_message(
    account_id: int,
    channel: str,
    message,
) -> bool:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO twilio_messages (
                twilio_account_id,
                message_sid,
                channel,
                direction,
                from_address,
                to_address,
                body,
                status,
                error_code,
                is_read
            )
            VALUES (
                %s, %s, %s, 'outbound',
                %s, %s, %s, %s, %s, TRUE
            )
            ON DUPLICATE KEY UPDATE id = id
            """,
            (
                account_id,
                message.sid,
                channel,
                message.from_,
                message.to,
                message.body or "",
                message.status,
                message.error_code,
            ),
        )

        connection.commit()
        return True

    except mysql.connector.Error:
        if connection is not None:
            connection.rollback()

        logger.exception(
            "Unable to save outgoing Twilio message %s",
            message.sid,
        )

        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def save_incoming_message(
    account_id: int,
    message_sid: str,
    channel: str,
    from_address: str,
    to_address: str,
    body: str,
) -> bool:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO twilio_messages (
                twilio_account_id,
                message_sid,
                channel,
                direction,
                from_address,
                to_address,
                body,
                status,
                is_read
            )
            VALUES (
                %s, %s, %s, 'inbound',
                %s, %s, %s, 'received', FALSE
            )
            ON DUPLICATE KEY UPDATE id = id
            """,
            (
                account_id,
                message_sid,
                channel,
                from_address,
                to_address,
                body,
            ),
        )

        connection.commit()
        return True

    except mysql.connector.Error:
        if connection is not None:
            connection.rollback()

        logger.exception(
            "Unable to save incoming Twilio message %s",
            message_sid,
        )

        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def list_messages_for_user(
    user_id: int,
    account_id: int,
    limit: int = 50,
    before_id: int | None = None,
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id,
                m.twilio_account_id,
                m.message_sid,
                m.channel,
                m.direction,
                m.from_address,
                m.to_address,
                m.body,
                m.status,
                m.error_code,
                m.is_read,
                m.created_at,
                m.updated_at
            FROM twilio_messages AS m
            JOIN twilio_accounts AS a
                ON a.id = m.twilio_account_id
            WHERE a.user_id = %s
              AND m.twilio_account_id = %s
              AND (%s IS NULL OR m.id < %s)
            ORDER BY m.id DESC
            LIMIT %s
            """,
            (user_id, account_id, before_id, before_id, limit),
        )

        messages = cursor.fetchall()

        for message in messages:
            message["created_at"] = message["created_at"].replace(
                tzinfo=timezone.utc
            )
            message["updated_at"] = message["updated_at"].replace(
                tzinfo=timezone.utc
            )

        return messages

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to load message history.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def count_unread_messages(user_id: int) -> int:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS unread_count
            FROM twilio_messages AS m
            JOIN twilio_accounts AS a
                ON a.id = m.twilio_account_id
            WHERE a.user_id = %s
              AND m.direction = 'inbound'
              AND m.is_read = FALSE
            """,
            (user_id,),
        )

        result = cursor.fetchone()
        return result["unread_count"]

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to load the unread-message count.",
        ) from None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()