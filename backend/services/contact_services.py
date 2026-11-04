import json

import mysql.connector

from ..database import get_connection


def list_contacts(search: str | None = None, tag: str | None = None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, fname, lname, mname, email, phone_number, tags
            FROM contacts
            WHERE 1 = 1
        """
        params = []

        if search:
            query += """
                AND (
                    fname LIKE %s OR
                    lname LIKE %s OR
                    email LIKE %s OR
                    phone_number LIKE %s
                )
            """
            like = f"%{search}%"
            params.extend([like, like, like, like])

        if tag:
            query += " AND JSON_CONTAINS(tags, JSON_ARRAY(%s)) "
            params.append(tag)

        query += " ORDER BY fname ASC"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_contact_by_id(contact_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, fname, lname, mname, email, phone_number, tags
            FROM contacts
            WHERE id = %s
            """,
            (contact_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def search_by_name(name: str):
    return list_contacts(search=name)


def search_by_tag(tag: str):
    return list_contacts(tag=tag)


def create_contact(payload):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        tags_json = json.dumps(payload.tags or [])

        cursor.execute(
            """
            INSERT INTO contacts (fname, lname, mname, email, phone_number, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                payload.fname,
                payload.lname,
                payload.mname,
                payload.email,
                payload.phone_number,
                tags_json,
            ),
        )

        connection.commit()
        contact_id = cursor.lastrowid
        return get_contact_by_id(contact_id)

    except mysql.connector.IntegrityError as err:
        if connection is not None:
            connection.rollback()
        print(f"Integrity error: {err}")
        return None

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def update_contact(contact_id: int, payload):
    current = get_contact_by_id(contact_id)
    if current is None:
        return None

    data = current.copy()

    for field in ["fname", "lname", "mname", "email", "phone_number"]:
        value = getattr(payload, field, None)
        if value is not None:
            data[field] = value

    if payload.tags is not None:
        data["tags"] = payload.tags

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE contacts
            SET fname=%s, lname=%s, mname=%s, email=%s, phone_number=%s, tags=%s
            WHERE id=%s
            """,
            (
                data.get("fname"),
                data.get("lname"),
                data.get("mname"),
                data.get("email"),
                data.get("phone_number"),
                json.dumps(data.get("tags", [])),
                contact_id,
            ),
        )

        connection.commit()
        return get_contact_by_id(contact_id)

    except mysql.connector.IntegrityError as err:
        if connection is not None:
            connection.rollback()
        print(f"Integrity error: {err}")
        return None

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def delete_contact(contact_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE FROM contacts
            WHERE id = %s
            """,
            (contact_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        if connection is not None:
            connection.rollback()
        print(f"Database error: {err}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()