"""
app/services/monitoring/scrapers/base.py
----------------------------------------
Base class for all scraper modules.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger


class BaseScraper(ABC):
    """
    Abstract base class for monitoring scrapers.
    Forces all scrapers to implement a `run` method.
    """
    def __init__(self, db: AsyncSession):
        self._db = db
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def run(self, competitor_id: UUID, url: str) -> Any:
        """
        Execute the scraper.
        Must be implemented by subclasses.
        Returns the created Snapshot object.
        """
        pass
