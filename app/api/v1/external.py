from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import UserRole
from app.schemas.health import HealthResponse
from datetime import datetime

router = APIRouter(prefix="/external", tags=["external"])

def get_current_api_user(current_user = Depends(get_current_user)):
    """Ensure the current user is an API user"""
    if current_user.role not in [UserRole.API_USER, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. API users only."
        )
    return current_user

@router.get("/health", response_model=HealthResponse)
def health_check(current_user = Depends(get_current_api_user)):
    """
    Health check endpoint for API users.
    
    This endpoint allows API users to verify their authentication
    and check the status of the service.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        message="Service is running normally"
    )

@router.get("/status")
def service_status(current_user = Depends(get_current_api_user)):
    """
    Service status endpoint.
    
    Returns basic service information for API users.
    """
    return {
        "service": "SaaS API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "tenant_id": current_user.tenant_id
        }
    } 