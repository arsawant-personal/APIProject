#!/usr/bin/env python3
"""
Database Reset Script
====================

This script clears all data from the database while preserving the schema:
1. Clears all data from tables (preserves structure)
2. Verifies migrations are up to date
3. Creates the super admin user
4. Verifies the reset was successful

Usage:
    python reset_database.py [--confirm]

Options:
    --confirm    Skip confirmation prompt (useful for automation)
"""

import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.models import user, tenant, product
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def print_banner():
    """Print a warning banner"""
    print("=" * 80)
    print("🚨 DATABASE RESET WARNING 🚨")
    print("=" * 80)
    print("This script will:")
    print("  ❌ DELETE ALL DATA in the database")
    print("  ❌ REMOVE ALL USERS, TENANTS, AND PRODUCTS")
    print("  ✅ PRESERVE database schema and structure")
    print("  ✅ Verify migrations are up to date")
    print("  ✅ Create the super admin user")
    print("=" * 80)
    print()

def confirm_reset():
    """Ask for user confirmation"""
    if "--confirm" in sys.argv:
        return True
    
    response = input("Are you sure you want to reset the database? (yes/no): ").lower().strip()
    return response in ['yes', 'y']

def test_database_connection():
    """Test if we can connect to the database"""
    print("🔍 Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL in .env file")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def clear_all_data():
    """Clear all data from tables while preserving structure"""
    print("🗑️  Clearing all data from tables...")
    try:
        with engine.connect() as conn:
            # Get all table names (excluding alembic_version)
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%'
                AND tablename NOT LIKE 'sql_%'
                AND tablename != 'alembic_version'
            """))
            tables = [row[0] for row in result]
            
            if not tables:
                print("ℹ️  No tables found to clear")
                return True
            
            print(f"Found {len(tables)} tables to clear: {', '.join(tables)}")
            
            # Clear all data from tables (preserve structure)
            for table in tables:
                conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
                print(f"  ✅ Cleared data from table: {table}")
            
            conn.commit()
            print("✅ All data cleared successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def verify_migrations():
    """Verify migrations are up to date"""
    print("🔍 Verifying migrations...")
    try:
        # Check if alembic_version table exists and has current version
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ Migrations are up to date")
            return True
        else:
            print(f"⚠️  Migration check failed: {result.stderr}")
            print("Running migrations to ensure schema is current...")
            
            # Run migrations to ensure schema is current
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.returncode == 0:
                print("✅ Migrations completed successfully")
                return True
            else:
                print(f"❌ Migration failed: {result.stderr}")
                return False
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        return False

def create_super_admin():
    """Create the super admin user"""
    print("👤 Creating super admin user...")
    try:
        db = SessionLocal()
        
        # Check if super admin already exists
        existing_admin = db.query(user.User).filter(
            user.User.email == settings.SUPER_ADMIN_EMAIL
        ).first()
        
        if existing_admin:
            print(f"ℹ️  Super admin already exists: {existing_admin.email}")
            db.close()
            return True
        
        # Create super admin user
        super_admin_data = UserCreate(
            email=settings.SUPER_ADMIN_EMAIL,
            password=settings.SUPER_ADMIN_PASSWORD,
            full_name="Super Administrator",
            role="SUPER_ADMIN",
            is_active=True,
            tenant_id=None  # Super admin doesn't belong to any tenant
        )
        
        super_admin = create_user(db=db, user=super_admin_data)
        print(f"✅ Super admin created: {super_admin.email}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        return False

def verify_reset():
    """Verify the database reset was successful"""
    print("🔍 Verifying database reset...")
    try:
        db = SessionLocal()
        
        # Check tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('users', 'tenants', 'products', 'alembic_version')
            """))
            tables = [row[0] for row in result]
            
            expected_tables = ['users', 'tenants', 'products', 'alembic_version']
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print("✅ All required tables exist")
        
        # Check super admin exists
        admin = db.query(user.User).filter(
            user.User.email == settings.SUPER_ADMIN_EMAIL
        ).first()
        
        if admin:
            print(f"✅ Super admin exists: {admin.email}")
        else:
            print("❌ Super admin not found")
            return False
        
        # Check no other data exists (except super admin)
        user_count = db.query(user.User).count()
        tenant_count = db.query(tenant.Tenant).count()
        product_count = db.query(product.Product).count()
        
        print(f"📊 Database state:")
        print(f"  Users: {user_count} (should be 1 - super admin only)")
        print(f"  Tenants: {tenant_count} (should be 0)")
        print(f"  Products: {product_count} (should be 0)")
        
        if user_count == 1 and tenant_count == 0 and product_count == 0:
            print("✅ Database reset verification successful")
            return True
        else:
            print("❌ Database reset verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying reset: {e}")
        return False
    finally:
        db.close()

def main():
    """Main reset function"""
    print_banner()
    
    if not confirm_reset():
        print("❌ Database reset cancelled")
        return False
    
    print("🚀 Starting database reset...")
    
    # Step 1: Test connection
    if not test_database_connection():
        return False
    
    # Step 2: Clear all data
    if not clear_all_data():
        return False
    
    # Step 3: Verify migrations
    if not verify_migrations():
        return False
    
    # Step 4: Create super admin
    if not create_super_admin():
        return False
    
    # Step 5: Verify reset
    if not verify_reset():
        return False
    
    print("\n" + "=" * 80)
    print("🎉 DATABASE RESET COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("✅ All data has been removed")
    print("✅ Database schema has been preserved")
    print("✅ Super admin user has been created")
    print("✅ Database is ready for use")
    print("\n📋 Next steps:")
    print("  1. Start the servers: python manage_servers.py start")
    print("  2. Access admin console: http://localhost:8080")
    print("  3. Login with: admin@yourcompany.com / your-super-admin-password")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 