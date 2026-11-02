import re
from.database import get_connection #check database.py for get_connection

def get_contact_by_phone(phone: str, connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, phone, created_at
            FROM contacts
            WHERE phone = %s
            """,
            (phone,),
        )

        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()
def create_contact(
    name: str,
    email: str,
    phone: str,
    connection=None,
):
    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO contacts (name, email, phone)
            VALUES (%s, %s, %s)
            """,
            (name, email, phone),
        )

        contact_id = cursor.lastrowid

        if owns_connection:
            connection.commit()

        return contact_id

    except Exception:
        if owns_connection:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()
            
def get_registration_session(phone: str, connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT phone, stage, name, updated_at
            FROM registration_sessions
            WHERE phone = %s
            """,
            (phone,),
        )

        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()

def start_registration_session(phone: str, connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO registration_sessions (phone, stage)
            VALUES (%s, 'awaiting_name')
            """,
            (phone,),
        )

        if owns_connection:
            connection.commit()

    except Exception:
        if owns_connection:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()

def save_registration_name(
    phone: str,
    name: str,
    connection=None,
):
    name = name.strip()

    if not name or len(name) > 150:
        raise ValueError("Name must contain 1 to 150 characters.")

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE registration_sessions
            SET name = %s, stage = 'awaiting_email'
            WHERE phone = %s
              AND stage = 'awaiting_name'
            """,
            (name, phone),
        )

        updated = cursor.rowcount == 1

        if owns_connection:
            connection.commit()

        return updated

    except Exception:
        if owns_connection:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()

def complete_registration(
    phone: str,
    email: str,
    connection=None,
):
    email = email.strip()

    if (
        len(email) > 255
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        raise ValueError("Please enter a valid email address.")

    owns_connection = connection is None

    if owns_connection:
        connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT name, stage
            FROM registration_sessions
            WHERE phone = %s
            FOR UPDATE
            """,
            (phone,),
        )

        session = cursor.fetchone()

        if session is None:
            raise ValueError("No registration session exists.")

        if session["stage"] != "awaiting_email":
            raise ValueError("Registration is not ready for an email.")

        cursor.execute(
            """
            INSERT INTO contacts (name, email, phone)
            VALUES (%s, %s, %s)
            """,
            (session["name"], email, phone),
        )

        contact_id = cursor.lastrowid

        cursor.execute(
            """
            DELETE FROM registration_sessions
            WHERE phone = %s
            """,
            (phone,),
        )

        if owns_connection:
            connection.commit()

        return contact_id

    except Exception:
        if owns_connection:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if owns_connection:
            connection.close()