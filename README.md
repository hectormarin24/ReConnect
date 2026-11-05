# ReConnect
Tarbiya Institute

## SMS contact registration

Registration is enabled for one designated Twilio account and number.

Required environment settings:

- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- TWILIO_ENCRYPTION_KEY
- TWILIO_WEBHOOK_BASE_URL
- REGISTRATION_TWILIO_ACCOUNT_ID
- REGISTRATION_PHONE_NUMBER

REGISTRATION_TWILIO_ACCOUNT_ID is the numeric local twilio_accounts.id,
not the Twilio Account SID.

Preserve TWILIO_ENCRYPTION_KEY after storing Twilio credentials.

For a new local database, run these SQL files in order:

1. database/database.sql
2. database/registration_sessions.sql
3. database/registration_runtime.sql

Install dependencies:

python -m pip install -r requirements.txt

Run the backend:

python -m uvicorn backend.main:app --reload

Run integration tests:

RUN_MYSQL_TESTS=1 python -m unittest discover -s tests -v

The tests create and delete a temporary database. The configured MySQL
user needs permission to create and drop databases.

Incoming webhook:

POST /webhooks/twilio/incoming

Registration changes and the saved reply are committed together.
Repeated processing of a message SID reuses the stored reply.
Messages from one sender are processed one at a time; carrier delivery
order is not guaranteed.

Twilio manages SMS opt-in/out/help responses. Application control-word
handling must match the sender's Twilio configuration.
Never commit .env.
Never commit .env.
