from pydantic import BaseModel, ConfigDict, Field, SecretStr
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class TwilioAccountConnectRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    label: str = Field(
        min_length=1,
        max_length=100,
    )

    account_sid: str = Field(
        pattern=r"^AC[0-9a-fA-F]{32}$",
    )

    auth_token: SecretStr = Field(
        min_length=1,
        max_length=128,
    )

class TwilioAccountResponse(BaseModel):
    id: int
    label: str
    account_sid: str
    sms_number: str | None
    whatsapp_number: str | None

class TwilioSmsSenderResponse(BaseModel):
    sid: str
    phone_number: str
    friendly_name: str | None = None

class SmsSendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_number: str = Field(
        pattern=r"^\+[1-9][0-9]{1,14}$",
    )

    to_number: str = Field(
        pattern=r"^\+[1-9][0-9]{1,14}$",
    )

    body: str = Field(
        min_length=1,
        max_length=1600,
    )


class SmsSendResponse(BaseModel):
    sid: str
    status: str
    history_saved: bool

class TwilioMessageResponse(BaseModel):
    id: int
    twilio_account_id: int
    message_sid: str
    channel: str
    direction: str
    from_address: str
    to_address: str
    body: str
    status: str
    error_code: int | None
    is_read: bool
    created_at: datetime
    updated_at: datetime

class UnreadCountResponse(BaseModel):
    unread_count: int