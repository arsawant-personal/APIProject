from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

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