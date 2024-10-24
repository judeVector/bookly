from fastapi.security import HTTPBearer
from fastapi import HTTPException, Request, status

from .utils import decode_token

from src.db.redis import token_in_blocklist


class TokenBearer(HTTPBearer):
    """
    Base token bearer class extending FastAPI's HTTPBearer.
    Provides common token validation and verification functionality.

    Args:
        auto_error (bool): Whether to auto-raise HTTP 403 errors for invalid auth headers.
            Defaults to True.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        """
        Validate and decode the bearer token from the request.

        Args:
            request (Request): FastAPI request object containing the authorization header

        Returns:
            dict: Decoded token data containing user information and claims

        Raises:
            HTTPException:
                - 403 if credentials are missing or invalid
                - 403 if token is invalid or expired
        """
        # Validate bearer token format
        credentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization credentials",
            )

        # Decode and validate token
        token = credentials.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Invalid token or token expired",
                    "resolution": "Please get a new token",
                },
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get a new token",
                },
            )

        # Perform token-specific validation
        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        """
        Abstract method to verify token-specific data.
        Must be implemented by child classes to provide custom token validation.

        Args:
            token_data (dict): Decoded token data to verify

        Raises:
            NotImplementedError: When called directly on base class
        """
        raise NotImplementedError("Please implement this method in child classes")


class AccessTokenBearer(TokenBearer):
    """
    Token bearer for validating access tokens.
    Ensures the token is not a refresh token.
    """

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify that the token is a valid access token.

        Args:
            token_data (dict): Decoded token data to verify

        Raises:
            HTTPException: 403 if token is missing or is a refresh token
        """
        if not token_data or token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid access token.",
            )


class RefreshTokenBearer(TokenBearer):
    """
    Token bearer for validating refresh tokens.
    Ensures the token is specifically a refresh token.
    """

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify that the token is a valid refresh token.

        Args:
            token_data (dict): Decoded token data to verify

        Raises:
            HTTPException: 403 if token is missing or is not a refresh token
        """
        if not token_data or not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid refresh token.",
            )
