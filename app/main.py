from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import time
from app.core.config import settings
from app.core.logging import setup_logging, logger, log_api_request, log_api_response
from app.core.tracking import api_tracker
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
    
    # Track API call for billing
    try:
        from app.core.database import get_db
        
        # Get database session
        db = next(get_db())
        
        # Try to get current user (optional)
        current_user = None
        try:
            # Extract user from token if present
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                
                # First try JWT token
                from app.core.security import verify_token
                from app.crud import user as user_crud
                payload = verify_token(token)
                if payload:
                    user_email = payload.get("sub")
                    if user_email:
                        current_user = user_crud.get_user_by_email(db, user_email)
                
                # If JWT token failed, try API token
                if not current_user:
                    from app.crud import token as token_crud
                    api_token = token_crud.verify_token(db, token)
                    if api_token:
                        print(f"🔑 Found API token for tenant: {api_token.tenant_id}")
                        # Create mock user for API token
                        from app.models.user import User, UserRole
                        current_user = User(
                            id=None,  # Use None instead of 0 to avoid foreign key constraint
                            email="api-token@system",
                            full_name="API Token User",
                            role=UserRole.API_USER,
                            tenant_id=api_token.tenant_id,
                            is_active=True
                        )
                        print(f"👤 Created mock user: {current_user.email}, tenant: {current_user.tenant_id}")
        except Exception as e:
            print(f"Error extracting user from token: {e}")
            pass
        
        # Track the API call
        print(f"🔍 About to track API call: {request.method} {request.url.path}")
        try:
            api_tracker.track_api_call(request, response, response_time, db, current_user)
        except Exception as e:
            print(f"❌ Error in tracking: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        # Don't fail the request if tracking fails
        logger.error(f"Error tracking API call: {e}")
    
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