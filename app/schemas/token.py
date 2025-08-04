from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TokenBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: List[str] = Field(..., min_items=1)
    is_active: bool = True
    expires_at: Optional[datetime] = None

class TokenCreate(TokenBase):
    tenant_id: int
    user_id: Optional[int] = None

class TokenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    scopes: Optional[List[str]] = Field(None, min_items=1)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class TokenResponse(TokenBase):
    id: int
    token_hash: str
    tenant_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TokenWithDetails(TokenResponse):
    tenant_name: str
    user_email: str
    user_full_name: str

class TokenCreateResponse(BaseModel):
    token: str
    token_details: TokenResponse
    message: str = "Token created successfully. Please copy the token now as it won't be shown again."

class TokenPaginated(BaseModel):
    items: List[TokenWithDetails]
    total: int
    page: int
    size: int
    pages: int 