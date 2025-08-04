from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class APICallBase(BaseModel):
    endpoint: str
    method: str
    path: str
    response_status: int
    processing_time: Optional[float] = None
    response_size: Optional[int] = None

class APICallCreate(APICallBase):
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    request_payload: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_ip: Optional[str] = None
    response_payload: Optional[str] = None
    response_time: Optional[float] = None
    user_agent: Optional[str] = None

class APICall(APICallBase):
    id: int
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    request_payload: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_ip: Optional[str] = None
    response_payload: Optional[str] = None
    response_time: Optional[float] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class APICallWithDetails(APICall):
    tenant_name: Optional[str] = None
    user_email: Optional[str] = None

class APICallFilter(BaseModel):
    tenant_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    response_status: Optional[int] = None
    limit: int = 100
    offset: int = 0

class APICallStats(BaseModel):
    total_calls: int
    total_processing_time: float
    avg_processing_time: float
    total_response_size: int
    avg_response_size: float
    success_rate: float
    calls_by_endpoint: Dict[str, int]
    calls_by_status: Dict[int, int]

class APICallPaginated(BaseModel):
    items: list[APICall]
    total: int
    page: int
    size: int
    pages: int

class APICallPaginatedWithDetails(BaseModel):
    items: list[APICallWithDetails]
    total: int
    page: int
    size: int
    pages: int 