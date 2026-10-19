-- ReConnect: Login Credentials Database
-- Connect to the reconnect database before running this script.
-- PostgreSQL 14 or newer. No extensions or Java application are required.

BEGIN;

CREATE TABLE public.app_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    first_name VARCHAR(100) NOT NULL
        CONSTRAINT app_user_first_name_required
        CHECK (length(btrim(first_name)) > 0),

    last_name VARCHAR(100) NOT NULL
        CONSTRAINT app_user_last_name_required
        CHECK (length(btrim(last_name)) > 0),

    email VARCHAR(254) NOT NULL
        CONSTRAINT app_user_email_required
        CHECK (length(email) > 0 AND email = btrim(email)),

    phone_number VARCHAR(32),

    -- Store the complete encoded Argon2id hash, including its salt and settings.
    -- The future Java registration code must generate this value.
    password_hash VARCHAR(255) NOT NULL
        CONSTRAINT app_user_password_hash_format
        CHECK (
            password_hash ~ '^\$argon2id\$v=19\$m=[1-9][0-9]*,t=[1-9][0-9]*,p=[1-9][0-9]*\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+$'
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A different capitalization cannot create a second account with the same email.
CREATE UNIQUE INDEX app_user_email_unique
    ON public.app_user (lower(email));

COMMENT ON TABLE public.app_user IS
    'ReConnect user identity and login credential storage.';
COMMENT ON COLUMN public.app_user.password_hash IS
    'Encoded Argon2id password hash. Never store a plaintext password here.';
COMMENT ON COLUMN public.app_user.email IS
    'Login email address; uniqueness is case-insensitive.';

COMMIT;
