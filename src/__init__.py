from fastapi import FastAPI
from contextlib import asynccontextmanager

from .books.routes import book_router
from .auth.routes import auth_router
from .reviews.routes import review_router

from src.db.postgres import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


version = "v1"

app = FastAPI(
    version=version,
    title="Bookly API",
    lifespan=lifespan,
    description="**Bookly** is a book management application built with FastAPI (Python). It offers core CRUD functionalities for managing a book catalog, along with user authentication features. This project provides a fast, secure, and scalable way to handle book data and user accounts, making it a great example of modern web application development with Python",
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["Reviews"])
