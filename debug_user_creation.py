#!/usr/bin/env python3
"""
Debug script to test user creation step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate
from app.crud.user import create_user
from app.models.user import UserRole

def test_user_creation():
    """Test user creation directly"""
    print("Testing user creation...")
    
    # Create a test user
    user_data = UserCreate(
        full_name="Test API User",
        email="api@testcompany.com",
        password="testpassword123",
        role=UserRole.API_USER,
        tenant_id=1,
        is_active=True
    )
    
    print(f"User data: {user_data}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Try to create user
        user = create_user(db=db, user=user_data)
        print(f"✅ User created successfully: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Tenant ID: {user.tenant_id}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        return user
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    test_user_creation() 