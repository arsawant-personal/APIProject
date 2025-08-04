from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import verify_token, create_access_token
from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import tenant as tenant_crud
from app.crud import user as user_crud
from app.crud import api_call as api_call_crud
from app.schemas.api_call import APICall, APICallFilter, APICallStats, APICallPaginated, APICallPaginatedWithDetails, APICallWithDetails
from app.models.user import UserRole
from app.api.deps import get_current_super_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# Tenant endpoints
@router.post("/tenants/", response_model=Tenant)
def create_tenant(
    tenant: TenantCreate,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new tenant"""
    return tenant_crud.create_tenant(db=db, tenant=tenant)

@router.get("/tenants/", response_model=List[Tenant])
def get_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get all tenants"""
    tenants = tenant_crud.get_tenants(db, skip=skip, limit=limit)
    return tenants

@router.get("/tenants/{tenant_id}", response_model=Tenant)
def get_tenant(
    tenant_id: int,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific tenant"""
    tenant = tenant_crud.get_tenant(db, tenant_id=tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/tenants/{tenant_id}", response_model=Tenant)
def update_tenant(
    tenant_id: int,
    tenant: TenantUpdate,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Update a tenant"""
    db_tenant = tenant_crud.get_tenant(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant_crud.update_tenant(db=db, tenant_id=tenant_id, tenant=tenant)

# User endpoints
@router.post("/users/", response_model=User)
def create_user(
    user: UserCreate,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    return user_crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get all users"""
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Update a user"""
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if trying to update a SUPER_ADMIN user
    if db_user.role == "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Cannot update SUPER_ADMIN users")
    
    updated_user = user_crud.update_user(db=db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if trying to delete a SUPER_ADMIN user
    if db_user.role == "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Cannot delete SUPER_ADMIN users")
    
    deleted_user = user_crud.delete_user(db=db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=400, detail="Failed to delete user")
    return {"message": "User deleted successfully"}

# API Call Tracking endpoints
@router.get("/api-calls/", response_model=APICallPaginatedWithDetails)
def get_api_calls(
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    response_status: Optional[int] = Query(None, description="Filter by response status"),
    limit: int = Query(25, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get API calls with filtering and pagination"""
    filter_params = APICallFilter(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
        endpoint=endpoint,
        method=method,
        response_status=response_status,
        limit=limit,
        offset=offset
    )
    
    # Get the paginated results
    api_calls = api_call_crud.get_api_calls(db, filter_params, offset, limit)
    
    # Get the total count for pagination
    total_count = api_call_crud.get_api_calls_count(db, filter_params)
    
    # Calculate pagination info
    page = (offset // limit) + 1
    pages = (total_count + limit - 1) // limit  # Ceiling division
    
    # Add tenant and user details to each API call
    api_calls_with_details = []
    for call in api_calls:
        call_dict = call.__dict__.copy()
        
        # Get tenant name
        tenant_name = None
        if call.tenant_id:
            from app.crud import tenant as tenant_crud
            tenant = tenant_crud.get_tenant(db, call.tenant_id)
            tenant_name = tenant.name if tenant else f"Tenant {call.tenant_id}"
        
        # Get user email
        user_email = None
        if call.user_id:
            user = user_crud.get_user(db, call.user_id)
            user_email = user.email if user else f"User {call.user_id}"
        
        call_dict["tenant_name"] = tenant_name
        call_dict["user_email"] = user_email
        
        api_calls_with_details.append(APICallWithDetails(**call_dict))
    
    return APICallPaginatedWithDetails(
        items=api_calls_with_details,
        total=total_count,
        page=page,
        size=limit,
        pages=pages
    )

@router.get("/api-calls/stats", response_model=APICallStats)
def get_api_call_stats(
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    response_status: Optional[int] = Query(None, description="Filter by response status"),
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get API call statistics"""
    filter_params = APICallFilter(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
        endpoint=endpoint,
        method=method,
        response_status=response_status
    )
    
    stats = api_call_crud.get_api_call_stats(db, filter_params)
    return stats

@router.get("/api-calls/date-range/{date_range}")
def get_api_calls_by_date_range(
    date_range: str,
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get API calls for common date ranges"""
    api_calls = api_call_crud.get_api_calls_by_date_range(db, tenant_id, date_range)
    return api_calls

@router.delete("/api-calls/cleanup")
def cleanup_old_api_calls(
    days: int = Query(90, description="Delete calls older than this many days"),
    current_user = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Clean up old API calls"""
    deleted_count = api_call_crud.delete_old_api_calls(db, days)
    return {"message": f"Deleted {deleted_count} old API calls"} 