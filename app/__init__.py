from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.main import init_db
from app.auth.routes import auth_router
from app.books.routes import book_router
from app.reviews.routes import review_router
from app.errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is running...")
    await init_db()
    yield
    print("Server is shutting down")

version = "v1"

app = FastAPI(
    title="Bookly API",
    description="A simple API for managing books",
    version=version,
)


register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router,prefix=f"/api/{version}/auth", tags=["auth"] )
app.include_router(review_router,prefix=f"/api/{version}/reviews", tags=["reviews"])
