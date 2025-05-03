import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.config import get_settings
from app.api.v1.endpoints import auth, user, post, moderator, admin
from app.core.database import engine, Base, get_db
from app.core.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    resource_not_found_handler,
    unauthorized_handler,
    bad_request_handler,
    storage_unavailable_handler,
    sqlalchemy_error_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError, HTTPException
from app.core.exceptions import (
    ResourceNotFoundException,
    UnauthorizedException,
    BadRequestException,
    StorageUnavailableException
)
from sqlalchemy.exc import SQLAlchemyError
from app.core.middleware.metrics import MetricsMiddleware
from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Добавляем middleware для метрик
app.add_middleware(MetricsMiddleware)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)
app.add_exception_handler(UnauthorizedException, unauthorized_handler)
app.add_exception_handler(BadRequestException, bad_request_handler)
app.add_exception_handler(StorageUnavailableException, storage_unavailable_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(post.router, prefix=settings.API_V1_STR)
app.include_router(moderator.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Travel Journal API",
        "docs": "/docs"
    } 