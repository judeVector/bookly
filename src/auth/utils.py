import uuid
from typing import Optional, Dict, Any
from loguru import logger
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from src.config import Config
import jwt
from fastapi import HTTPException, status


# Constants
ACCESS_TOKEN_EXPIRY = 3600  # Default token expiry time in seconds (1 hour)
MIN_PASSWORD_LENGTH = 8  # Minimum required password length

# Initialize password hashing context with bcrypt scheme
password_context = CryptContext(schemes=["bcrypt"])


def generate_password_hash(password: str) -> str:
    """
    Generate a secure hash of the provided password using bcrypt.

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The hashed password

    Raises:
        ValueError: If password doesn't meet minimum requirements
    """
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )

    try:
        hash = password_context.hash(password)
        return hash
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Failed to hash password") from e


def verify_password(password: str, hash: str) -> bool:
    """
    Verify if a plain text password matches its hashed version.

    Args:
        password (str): The plain text password to verify
        hash (str): The hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    if not password or not hash:
        return False

    try:
        return password_context.verify(password, hash)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def create_access_token(
    user_data: Dict[str, Any], expiry: Optional[timedelta] = None, refresh: bool = False
) -> str:
    """
    Create a JWT access token containing user data and claims.

    Args:
        user_data (Dict[str, Any]): Dictionary containing user information to encode in token
        expiry (Optional[timedelta]): Custom token expiration time. Defaults to ACCESS_TOKEN_EXPIRY
        refresh (bool): Whether this is a refresh token. Defaults to False

    Returns:
        str: Encoded JWT token

    Raises:
        ValueError: If user_data is empty or invalid
    """
    if not user_data:
        raise ValueError("User data cannot be empty")

    try:
        # Create a copy of user_data to avoid modifying the original
        payload = {"user": user_data.copy()}

        # Use UTC time for token expiration
        expiration_delta = (
            expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
        )
        payload["exp"] = datetime.now(timezone.utc) + expiration_delta
        payload["iat"] = datetime.now(timezone.utc)
        payload["jti"] = str(uuid.uuid4())
        payload["refresh"] = refresh

        token = jwt.encode(
            payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
        )

        return token

    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise ValueError("Failed to create access token") from e


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token (str): The JWT token to decode and validate

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        HTTPException: With status code 403 if token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token is required"
        )

    try:
        # Add leeway of 1 second for clock skew
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            leeway=1,
        )
        return token_data

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
        )

    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )

    except Exception as e:
        logger.exception(f"Unexpected error decoding token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token decoding failed"
        )
