import logging
import os
import time
import uuid

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.main import app
from api.diagnostics import router as diagnostics_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("insurance_ai_copilot")

app.include_router(diagnostics_router)

raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
allowed_origins = [x.strip() for x in raw_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

class ApiKeyMiddleware(BaseHTTPMiddleware):
    OPEN_PATHS = {
        "/", "/health", "/ready", "/version",
        "/docs", "/redoc", "/openapi.json",
    }

    async def dispatch(self, request, call_next):
        if os.getenv("APP_ENV", "development").lower() != "production":
            return await call_next(request)

        path = request.url.path
        if path in self.OPEN_PATHS or path.startswith("/docs"):
            return await call_next(request)

        expected_key = os.getenv("APP_API_KEY", "").strip()
        if not expected_key:
            return JSONResponse(
                status_code=503,
                content={"detail": "APP_API_KEY is not configured for production."},
            )

        supplied_key = request.headers.get("X-API-Key", "")
        if supplied_key != expected_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key."},
            )

        return await call_next(request)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(ApiKeyMiddleware)
