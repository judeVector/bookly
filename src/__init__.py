from fastapi import FastAPI
from .books.routes import book_router
from contextlib import asynccontextmanager

from src.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Database is starting.....")
    await init_db()
    yield
    print("Database has been stopped")


version = "v1"

app = FastAPI(version=version, title="Bookly API", lifespan=lifespan,
              description="A Simple Book Service for Book Management")

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['Books'])
