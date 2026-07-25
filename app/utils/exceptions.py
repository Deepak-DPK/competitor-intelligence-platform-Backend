"""
app/utils/exceptions.py
-----------------------
Application-level exception hierarchy.

Raise these from service/repository layers; the global exception handler in
main.py (or dedicated exception handlers registered per-router) will
translate them to the correct HTTP status codes.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base class for all application exceptions."""

    status_code: int = 500
    detail: str = "An unexpected error occurred."

    def __init__(
        self,
        detail: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = extra or {}
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""
    status_code = 404
    detail = "Resource not found."


class UnauthorizedException(AppException):
    """Raised when authentication fails or token is invalid."""
    status_code = 401
    detail = "Authentication required."


class ForbiddenException(AppException):
    """Raised when the user does not have permission."""
    status_code = 403
    detail = "You do not have permission to perform this action."


class ConflictException(AppException):
    """Raised on duplicate / conflicting resource creation."""
    status_code = 409
    detail = "Resource already exists."


class ValidationException(AppException):
    """Raised when business-level validation fails."""
    status_code = 422
    detail = "Validation error."


class ServiceUnavailableException(AppException):
    """Raised when a downstream service (AI, scraper) is unavailable."""
    status_code = 503
    detail = "Service temporarily unavailable."
