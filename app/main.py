from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.core.config import settings
from app.core.logging import setup_logging, logger, log_api_request, log_api_response
from app.api.v1.api import api_router

# Initialize logging
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    enable_detailed_logging=settings.ENABLE_DETAILED_LOGGING,
    log_to_file=settings.LOG_TO_FILE,
    log_file_path=settings.LOG_FILE_PATH
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all API requests and responses"""
    start_time = time.time()
    
    # Log request
    log_api_request(request.method, str(request.url.path))
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Log response
    log_api_response(response.status_code, response_time)
    
    return response

@app.get("/")
def read_root():
    return {"message": "Welcome to SaaS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Admin API Documentation
@app.get("/admin/docs", include_in_schema=False)
def admin_docs():
    """Redirect to admin API documentation"""
    return {"message": "Admin API Documentation", "url": "/docs"}

# External API Documentation
@app.get("/external/docs", include_in_schema=False)
def external_docs():
    """Redirect to external API documentation"""
    return {"message": "External API Documentation", "url": "/docs"} 