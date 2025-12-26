from fastapi import APIRouter, HTTPException
import traceback
from auth.auth_service import (
    register_user,
    verify_registration_otp,
    login_user,
    logout_user,
    send_login_otp,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: dict):
    """
    Register user and send OTP
    """
    try:
        register_user(
            phone=payload.get("phone"),
            password=payload.get("password"),
            first_name=payload.get("first_name") or payload.get("firstName"),
            middle_name=payload.get("middle_name") or payload.get("middleName"),
            last_name=payload.get("last_name") or payload.get("lastName"),
            dob=payload.get("dob"),
        )
        return {"message": "OTP sent to phone"}
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp")
def verify_otp(payload: dict):
    """
    Verify OTP and log user in
    """
    try:
        token = verify_registration_otp(
            phone=payload.get("phone"),
            otp_code=payload.get("otp") or payload.get("otp_code"),
        )
        return {"token": token}
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-login-otp")
def send_login_otp_route(payload: dict):
    """
    Send OTP for login
    """
    try:
        send_login_otp(payload["phone"])
        return {"message": "OTP sent"}
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(payload: dict):
    """
    Login existing user
    """
    try:
        result = login_user(
            phone=payload.get("phone"),
            password=payload.get("password"),
            otp=payload.get("otp"),
        )
        return result
    except ValueError as e:
        traceback.print_exc()
        # If OTP required, we return 400 so frontend knows to show OTP field
        # But if invalid credentials, we usually return 401
        # The service raises 'Invalid credentials' or 'OTP verification required'
        # We can distinguish messages or just return 400 for everything except auth failure?
        # Standard: 401 for auth failure.
        if str(e) == "Invalid credentials":
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
def logout(payload: dict):
    """
    Logout user
    """
    logout_user(payload["token"])
    return {"message": "Logged out successfully"}
