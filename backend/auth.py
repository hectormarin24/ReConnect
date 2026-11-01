import bcrypt
import hashlib
import secrets
import mysql.connector

from datetime import datetime, timedelta, timezone
from .database import get_connection
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)

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

def create_session(user_id: int):
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=8)
    ).replace(tzinfo=None, microsecond=0)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO user_sessions
                (token_hash, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (token_hash, user_id, expires_at),
        )

        connection.commit()

        return token

    except mysql.connector.Error:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired session.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    token_hash = hashlib.sha256(
        credentials.credentials.encode("utf-8")
    ).hexdigest()

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                u.id,
                u.full_name,
                u.email
            FROM user_sessions AS s
            JOIN admin_users AS u ON u.id = s.user_id
            WHERE s.token_hash = %s
              AND s.expires_at > UTC_TIMESTAMP()
            """,
            (token_hash,),
        )

        user = cursor.fetchone()

        if user is None:
            raise unauthorized

        return user

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()