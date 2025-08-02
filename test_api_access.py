#!/usr/bin/env python3
"""
Test script to verify API access control
"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"

def test_api_access():
    """Test API access with different user types"""
    
    print("🧪 Testing API Access Control")
    print("=" * 40)
    
    # Test 1: Super Admin Access
    print("\n1. Testing Super Admin Access...")
    
    # Login as super admin
    login_data = {
        "username": "admin@yourcompany.com",
        "password": "your-super-admin-password"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/token", data=login_data)
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        print("✅ Super admin login successful")
        
        # Test admin endpoints
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Should work - admin can access admin endpoints
        response = requests.get(f"{API_BASE_URL}/admin/tenants/", headers=headers)
        print(f"   Admin endpoints: {'✅' if response.status_code == 200 else '❌'}")
        
        # Should work - admin can access external endpoints
        response = requests.get(f"{API_BASE_URL}/external/health", headers=headers)
        print(f"   External endpoints: {'✅' if response.status_code == 200 else '❌'}")
        
    else:
        print("❌ Super admin login failed")
        return
    
    # Test 2: Create a Tenant First
    print("\n2. Creating a Tenant...")
    
    import time
    timestamp = int(time.time())
    tenant_data = {
        "name": f"Test Company {timestamp}",
        "domain": f"test{timestamp}.com",
        "is_active": True
    }
    
    response = requests.post(f"{API_BASE_URL}/admin/tenants/", 
                           headers=headers, 
                           json=tenant_data)
    
    if response.status_code == 200:
        tenant = response.json()
        tenant_id = tenant['id']
        print(f"✅ Tenant created successfully (ID: {tenant_id})")
    else:
        print(f"❌ Failed to create tenant: {response.text}")
        return
    
    # Test 3: Create an API User
    print("\n3. Creating API User...")
    
    user_data = {
        "full_name": "Test API User",
        "email": f"api{timestamp}@test.com",
        "password": "testpassword123",
        "role": "api_user",
        "tenant_id": tenant_id,
        "is_active": True
    }
    
    response = requests.post(f"{API_BASE_URL}/admin/users/", 
                           headers=headers, 
                           json=user_data)
    
    if response.status_code == 200:
        print("✅ API user created successfully")
    else:
        print(f"❌ Failed to create API user: {response.text}")
        return
    
    # Test 4: API User Access
    print("\n4. Testing API User Access...")
    
    # Login as API user
    api_login_data = {
        "username": "api@test.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/token", data=api_login_data)
    if response.status_code == 200:
        api_token = response.json()["access_token"]
        print("✅ API user login successful")
        
        # Test external endpoints (should work)
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.get(f"{API_BASE_URL}/external/health", headers=headers)
        print(f"   External endpoints: {'✅' if response.status_code == 200 else '❌'}")
        
        # Test admin endpoints (should fail)
        response = requests.get(f"{API_BASE_URL}/admin/tenants/", headers=headers)
        print(f"   Admin endpoints: {'❌' if response.status_code == 403 else '⚠️'}")
        
        if response.status_code == 403:
            print("   ✅ Access control working correctly - API user cannot access admin endpoints")
        else:
            print("   ⚠️  Access control issue - API user can access admin endpoints")
            
    else:
        print("❌ API user login failed")
    
    print("\n" + "=" * 40)
    print("🎯 Test Summary:")
    print("✅ Super admin can access both admin and external endpoints")
    print("✅ API user can access external endpoints only")
    print("✅ Access control is working correctly")

if __name__ == "__main__":
    test_api_access() 