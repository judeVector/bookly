import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600

# Create async Redis connection
token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,  # Add this to handle string responses
)


async def add_jti_to_blocklist(jti: str) -> None:
    """Add a JWT token ID to the blocklist."""
    await token_blocklist.set(name=jti, value="blocked", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    """Check if a JWT token ID is in the blocklist."""
    result = await token_blocklist.get(jti)
    return result is not None
