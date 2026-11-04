import datetime
import email
import imaplib
import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from ..database import get_connection


def save_email_message(contact_id, direction, from_email, to_email, subject, body):
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
                received_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            ),
        )

        connection.commit()
        return True
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
        mail.select("inbox")

        status, data = mail.search(None, "ALL")
        message_ids = data[0].split()
        messages = []

        for msg_id in message_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
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

            messages.append(msg_record)
            from_email = parseaddr(message.get("From", ""))[1]
            save_email_message(
                contact_id=None,
                direction="inbound",
                from_email=from_email,
                to_email=message.get("To"),
                subject=message.get("Subject"),
                body=body,
            )

        mail.logout()
        return messages
    except Exception as exc:
        print(f"Inbox fetch failed: {exc}")
        return []