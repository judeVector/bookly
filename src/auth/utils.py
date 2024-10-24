import uuid
import logging
from loguru import logger

from datetime import timedelta, datetime
from passlib.context import CryptContext
from src.config import Config
import jwt
from fastapi import HTTPException, status

ACCESS_TOKEN_EXPIRY = 3600

password_context = CryptContext(schemes=["bcrypt"])


# Password Hashing and Verifying Functions
def generate_password_hash(password: str) -> str:

    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:

    result = password_context.verify(password, hash)
    return result


# JWT Token creation and Decoding Functions
def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:

    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM
        )
        return token_data
    except jwt.DecodeError:
        logger.error("Invalid token or token expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token or token expired",
        )
    except jwt.PyJWTError as e:
        logger.exception("JWT error occurred: %s", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token decoding failed",
        )
