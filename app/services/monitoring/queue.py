"""
app/services/monitoring/queue.py
--------------------------------
In-memory monitoring queue using asyncio.
For Phase 5, this allows running background scraping jobs inside the FastAPI process.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class ScrapeJob:
    """Represents a single scraping task."""
    competitor_id: UUID
    module_type: str  # "website", "pricing", "keyword", "social", "advertising"
    url: Optional[str] = None
    retry_count: int = 0


class MonitoringQueue:
    """Singleton queue for background scraping jobs."""
    def __init__(self):
        # We use asyncio.Queue, but it must be initialized within the running event loop.
        self._queue: Optional[asyncio.Queue[ScrapeJob]] = None

    def _ensure_queue(self):
        if self._queue is None:
            self._queue = asyncio.Queue()

    async def enqueue(self, job: ScrapeJob) -> None:
        self._ensure_queue()
        await self._queue.put(job)

    async def dequeue(self) -> ScrapeJob:
        self._ensure_queue()
        return await self._queue.get()

    def task_done(self):
        self._ensure_queue()
        self._queue.task_done()


# Global singleton queue instance
monitoring_queue = MonitoringQueue()
