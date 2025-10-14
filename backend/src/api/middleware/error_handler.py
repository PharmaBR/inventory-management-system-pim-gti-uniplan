"""Global error handling middleware."""
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.logging import logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "details": None,
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation error",
            "details": exc.errors(),
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors (unique constraints, foreign keys, etc)."""
    logger.error(
        f"Database integrity error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    # Parse common integrity errors
    error_message = "Database integrity error"
    if "unique constraint" in str(exc).lower():
        error_message = "Duplicate value: this record already exists"
    elif "foreign key constraint" in str(exc).lower():
        error_message = "Referenced record does not exist"
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "code": 409,
            "message": error_message,
            "details": None,
        }
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle general database errors."""
    logger.error(
        f"Database error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Database error occurred",
            "details": None,
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "details": None,
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from fastapi.exceptions import RequestValidationError
    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
