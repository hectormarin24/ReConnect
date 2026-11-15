import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

encryption_key = os.getenv("TWILIO_ENCRYPTION_KEY")

if not encryption_key:
    raise RuntimeError(
        "TWILIO_ENCRYPTION_KEY is missing from the environment."
    )

cipher = Fernet(encryption_key.encode("ascii"))

def encrypt_secret(value: str) -> str:
    encrypted = cipher.encrypt(value.encode("utf-8"))
    return encrypted.decode("ascii")


def decrypt_secret(encrypted_value: str) -> str:
    decrypted = cipher.decrypt(encrypted_value.encode("ascii"))
    return decrypted.decode("utf-8")