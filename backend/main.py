from fastapi import FastAPI, HTTPException

from .auth import authenticate_user, create_user
from .schemas import LoginRequest, RegisterRequest

app = FastAPI(title="ReConnect Backend")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/register")
def register(request: RegisterRequest):
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters.",
        )

    created = create_user(
        request.full_name,
        request.email,
        request.password,
    )

    if not created:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    return {
        "success": True,
        "message": "Account created successfully.",
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = authenticate_user(
        request.email,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return {
        "success": True,
        "user": user,
    }