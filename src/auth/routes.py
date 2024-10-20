from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, decode_token, verify_password

from src.db.main import get_session


auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    user_exists = await user_service.user_exists(user_data.email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email {user_data.email} already exist",
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login", response_model=UserLoginModel)
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} does not exist",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    token_data = {"email": user.email, "user_uid": str(user.uid)}

    access_token = create_access_token(user_data=token_data)
    refresh_token = create_access_token(
        user_data=token_data,
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    return JSONResponse(
        content={
            "message": "Login Successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": str(user.uid),
                "email": user.email,
            },
        }
    )
