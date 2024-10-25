from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, decode_token, verify_password
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    Rolechecker,
)

from src.db.postgres import get_session
from src.db.redis import add_jti_to_blocklist


auth_router = APIRouter()
user_service = UserService()
role_checker = Rolechecker(["admin"])

# Number of days for which refresh token remains valid
REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    """
    Create a new user account endpoint.

    Args:
        user_data (UserCreateModel): User registration data including email and password
        session (AsyncSession): Database session for user creation

    Returns:
        UserModel: Created user details

    Raises:
        HTTPException: 403 if user with email already exists
    """
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
    """
    User login endpoint that authenticates credentials and returns access/refresh tokens.

    Args:
        login_data (UserLoginModel): User login credentials (email and password)
        session (AsyncSession): Database session for user lookup

    Returns:
        JSONResponse: Contains:
            - Success message
            - Access token
            - Refresh token
            - User details (uid and email)

    Raises:
        HTTPException:
            - 404 if user not found
            - 401 if password is incorrect
    """
    email = login_data.email
    password = login_data.password

    # Verify user exists
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} does not exist",
        )

    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Generate tokens
    token_data = {"email": user.email, "user_uid": str(user.uid), "role": user.role}
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


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Endpoint to get a new access token using a valid refresh token.

    Args:
        token_details (dict): Decoded refresh token data from RefreshTokenBearer dependency
            Contains token expiration and user information

    Returns:
        JSONResponse: Contains new access token

    Raises:
        HTTPException: 400 if refresh token is invalid or expired
    """
    expiry_timestamp = token_details["exp"]

    # Check if refresh token is still valid
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get("/me")
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):

    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )
