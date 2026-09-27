from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import RequestIdMiddleware, SecurityHeadersMiddleware
from app.core.exceptions import PackWiseAPIException
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: logging initialization
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.APP_ENV}]")
    logger.info(f"API Prefix mounted at: {settings.API_PREFIX}")
    logger.info("Milestones M0-M5: Production backend architecture & explainability pipeline active.")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Based Intelligent Food Packaging Material Recommendation System (SIH 2026 Production Baseline)",
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)

# 1. Mount Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Mount Request ID Middleware (Audit Traceability & Latency Logging)
app.add_middleware(RequestIdMiddleware)

# 3. Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount API v1 router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": f"{settings.API_PREFIX}/docs",
        "health": f"{settings.API_PREFIX}/health",
        "readiness": f"{settings.API_PREFIX}/readiness"
    }


# -----------------------------------------------------------------------------
# Structured Production Error Handlers (Section 5)
# -----------------------------------------------------------------------------

@app.exception_handler(PackWiseAPIException)
async def packwise_exception_handler(request: Request, exc: PackWiseAPIException):
    req_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.error_message,
                "details": exc.details
            },
            "request_id": req_id
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    formatted_errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        formatted_errors.append({"field": field, "message": msg, "type": err.get("type")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The submitted payload failed input schema validation.",
                "details": {"validation_errors": formatted_errors}
            },
            "request_id": req_id
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    detail_content = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": detail_content.get("message", str(exc.detail)),
                "details": detail_content
            },
            "request_id": req_id
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    # Log internal stack trace to server logs only; never expose to client
    logger.error(f"[{req_id}] Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request. Please reference request_id.",
                "details": {}
            },
            "request_id": req_id
        }
    )
