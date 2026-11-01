import re
from.database import get_connection #check database.py for get_connection

def get_contact_by_phone(phone: str):  #function that checks for a contact via phone number
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

        connection.close()
def create_contact(name: str, email: str, phone: str):
    connection = get_connection()
    cursor = None
    
    try:
        cursor = connection.cursor() #(dictionary = True) is not necessasry here because an insert doesn't return rows.

        cursor.execute(
            """
            INSERT INTO contacts (name, email, phone)
            VALUES (%s, %s, %s)
            """,
            (name, email, phone)
        )

        contact_id = cursor.lastrowid #gets the ID mySQL assigned to the new contact
        connection.commit()

        return contact_id #for sms code result
    
    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()
   
def get_registration_session(phone: str):
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            Select phone, stage, name, updated_at
            FROM registration_sessions
            WHERE phone = %s
            """,
            (phone,),
        )
        
        return cursor.fetchone()
    
    finally:
        if cursor is not None:
            cursor.close()

        connection.close()

def start_registration_session(phone: str):
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

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()

def save_registration_name(phone: str, name: str):
    name = name.strip()

    if not name or len(name) > 150:
        raise ValueError("name must contain 1 to 150 characters.")
    
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
        connection.commit()

        return updated

    except Exception:
        connection.rollback()
        raise
    
    finally:
        if cursor is not None:
            cursor.close()
        
        connection.close()

def complete_registration(phone: str, email: str):
    email = email.strip()

    if (
        len(email) > 255
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        raise ValueError("Please enter a valid email address.")
    
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
            raise ValueError("Registration is not ready for an email") 
        
        cursor.execute(
            """
                INSERT INTO contacts (name, email, phone)
                Values (%s, %s, %s)
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
        connection.commit()
        return contact_id
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()