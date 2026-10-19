# ReConnect Login Credentials Database

Sprint task: **Create the database for login credentials**.

This submission creates a PostgreSQL database named `reconnect` and one table, `app_user`, for user identity and password-hash storage. The name, email and phone fields correspond to the supplied registration mockup. Java will connect to this database when the application login and registration work is implemented.

## Files

| File | Purpose |
| --- | --- |
| `01_create_database.sql` | Creates the empty `reconnect` database |
| `02_create_users_table.sql` | Creates the user table, constraints and unique email index |
| `README.md` | Setup instructions and field definitions |

## Setup

Requires PostgreSQL 14 or newer and an existing PostgreSQL account with permission to create a database. The scripts contain no database passwords or default user accounts.

From this folder, run:

```sh
psql -U postgres -d postgres -v ON_ERROR_STOP=1 -f 01_create_database.sql
psql -U postgres -d reconnect -v ON_ERROR_STOP=1 -f 02_create_users_table.sql
```

Replace `postgres` after `-U` with your PostgreSQL administrator username if needed. Enter its password when prompted.

In pgAdmin, run the first script while connected to the existing `postgres` database with autocommit enabled. Refresh the database list, open a new Query Tool connected to `reconnect`, and run the second script.

Run these scripts once against a fresh database. If `reconnect` already exists, skip the first script after confirming it is the intended database. If `app_user` already exists, use a separate clean database for this submission instead of replacing the existing table. These scripts do not drop or overwrite existing data.

## User table

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | UUID | Automatically generated primary key |
| `first_name` | VARCHAR(100) | Required first name |
| `last_name` | VARCHAR(100) | Required last name |
| `email` | VARCHAR(254) | Required login email; unique regardless of capitalization |
| `phone_number` | VARCHAR(32) | Optional phone number; use NULL when omitted |
| `password_hash` | VARCHAR(255) | Required encoded Argon2id password hash |
| `created_at` | TIMESTAMPTZ | Automatically recorded account creation time |

Required text fields cannot be blank. Email addresses cannot contain leading or trailing spaces. A unique index prevents addresses such as `Person@example.org` and `person@example.org` from belonging to separate accounts. The application must still validate that the submitted email is a valid email address.

The password field accepts the encoded Argon2id hash format. Hash generation and password verification belong to the future Java application. The encoded hash includes its salt and hashing parameters, so a separate salt column is unnecessary. The database format check does not perform password hashing or prove that a hash was generated correctly. Password confirmation is checked by the application and is not stored.

## Check the result

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'app_user'
ORDER BY ordinal_position;

SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'app_user';
```

This submission covers database creation and credential storage. The Java API, login screens, account approval workflow, sessions, password recovery, and deployment configuration are separate application work and are not included.
