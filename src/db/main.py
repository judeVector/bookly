from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger

from src.config import Config

# Create the async engine
async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        # echo=True,  # Uncomment for SQLAlchemy engine logs
    )
)

SessionFactory = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initialize the PostgreSQL Database connection.
    """
    logger.info("Initializing PostgreSQL connection pool...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("PostgreSQL connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL connection pool: {e}")
        raise


async def get_session() -> AsyncSession:  # type: ignore
    """
    Get a new database session.
    This function yields a session and ensures proper cleanup.
    """
    async with SessionFactory() as session:
        yield session


async def close_db() -> None:
    """
    Close the PostgreSQL connection pool.
    """
    logger.info("Closing PostgreSQL connection pool...")
    await async_engine.dispose()
