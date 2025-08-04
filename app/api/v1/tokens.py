from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_super_admin, get_current_user
from app.models.user import UserRole
from app.crud import token as token_crud, user as user_crud, tenant as tenant_crud
from app.schemas.token import TokenCreate, TokenUpdate, TokenResponse, TokenWithDetails, TokenCreateResponse, TokenPaginated
import json

router = APIRouter(prefix="/tokens", tags=["tokens"])

@router.post("/", response_model=TokenCreateResponse)
def create_token(
    token_data: TokenCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Create a new API token"""
    # Verify tenant exists
    tenant = tenant_crud.get_tenant(db, tenant_id=token_data.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Verify user exists and belongs to the tenant (if provided)
    if token_data.user_id:
        user = user_crud.get_user(db, user_id=token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.tenant_id != token_data.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not belong to the specified tenant"
            )
    
    # Create the token
    db_token = token_crud.create_token(db, token_data)
    
    return TokenCreateResponse(
        token=db_token.plain_token,
        token_details=TokenResponse(
            id=db_token.id,
            name=db_token.name,
            token_hash=db_token.token_hash,
            scopes=json.loads(db_token.scopes),
            is_active=db_token.is_active,
            expires_at=db_token.expires_at,
            tenant_id=db_token.tenant_id,
            user_id=db_token.user_id,
            created_at=db_token.created_at,
            updated_at=db_token.updated_at
        ),
        message="Token created successfully. Please copy the token now as it won't be shown again."
    )

@router.get("/", response_model=TokenPaginated)
def get_tokens(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    tenant_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Get all tokens with pagination and optional filtering"""
    skip = (page - 1) * size
    
    # Get total count
    total_tokens = token_crud.get_tokens_count(db, tenant_id=tenant_id, user_id=user_id)
    
    # Get tokens for current page
    if tenant_id:
        tokens = token_crud.get_tokens_by_tenant(db, tenant_id=tenant_id, skip=skip, limit=size)
    elif user_id:
        tokens = token_crud.get_tokens_by_user(db, user_id=user_id, skip=skip, limit=size)
    else:
        tokens = token_crud.get_all_tokens(db, skip=skip, limit=size)
    
    result = []
    for token in tokens:
        details = token_crud.get_token_with_details(db, token.id)
        if details:
            result.append(TokenWithDetails(
                id=token.id,
                name=token.name,
                token_hash=token.token_hash,
                scopes=json.loads(token.scopes),
                is_active=token.is_active,
                expires_at=token.expires_at,
                tenant_id=token.tenant_id,
                user_id=token.user_id,
                created_at=token.created_at,
                updated_at=token.updated_at,
                tenant_name=details["tenant_name"],
                user_email=details["user_email"],
                user_full_name=details["user_full_name"]
            ))
    
    total_pages = (total_tokens + size - 1) // size
    
    return TokenPaginated(
        items=result,
        total=total_tokens,
        page=page,
        size=size,
        pages=total_pages
    )

@router.get("/{token_id}", response_model=TokenWithDetails)
def get_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Get a specific token by ID"""
    details = token_crud.get_token_with_details(db, token_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    token = details["token"]
    return TokenWithDetails(
        id=token.id,
        name=token.name,
        token_hash=token.token_hash,
        scopes=json.loads(token.scopes),
        is_active=token.is_active,
        expires_at=token.expires_at,
        tenant_id=token.tenant_id,
        user_id=token.user_id,
        created_at=token.created_at,
        updated_at=token.updated_at,
        tenant_name=details["tenant_name"],
        user_email=details["user_email"],
        user_full_name=details["user_full_name"]
    )

@router.put("/{token_id}", response_model=TokenResponse)
def update_token(
    token_id: int,
    token_update: TokenUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Update a token (only scopes and status can be updated)"""
    db_token = token_crud.update_token(db, token_id, token_update)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return TokenResponse(
        id=db_token.id,
        name=db_token.name,
        token_hash=db_token.token_hash,
        scopes=json.loads(db_token.scopes),
        is_active=db_token.is_active,
        expires_at=db_token.expires_at,
        tenant_id=db_token.tenant_id,
        user_id=db_token.user_id,
        created_at=db_token.created_at,
        updated_at=db_token.updated_at
    )

@router.delete("/{token_id}")
def delete_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Delete a token"""
    success = token_crud.delete_token(db, token_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return {"message": "Token deleted successfully"}

@router.get("/stats/summary")
def get_token_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_super_admin)
):
    """Get token statistics"""
    from datetime import datetime
    
    all_tokens = token_crud.get_all_tokens(db, skip=0, limit=10000)
    
    total_tokens = len(all_tokens)
    active_tokens = len([t for t in all_tokens if t.is_active])
    expired_tokens = len([t for t in all_tokens if t.expires_at and t.expires_at < datetime.utcnow()])
    
    # Count unique tenants with tokens
    tenant_ids = set(t.tenant_id for t in all_tokens)
    tenants_with_tokens = len(tenant_ids)
    
    return {
        "total_tokens": total_tokens,
        "active_tokens": active_tokens,
        "expired_tokens": expired_tokens,
        "tenants_with_tokens": tenants_with_tokens
    } 