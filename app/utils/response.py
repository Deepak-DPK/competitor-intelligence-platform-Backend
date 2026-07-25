"""
app/utils/response.py
---------------------
Standardised JSON response helpers.

All API responses follow the envelope format:
    {
        "success": true,
        "data": <payload>,
        "message": "Optional message",
        "pagination": { ... }   # only on list endpoints
    }

Error responses (handled by FastAPI's exception layer) follow:
    {
        "success": false,
        "detail": "Error description",
        "request_id": "uuid"
    }
"""

from typing import Any, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    pagination: Optional[dict] = None,
) -> dict:
    """Build a standardised success envelope."""
    response: dict = {"success": True, "data": data}
    if message:
        response["message"] = message
    if pagination:
        response["pagination"] = pagination
    return response


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: Optional[str] = None,
) -> dict:
    """Build a standardised paginated success envelope."""
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data=data,
        message=message,
        pagination={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    )
