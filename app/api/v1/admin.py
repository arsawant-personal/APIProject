from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import verify_token, create_access_token
from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import tenant as tenant_crud
from app.crud import user as user_crud
from app.api.deps import get_current_super_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# Tenant Management
@router.post("/tenants/", response_model=Tenant)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    return tenant_crud.create_tenant(db=db, tenant=tenant)

@router.get("/tenants/", response_model=List[Tenant])
def get_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    return tenant_crud.get_tenants(db=db, skip=skip, limit=limit)

@router.get("/tenants/{tenant_id}", response_model=Tenant)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    tenant = tenant_crud.get_tenant(db=db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/tenants/{tenant_id}", response_model=Tenant)
def update_tenant(
    tenant_id: int,
    tenant: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    updated_tenant = tenant_crud.update_tenant(db=db, tenant_id=tenant_id, tenant=tenant)
    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return updated_tenant

# User Management
@router.post("/users/", response_model=User)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    return user_crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    return user_crud.get_users(db=db, skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    user = user_crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Token Generation for API Users
@router.post("/users/{user_id}/generate-token")
def generate_user_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Generate a bearer token for an API user"""
    user = user_crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role not in ["api_user", "tenant_admin", "super_admin"]:
        raise HTTPException(
            status_code=400, 
            detail="Only API users, tenant admins, and super admins can have tokens generated"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "access_token": access_token,
        "token_type": "bearer"
    } 