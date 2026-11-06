import datetime
import email
import imaplib
import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

import mysql.connector

from ..database import get_connection


def save_email_message(
    contact_id,
    direction,
    from_email,
    to_email,
    subject,
    body,
    imap_uidvalidity=None,
    imap_uid=None,
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if direction == "inbound" and contact_id is None:
            sender_address = parseaddr(from_email or "")[1]
            if sender_address:
                cursor.execute(
                    """
                    SELECT id
                    FROM contacts
                    WHERE LOWER(email) = LOWER(%s)
                    """,
                    (sender_address,),
                )
                contact = cursor.fetchone()
                if contact is not None:
                    contact_id = contact[0]

        cursor.execute(
            """
            INSERT INTO email_messages (
                contact_id,
                direction,
                from_email,
                to_email,
                subject,
                body,
                status,
                sent_at,
                received_at,
                imap_uidvalidity,
                imap_uid
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                contact_id,
                direction,
                from_email,
                to_email,
                subject,
                body,
                "sent" if direction == "outbound" else "received",
                None if direction == "inbound" else datetime.datetime.now(),
                None if direction == "outbound" else datetime.datetime.now(),
                imap_uidvalidity,
                imap_uid,
            ),
        )

        inserted = cursor.rowcount > 0
        connection.commit()
        return inserted
    except mysql.connector.IntegrityError as exc:
        if connection is not None:
            connection.rollback()
        if (
            imap_uidvalidity is not None
            and imap_uid is not None
            and exc.errno == mysql.connector.errorcode.ER_DUP_ENTRY
        ):
            return False
        print(f"Error saving email message: {exc}")
        return False
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        print(f"Error saving email message: {exc}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def send_outbound_email(to_email: str, subject: str, body: str, contact_id=None):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM")

    if not all([host, username, password, sender]):
        raise ValueError("SMTP configuration is incomplete.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        save_email_message(
            contact_id=contact_id,
            direction="outbound",
            from_email=sender,
            to_email=to_email,
            subject=subject,
            body=body,
        )
        return True
    except Exception as exc:
        print(f"Email send failed: {exc}")
        return False


def fetch_inbound_emails():
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")

    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(username, password)
        status, _ = mail.select("inbox")
        if status != "OK":
            raise RuntimeError("Unable to select the inbox.")

        _, uidvalidity_data = mail.response("UIDVALIDITY")
        if not uidvalidity_data or not uidvalidity_data[0]:
            raise RuntimeError("The IMAP server did not provide UIDVALIDITY.")
        uidvalidity = int(uidvalidity_data[0])

        status, data = mail.uid("search", None, "ALL")
        if status != "OK":
            raise RuntimeError("Unable to search the inbox.")

        message_uids = data[0].split()
        messages = []

        for message_uid in message_uids:
            status, msg_data = mail.uid("fetch", message_uid, "(RFC822)")
            if status != "OK":
                raise RuntimeError(f"Unable to fetch inbox message UID {message_uid!r}.")

            raw_email = next(
                item[1]
                for item in msg_data
                if isinstance(item, tuple) and isinstance(item[1], bytes)
            )
            message = email.message_from_bytes(raw_email)

            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload is not None:
                            body = payload.decode("utf-8", errors="replace")
                        break
            else:
                payload = message.get_payload(decode=True)
                if payload is not None:
                    body = payload.decode("utf-8", errors="replace")

            msg_record = {
                "from": message.get("From"),
                "to": message.get("To"),
                "subject": message.get("Subject"),
                "body": body,
            }

            from_email = parseaddr(message.get("From", ""))[1]
            inserted = save_email_message(
                contact_id=None,
                direction="inbound",
                from_email=from_email,
                to_email=message.get("To"),
                subject=message.get("Subject"),
                body=body,
                imap_uidvalidity=uidvalidity,
                imap_uid=int(message_uid),
            )
            if inserted:
                messages.append(msg_record)

        mail.logout()
        return messages
    except Exception as exc:
        print(f"Inbox fetch failed: {exc}")
        return []