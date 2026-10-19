import bcrypt
import mysql.connector
from .database import get_connection

def authenticate_user(email: str, password: str):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, password_hash
            FROM admin_users
            WHERE email = %s
            """,
            (email,),
        )

        user = cursor.fetchone()

        if user is None:
            return None

        valid_password = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )

        if not valid_password:
            return None

        return {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def create_user(full_name: str, email: str, password: str):
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO admin_users
                (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash),
        )

        connection.commit()
        return True

    except mysql.connector.IntegrityError:
        if connection is not None:
            connection.rollback()

        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()