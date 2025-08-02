from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.user import UserRole
from app.schemas.tenant import Tenant

class UserBase(BaseModel):
    email: str
    full_name: str
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str
    tenant_id: Optional[int] = None
    is_active: bool = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    tenant_id: Optional[int] = None
    tenant: Optional[Tenant] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 