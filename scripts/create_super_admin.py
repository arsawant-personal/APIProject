import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate
from app.models.user import UserRole

def create_super_admin():
    db = SessionLocal()
    try:
        # Check if super admin already exists
        existing_admin = get_user_by_email(db=db, email="admin@yourcompany.com")
        if existing_admin:
            print(f"Super admin already exists: {existing_admin.email}")
            return
        
        # Create super admin user
        super_admin = UserCreate(
            email="admin@yourcompany.com",  # Change this in production
            password="your-super-admin-password",  # Change this in production
            full_name="Super Admin",
            role=UserRole.SUPER_ADMIN
        )
        
        user = create_user(db=db, user=super_admin)
        print(f"Super admin created successfully!")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print("\nIMPORTANT: Change the default credentials in production!")
        
    except Exception as e:
        print(f"Error creating super admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin() 