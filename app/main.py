from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
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
    """Comprehensive external API documentation"""
    return {
        "message": "External API Documentation",
        "description": "APIs available for authenticated API users and tenants",
        "base_url": "http://localhost:8000/api/v1/external",
        "authentication": "Bearer token required",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint for API users",
                "response": {
                    "status": "healthy",
                    "timestamp": "2025-08-02T23:38:39.362006",
                    "user_id": 12,
                    "tenant_id": 16,
                    "message": "Service is running normally"
                }
            },
            "status": {
                "method": "GET", 
                "path": "/status",
                "description": "Service status and user context",
                "response": {
                    "service": "SaaS API",
                    "version": "1.0.0",
                    "status": "operational",
                    "timestamp": "2025-08-02T23:38:39.362006",
                    "user": {
                        "id": 12,
                        "email": "user@example.com",
                        "tenant_id": 16
                    }
                }
            },
            "profile": {
                "method": "GET",
                "path": "/profile", 
                "description": "Get current user profile information",
                "response": {
                    "id": 12,
                    "email": "user@example.com",
                    "full_name": "Demo API User",
                    "role": "API_USER",
                    "tenant_id": 16,
                    "is_active": True,
                    "created_at": "2025-08-02T23:38:39.362006",
                    "updated_at": "2025-08-02T23:38:39.362006"
                }
            },
            "tenant": {
                "method": "GET",
                "path": "/tenant",
                "description": "Get tenant information for current user",
                "response": {
                    "id": 16,
                    "name": "Demo Company",
                    "domain": "demo.example.com",
                    "is_active": True,
                    "created_at": "2025-08-02T23:38:39.362006",
                    "updated_at": "2025-08-02T23:38:39.362006"
                }
            },
            "ping": {
                "method": "GET",
                "path": "/ping",
                "description": "Simple connectivity test",
                "response": {
                    "pong": True,
                    "timestamp": "2025-08-02T23:38:39.362006",
                    "user_id": 12
                }
            },
            "echo": {
                "method": "POST",
                "path": "/echo",
                "description": "Test endpoint that echoes back data",
                "request_body": {
                    "test": "message",
                    "number": 42,
                    "boolean": True
                },
                "response": {
                    "message": {"test": "message", "number": 42, "boolean": True},
                    "user_id": 12,
                    "tenant_id": 16,
                    "timestamp": "2025-08-02T23:38:39.362006",
                    "echo": True
                }
            }
        },
        "access_control": {
            "API_USER": "Can access all external endpoints",
            "TENANT_ADMIN": "Can access all external endpoints", 
            "SUPER_ADMIN": "Can access all external endpoints",
            "USER": "Cannot access external endpoints"
        },
        "swagger_ui": "/docs",
        "openapi_spec": "/api/v1/openapi.json"
    } 