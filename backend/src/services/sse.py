"""
SSE (Server-Sent Events) manager.

A single in-memory pub/sub hub per station. Liquidsoap fires a webhook
to POST /api/v1/stations/{id}/now-playing; the FastAPI handler calls
sse_manager.publish(), which pushes the event to every connected browser.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

logger = logging.getLogger(__name__)


class SSEManager:
    def __init__(self) -> None:
        # station_id (str) -> set of active asyncio.Queue instances
        self._subscribers: dict[str, set[asyncio.Queue[str]]] = {}
        # Last known now-playing per station (so new subscribers get state immediately)
        self._last_event: dict[str, str] = {}

    def _station_key(self, station_id: Any) -> str:
        return str(station_id)

    async def subscribe(self, station_id: Any) -> asyncio.Queue[str]:
        key = self._station_key(station_id)
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=20)
        self._subscribers.setdefault(key, set()).add(queue)
        logger.debug("SSE subscribe station=%s total=%d", key, len(self._subscribers[key]))
        return queue

    async def unsubscribe(self, station_id: Any, queue: asyncio.Queue[str]) -> None:
        key = self._station_key(station_id)
        subscribers = self._subscribers.get(key)
        if subscribers:
            subscribers.discard(queue)

    async def publish(self, station_id: Any, event_type: str, data: dict) -> None:
        key = self._station_key(station_id)
        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        self._last_event[key] = payload
        for queue in list(self._subscribers.get(key, set())):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning("SSE queue full for station=%s, dropping event", key)

    def get_last_event(self, station_id: Any) -> str | None:
        return self._last_event.get(self._station_key(station_id))

    async def stream(
        self, station_id: Any, queue: asyncio.Queue[str]
    ) -> AsyncGenerator[str, None]:
        """Async generator that yields SSE-formatted strings."""
        try:
            # Immediately send the last known state (if any)
            last = self.get_last_event(station_id)
            if last:
                yield last
            else:
                yield "event: connected\ndata: {}\n\n"

            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=25)
                    yield payload
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep the connection alive
                    yield ": heartbeat\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await self.unsubscribe(station_id, queue)


# Application-wide singleton
sse_manager = SSEManager()
