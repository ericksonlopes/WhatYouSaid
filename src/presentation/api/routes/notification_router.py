from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from src.config.logger import Logger

logger = Logger()
router = APIRouter()


@router.get("/rest/notifications/sse")
async def sse_notifications():
    """
    Server-Sent Events endpoint for real-time notifications.
    (Placeholder for decommissioned WebSocket)
    """

    async def event_generator():
        try:
            while True:
                # Keep-alive comment
                yield ": keep-alive\n\n"
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("SSE connection closed by client")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
