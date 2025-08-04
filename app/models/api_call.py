from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant and User Information
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # API Call Details
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    path = Column(String(500), nullable=False)
    
    # Request Details
    request_payload = Column(Text, nullable=True)  # JSON payload
    request_headers = Column(JSON, nullable=True)
    request_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    
    # Response Details
    response_status = Column(Integer, nullable=False, index=True)
    response_payload = Column(Text, nullable=True)  # JSON response
    response_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Performance Metrics
    processing_time = Column(Float, nullable=True)  # Time in seconds
    response_time = Column(Float, nullable=True)    # Total time including network
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="api_calls")
    user = relationship("User", back_populates="api_calls")
    
    def __repr__(self):
        return f"<APICall(id={self.id}, endpoint='{self.endpoint}', tenant_id={self.tenant_id}, status={self.response_status})>" 