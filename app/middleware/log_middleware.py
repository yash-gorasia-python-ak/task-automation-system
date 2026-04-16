import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.metadata_repository import RequestMetadata
from app.db.session import async_session


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        async with async_session() as db:
            new_record = RequestMetadata(
                request_id=str(uuid.uuid4()),
                method=request.method,
                endpoint=str(request.url),
                status_code=str(response.status_code),
                response_time=f"{process_time:.4f}s",
            )
            db.add(new_record)
            await db.commit()

        return response
