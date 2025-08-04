import time
import json
from typing import Dict, Any
from fastapi import Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.api_call import create_api_call
from app.schemas.api_call import APICallCreate

class APICallTracker:
    """Middleware for tracking API calls"""
    
    def __init__(self):
        self.excluded_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/favicon.ico"
        }
    
    def should_track(self, path: str) -> bool:
        """Determine if the path should be tracked"""
        return not any(path.startswith(excluded) for excluded in self.excluded_paths)
    
    def extract_payload(self, request: Request) -> str:
        """Extract request payload safely"""
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body = request.body()
                if body:
                    return body.decode('utf-8')
        except Exception:
            pass
        return None
    
    def extract_headers(self, request: Request) -> Dict[str, Any]:
        """Extract relevant headers"""
        headers = {}
        sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        
        for key, value in request.headers.items():
            if key.lower() not in sensitive_headers:
                headers[key] = value
        
        return headers
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None
    
    def track_api_call(
        self,
        request: Request,
        response: Response,
        processing_time: float,
        db: Session,
        current_user=None
    ):
        """Track an API call"""
        try:
            # Extract basic info
            path = str(request.url.path)
            method = request.method
            status_code = response.status_code
            
            print(f"🔍 Tracking API call: {method} {path} -> {status_code}")
            
            # Skip if not should track
            if not self.should_track(path):
                print(f"   Skipping {path} (excluded)")
                return
            
            print(f"   Tracking {path}")
            print(f"   Current user: {current_user.email if current_user else 'None'}")
            print(f"   Tenant ID: {current_user.tenant_id if current_user else 'None'}")
            
            # Extract payloads
            request_payload = self.extract_payload(request)
            response_payload = None
            
            # Try to get response body (this might not always work)
            try:
                if hasattr(response, 'body'):
                    response_payload = response.body.decode('utf-8') if response.body else None
            except Exception:
                pass
            
            # Calculate response size
            response_size = len(response_payload.encode('utf-8')) if response_payload else 0
            
            # Get user info
            tenant_id = None
            user_id = None
            
            if current_user:
                user_id = current_user.id
                tenant_id = current_user.tenant_id
            
            # Create API call record
            api_call_data = APICallCreate(
                endpoint=path,
                method=method,
                path=path,
                tenant_id=tenant_id,
                user_id=user_id,
                request_payload=request_payload,
                request_headers=self.extract_headers(request),
                request_ip=self.get_client_ip(request),
                response_payload=response_payload,
                response_status=status_code,
                response_size=response_size,
                processing_time=processing_time,
                response_time=processing_time,  # For now, same as processing time
                user_agent=request.headers.get("User-Agent")
            )
            
            print(f"   Saving API call to database...")
            # Save to database
            try:
                create_api_call(db, api_call_data)
                print(f"   ✅ API call saved successfully")
            except Exception as e:
                print(f"   ❌ Error saving API call: {e}")
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"❌ Error tracking API call: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Request path: {request.url.path}")
            print(f"   Request method: {request.method}")
            print(f"   Response status: {response.status_code}")

# Global tracker instance
api_tracker = APICallTracker() 