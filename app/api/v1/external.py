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

@router.get("/profile")
def get_user_profile(current_user = Depends(get_current_api_user)):
    """
    Get current user profile.
    
    Returns the profile information for the authenticated API user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }

@router.get("/tenant")
def get_tenant_info(current_user = Depends(get_current_api_user), db: Session = Depends(get_db)):
    """
    Get tenant information.
    
    Returns information about the tenant associated with the current user.
    """
    from app.crud.tenant import get_tenant
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tenant associated with this user"
        )
    
    tenant = get_tenant(db, tenant_id=current_user.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "domain": tenant.domain,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None
    }

@router.post("/echo")
def echo_message(message: dict, current_user = Depends(get_current_api_user)):
    """
    Echo endpoint for testing.
    
    Returns the message sent by the API user with additional metadata.
    """
    return {
        "message": message,
        "user_id": current_user.id,
        "tenant_id": current_user.tenant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "echo": True
    }

@router.get("/ping")
def ping(current_user = Depends(get_current_api_user)):
    """
    Simple ping endpoint.
    
    Returns a simple pong response to verify connectivity.
    """
    return {
        "pong": True,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": current_user.id
    } 