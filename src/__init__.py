from fastapi import FastAPI
from contextlib import asynccontextmanager

from .books.routes import book_router
from .auth.routes import auth_router

from src.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting.....")
    await init_db()
    yield
    print("Server has been stopped")


version = "v1"

app = FastAPI(
    version=version,
    title="Bookly API",
    lifespan=lifespan,
    description="A Simple Book Service for Book Management",
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
