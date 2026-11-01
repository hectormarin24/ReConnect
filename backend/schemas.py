from pydantic import BaseModel, ConfigDict, Field, SecretStr


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