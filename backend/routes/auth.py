from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth import authenticate_admin, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(data: LoginRequest):

    if not authenticate_admin(
        data.username,
        data.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(
        data.username
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": data.username,
    }