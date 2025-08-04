from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.token import Token
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.token import TokenCreate, TokenUpdate
from app.core.security import get_password_hash, verify_password
import secrets
import json
from typing import List, Optional
from datetime import datetime

def create_token(db: Session, token_data: TokenCreate) -> Token:
    """Create a new token"""
    # Generate a secure random token
    token_value = secrets.token_urlsafe(32)
    token_hash = get_password_hash(token_value)
    
    # Convert scopes list to JSON string
    scopes_json = json.dumps(token_data.scopes)
    
    db_token = Token(
        name=token_data.name,
        token_hash=token_hash,
        scopes=scopes_json,
        is_active=token_data.is_active,
        expires_at=token_data.expires_at,
        tenant_id=token_data.tenant_id,
        user_id=token_data.user_id
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    # Store the plain token temporarily for response
    db_token.plain_token = token_value
    
    return db_token

def get_token(db: Session, token_id: int) -> Optional[Token]:
    """Get a token by ID"""
    return db.query(Token).filter(Token.id == token_id).first()

def get_tokens_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Token]:
    """Get all tokens for a specific tenant"""
    return db.query(Token).filter(Token.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_tokens_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Token]:
    """Get all tokens for a specific user"""
    return db.query(Token).filter(Token.user_id == user_id).offset(skip).limit(limit).all()

def get_all_tokens(db: Session, skip: int = 0, limit: int = 100) -> List[Token]:
    """Get all tokens"""
    return db.query(Token).offset(skip).limit(limit).all()

def get_tokens_count(db: Session, tenant_id: Optional[int] = None, user_id: Optional[int] = None) -> int:
    """Get total count of tokens with optional filtering"""
    query = db.query(Token)
    
    if tenant_id:
        query = query.filter(Token.tenant_id == tenant_id)
    if user_id:
        query = query.filter(Token.user_id == user_id)
    
    return query.count()

def update_token(db: Session, token_id: int, token_update: TokenUpdate) -> Optional[Token]:
    """Update a token"""
    db_token = get_token(db, token_id)
    if not db_token:
        return None
    
    update_data = token_update.dict(exclude_unset=True)
    
    # Convert scopes list to JSON string if provided
    if "scopes" in update_data:
        update_data["scopes"] = json.dumps(update_data["scopes"])
    
    for field, value in update_data.items():
        setattr(db_token, field, value)
    
    db.commit()
    db.refresh(db_token)
    return db_token

def delete_token(db: Session, token_id: int) -> bool:
    """Delete a token"""
    db_token = get_token(db, token_id)
    if not db_token:
        return False
    
    db.delete(db_token)
    db.commit()
    return True

def verify_token(db: Session, token_value: str) -> Optional[Token]:
    """Verify a token and return the token object if valid"""
    # Get all active tokens
    tokens = db.query(Token).filter(Token.is_active == True).all()
    
    for token in tokens:
        if verify_password(token_value, token.token_hash):
            # Check if token is expired
            if token.expires_at and token.expires_at < datetime.utcnow():
                continue
            return token
    
    return None

def get_token_with_details(db: Session, token_id: int) -> Optional[dict]:
    """Get token with tenant and user details"""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        return None
    
    # Get tenant and user details
    tenant = db.query(Tenant).filter(Tenant.id == token.tenant_id).first()
    
    # Handle user details (user_id might be None)
    user_email = "No User"
    user_full_name = "No User"
    if token.user_id:
        user = db.query(User).filter(User.id == token.user_id).first()
        if user:
            user_email = user.email
            user_full_name = user.full_name
    
    return {
        "token": token,
        "tenant_name": tenant.name if tenant else "Unknown",
        "user_email": user_email,
        "user_full_name": user_full_name
    } 