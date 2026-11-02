import os
import unittest
import uuid

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

import mysql.connector

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator


ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

os.environ.setdefault(
    "TWILIO_ENCRYPTION_KEY",
    Fernet.generate_key().decode(),
)

from backend import (
    contacts,
    registration,
    message_store,
    twilio_webhooks,
)
from backend.encryption import encrypt_secret
from backend.main import app


@unittest.skipUnless(
    os.getenv("RUN_MYSQL_TESTS") == "1",
    "Set RUN_MYSQL_TESTS=1",
)
class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = dict(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            time_zone="+00:00",
        )

        cls.db_name = "reconnect_sms_test_" + uuid.uuid4().hex

        connection = mysql.connector.connect(**cls.settings)
        cursor = connection.cursor()

        cursor.execute(
            f"CREATE DATABASE `{cls.db_name}`"
        )

        cursor.close()
        connection.close()

        cls.addClassCleanup(cls.drop_test_database)

        connection = cls.connect()

        try:
            cursor = connection.cursor()

            filenames = (
                "database.sql",
                "contacts.sql",
                "registration_sessions.sql",
                "registration_runtime.sql",
            )

            for filename in filenames:
                source = (
                    ROOT / "database" / filename
                ).read_text()

                for statement in source.split(";"):
                    statement = statement.strip()

                    if not statement:
                        continue

                    # Never switch to the real reconnect database.
                    if statement.upper().startswith(
                        ("USE ", "CREATE DATABASE")
                    ):
                        continue

                    cursor.execute(statement)

                    if cursor.with_rows:
                        cursor.fetchall()

            connection.commit()
            cursor.close()

        finally:
            connection.close()

        # Point all tested database functions at the temporary DB.
        for module in (
            contacts,
            registration,
            message_store,
            twilio_webhooks,
        ):
            replacement = patch.object(
                module,
                "get_connection",
                cls.connect,
            )

            replacement.start()
            cls.addClassCleanup(replacement.stop)

    @classmethod
    def connect(cls):
        return mysql.connector.connect(
            database=cls.db_name,
            **cls.settings,
        )

    @classmethod
    def drop_test_database(cls):
        connection = mysql.connector.connect(**cls.settings)

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"DROP DATABASE `{cls.db_name}`"
            )

            cursor.close()

        finally:
            connection.close()

    def sql(self, statement, params=(), fetch=False):
        connection = self.connect()

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(statement, params)

            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.lastrowid

            connection.commit()
            cursor.close()

            return result

        finally:
            connection.close()

    def setUp(self):
        # These tables are in the temporary database only.
        for table in (
            "twilio_messages",
            "registration_sessions",
            "contacts",
            "registration_locks",
            "twilio_accounts",
            "user_sessions",
            "admin_users",
        ):
            self.sql(f"DELETE FROM {table}")

        user_id = self.sql(
            """
            INSERT INTO admin_users
                (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            ("Test Staff", "staff@example.com", "unused"),
        )

        self.account_sid = "AC" + uuid.uuid4().hex
        self.token = "local-test-token"

        self.account_id = self.sql(
            """
            INSERT INTO twilio_accounts
                (user_id, label, account_sid, auth_token_encrypted)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                "Test",
                self.account_sid,
                encrypt_secret(self.token),
            ),
        )

        self.phone = "+12025550125"
        self.number = "+12025550100"
        self.base_url = "https://registration.example.test"

        environment = patch.dict(
            os.environ,
            {
                "REGISTRATION_TWILIO_ACCOUNT_ID": str(
                    self.account_id
                ),
                "REGISTRATION_PHONE_NUMBER": self.number,
                "TWILIO_WEBHOOK_BASE_URL": self.base_url,
            },
        )

        environment.start()
        self.addCleanup(environment.stop)

    def post(
        self,
        body,
        sid=None,
        signature=True,
        **extra,
    ):
        data = dict(
            AccountSid=self.account_sid,
            MessageSid=sid or "SM" + uuid.uuid4().hex,
            From=self.phone,
            To=self.number,
            Body=body,
        )

        data.update(extra)

        path = "/webhooks/twilio/incoming"

        signed = RequestValidator(
            self.token
        ).compute_signature(
            self.base_url + path,
            data,
        )

        with TestClient(app) as client:
            return client.post(
                path,
                data=data,
                headers={
                    "X-Twilio-Signature": (
                        signed if signature else "invalid"
                    ),
                },
            )

    def reply(self, response):
        self.assertEqual(
            response.status_code,
            200,
            response.text,
        )

        root = ElementTree.fromstring(response.text)
        return root.findtext("Message") or ""

    def test_full_conversation(self):
        self.assertIn(
            "full name",
            self.reply(self.post("Hello")),
        )

        self.assertIn(
            "email",
            self.reply(self.post("Test Person")),
        )

        self.assertIn(
            "registered!",
            self.reply(self.post("person@example.com")),
        )

        contact = contacts.get_contact_by_phone(self.phone)

        self.assertEqual(contact["name"], "Test Person")

        self.assertIsNone(
            contacts.get_registration_session(self.phone)
        )

        self.assertIn(
            "already registered",
            self.reply(self.post("Hello again")),
        )

    def test_invalid_answers_keep_progress(self):
        self.post("Hello")

        self.assertIn(
            "1 to 150",
            self.reply(self.post("   ")),
        )

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_name")

        self.post("Test Person")

        self.assertIn(
            "valid email",
            self.reply(self.post("invalid")),
        )

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_email")

    def test_duplicate_email_can_be_corrected(self):
        contacts.create_contact(
            "Existing",
            "used@example.com",
            "+12025550124",
        )

        self.post("Hello")
        self.post("Test Person")

        self.assertIn(
            "already registered",
            self.reply(self.post("used@example.com")),
        )

        self.assertIsNotNone(
            contacts.get_registration_session(self.phone)
        )

        self.assertIn(
            "registered!",
            self.reply(self.post("different@example.com")),
        )

    def test_duplicate_sid_reuses_reply(self):
        self.post("Hello")

        sid = "SM" + uuid.uuid4().hex

        first = self.reply(self.post("Test Person", sid))
        repeated = self.reply(self.post("Test Person", sid))

        self.assertEqual(first, repeated)

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_email")

    def test_concurrent_duplicate(self):
        sid = "SM" + uuid.uuid4().hex

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(
                    lambda _: self.post("Hello", sid),
                    range(2),
                )
            )

        self.assertEqual(
            self.reply(responses[0]),
            self.reply(responses[1]),
        )

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_name")

    def test_different_messages_are_serialized(self):
        self.post("Hello")

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(
                    self.post,
                    ["First Name", "Second Name"],
                )
            )

        replies = [
            self.reply(response)
            for response in responses
        ]

        self.assertEqual(
            sum(
                "What is your email" in reply
                for reply in replies
            ),
            1,
        )

        self.assertEqual(
            sum(
                "valid email" in reply
                for reply in replies
            ),
            1,
        )

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_email")

    def test_failure_rolls_back_contact_and_session(self):
        self.post("Hello")
        self.post("Test Person")

        sid = "SM" + uuid.uuid4().hex
        original = registration.complete_registration

        def fail_after_completion(*args, **kwargs):
            original(*args, **kwargs)

            raise RuntimeError(
                "Simulated failure before recording the reply"
            )

        with patch.object(
            registration,
            "complete_registration",
            fail_after_completion,
        ):
            response = self.post(
                "person@example.com",
                sid,
            )

            self.assertEqual(response.status_code, 503)

        self.assertIsNone(
            contacts.get_contact_by_phone(self.phone)
        )

        session = contacts.get_registration_session(self.phone)

        self.assertEqual(session["stage"], "awaiting_email")

        rows = self.sql(
            """
            SELECT registration_processed_at
            FROM twilio_messages
            WHERE message_sid = %s
            """,
            (sid,),
            fetch=True,
        )

        self.assertIsNone(
            rows[0]["registration_processed_at"]
        )

        self.assertIn(
            "registered!",
            self.reply(
                self.post("person@example.com", sid)
            ),
        )

    def test_control_messages(self):
        self.post("Hello")

        for word in (
            "HELP",
            "START",
            "YES",
            "INFO",
            "UNSTOP",
        ):
            self.assertEqual(
                self.reply(self.post(word)),
                "",
            )

            session = contacts.get_registration_session(
                self.phone
            )

            self.assertEqual(
                session["stage"],
                "awaiting_name",
            )

        self.assertEqual(
            self.reply(self.post("STOP")),
            "",
        )

        self.assertIsNone(
            contacts.get_registration_session(self.phone)
        )

    def test_custom_opt_out(self):
        self.post("Hello")

        self.assertEqual(
            self.reply(
                self.post("ARRET", OptOutType="STOP")
            ),
            "",
        )

        self.assertIsNone(
            contacts.get_registration_session(self.phone)
        )

    def test_bad_signature(self):
        response = self.post(
            "Hello",
            signature=False,
        )

        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.sql(
                "SELECT id FROM twilio_messages",
                fetch=True,
            ),
            [],
        )

    def test_other_number_and_account(self):
        self.assertEqual(
            self.reply(
                self.post("Hello", To="+12025550199")
            ),
            "",
        )

        with patch.dict(
            os.environ,
            {"REGISTRATION_TWILIO_ACCOUNT_ID": "999999"},
        ):
            self.assertEqual(
                self.reply(self.post("Hello")),
                "",
            )

        self.assertIsNone(
            contacts.get_registration_session(self.phone)
        )

    def test_whatsapp_unchanged(self):
        response = self.post(
            "Hello",
            From="whatsapp:" + self.phone,
            To="whatsapp:" + self.number,
        )

        self.assertEqual(response.status_code, 204)

        self.assertIsNone(
            contacts.get_registration_session(self.phone)
        )

    def test_invalid_phone_is_not_registered(self):
        self.assertEqual(
            self.reply(
                self.post("Hello", From="unknown")
            ),
            "",
        )

        self.assertEqual(
            self.sql(
                "SELECT phone FROM registration_sessions",
                fetch=True,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()