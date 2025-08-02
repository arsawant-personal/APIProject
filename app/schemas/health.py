from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    user_id: int
    tenant_id: Optional[int]
    message: str 