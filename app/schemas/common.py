"""
app/schemas/common.py
---------------------
Shared schemas for standard API responses (e.g. pagination).
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper for collections."""
    
    items: List[T] = Field(description="The list of items for the current page")
    total: int = Field(description="Total number of items matching the query")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items requested per page")
    
    model_config = ConfigDict(from_attributes=True)
