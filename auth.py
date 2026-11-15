
import re


def validate_login_input(email, password):
    """
    Check login inputs before attempting authentication.

    Returns:
        (True, "") if inputs are valid.
        (False, error_message) otherwise.
    """

    email = email.strip()

    if not email or not password:
        return False, "Please enter your email and password."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    return True, ""



import hashlib
import hmac
import os


def hash_password(password):
    """Create a salted password hash for account storage."""
    salt = os.urandom(16)
    iterations = 600_000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )

    return f"{iterations}${salt.hex()}${password_hash.hex()}"


def verify_password(password, stored_hash):
    """Check a password against its stored hash."""
    try:
        iterations_text, salt_hex, hash_hex = stored_hash.split("$")

        iterations = int(iterations_text)
        if iterations != 600_000:
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        if len(salt) != 16 or len(expected_hash) != 32:
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    except (ValueError, TypeError, AttributeError):
        return False



def authenticate_user(email, password, account):
    """
    Authenticate a user against an account record.

    account should be a dictionary containing:
        email
        password_hash

    Returns (success, message).
    """
    valid, message = validate_login_input(email, password)

    if not valid:
        return False, message

    # The database will provide this account record later.
    if account is None:
        return False, "Incorrect email or password, please try again."

    stored_email = account.get("email", "")
    stored_hash = account.get("password_hash", "")

    if (
        email.strip().casefold() != stored_email.casefold()
        or not verify_password(password, stored_hash)
    ):
        return False, "Incorrect email or password, please try again."

    return True, "Login successful."
