from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    user_id: Optional[int]
    tenant_id: Optional[int]
    message: str 