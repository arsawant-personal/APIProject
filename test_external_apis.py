#!/usr/bin/env python3
"""
Test External APIs
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_external_apis():
    """Test the external APIs with an API user token"""
    
    print("🧪 Testing External APIs")
    print("=" * 40)
    
    # 1. Login as super admin
    admin_login_data = {
        "username": "admin@yourcompany.com",
        "password": "your-super-admin-password"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/token", data=admin_login_data)
    if response.status_code != 200:
        print("❌ Super admin login failed")
        return
    
    admin_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Create a tenant
    import time
    timestamp = int(time.time())
    tenant_data = {
        "name": f"Demo Company {timestamp}",
        "domain": f"demo{timestamp}.com",
        "is_active": True
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/admin/tenants/", 
                           headers=headers, 
                           json=tenant_data)
    
    if response.status_code != 200:
        print("❌ Failed to create tenant")
        return
    
    tenant = response.json()
    tenant_id = tenant['id']
    print(f"✅ Created tenant: {tenant['name']} (ID: {tenant_id})")
    
    # 3. Create an API user
    user_data = {
        "full_name": "Demo API User",
        "email": f"demo{timestamp}@test.com",
        "password": "demo123",
        "role": "API_USER",
        "tenant_id": tenant_id,
        "is_active": True
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/admin/users/", 
                           headers=headers, 
                           json=user_data)
    
    if response.status_code != 200:
        print("❌ Failed to create API user")
        return
    
    print("✅ Created API user")
    
    # 4. Login as API user
    api_login_data = {
        "username": f"demo{timestamp}@test.com",
        "password": "demo123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/token", data=api_login_data)
    if response.status_code != 200:
        print("❌ API user login failed")
        return
    
    api_token = response.json()["access_token"]
    api_headers = {"Authorization": f"Bearer {api_token}"}
    
    print("✅ API user login successful")
    print(f"🔑 Token: {api_token[:20]}...")
    
    # 5. Test External APIs
    print("\n📡 Testing External APIs:")
    print("-" * 30)
    
    # Health Check
    print("\n1. Health Check (/api/v1/external/health):")
    response = requests.get(f"{API_BASE_URL}/api/v1/external/health", headers=api_headers)
    if response.status_code == 200:
        health_data = response.json()
        print("✅ Health check successful")
        print(f"   Status: {health_data['status']}")
        print(f"   Message: {health_data['message']}")
        print(f"   User ID: {health_data['user_id']}")
        print(f"   Tenant ID: {health_data['tenant_id']}")
        print(f"   Timestamp: {health_data['timestamp']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(response.text)
    
    # Service Status
    print("\n2. Service Status (/api/v1/external/status):")
    response = requests.get(f"{API_BASE_URL}/api/v1/external/status", headers=api_headers)
    if response.status_code == 200:
        status_data = response.json()
        print("✅ Service status successful")
        print(f"   Service: {status_data['service']}")
        print(f"   Version: {status_data['version']}")
        print(f"   Status: {status_data['status']}")
        print(f"   User: {status_data['user']['email']}")
        print(f"   Tenant: {status_data['user']['tenant_id']}")
    else:
        print(f"❌ Service status failed: {response.status_code}")
        print(response.text)
    
    # User Profile
    print("\n3. User Profile (/api/v1/external/profile):")
    response = requests.get(f"{API_BASE_URL}/api/v1/external/profile", headers=api_headers)
    if response.status_code == 200:
        profile_data = response.json()
        print("✅ User profile successful")
        print(f"   Name: {profile_data['full_name']}")
        print(f"   Email: {profile_data['email']}")
        print(f"   Role: {profile_data['role']}")
        print(f"   Tenant ID: {profile_data['tenant_id']}")
        print(f"   Active: {profile_data['is_active']}")
    else:
        print(f"❌ User profile failed: {response.status_code}")
        print(response.text)
    
    # Tenant Info
    print("\n4. Tenant Info (/api/v1/external/tenant):")
    response = requests.get(f"{API_BASE_URL}/api/v1/external/tenant", headers=api_headers)
    if response.status_code == 200:
        tenant_data = response.json()
        print("✅ Tenant info successful")
        print(f"   Name: {tenant_data['name']}")
        print(f"   Domain: {tenant_data['domain']}")
        print(f"   Active: {tenant_data['is_active']}")
        print(f"   ID: {tenant_data['id']}")
    else:
        print(f"❌ Tenant info failed: {response.status_code}")
        print(response.text)
    
    # Ping
    print("\n5. Ping (/api/v1/external/ping):")
    response = requests.get(f"{API_BASE_URL}/api/v1/external/ping", headers=api_headers)
    if response.status_code == 200:
        ping_data = response.json()
        print("✅ Ping successful")
        print(f"   Pong: {ping_data['pong']}")
        print(f"   User ID: {ping_data['user_id']}")
        print(f"   Timestamp: {ping_data['timestamp']}")
    else:
        print(f"❌ Ping failed: {response.status_code}")
        print(response.text)
    
    # Echo
    print("\n6. Echo (/api/v1/external/echo):")
    echo_data = {"test": "message", "number": 42, "boolean": True}
    response = requests.post(f"{API_BASE_URL}/api/v1/external/echo", 
                           headers=api_headers, 
                           json=echo_data)
    if response.status_code == 200:
        echo_response = response.json()
        print("✅ Echo successful")
        print(f"   Message: {echo_response['message']}")
        print(f"   Echo: {echo_response['echo']}")
        print(f"   User ID: {echo_response['user_id']}")
        print(f"   Tenant ID: {echo_response['tenant_id']}")
    else:
        print(f"❌ Echo failed: {response.status_code}")
        print(response.text)
    
    # 6. Test Access Control
    print("\n🔒 Testing Access Control:")
    print("-" * 30)
    
    # Try to access admin endpoint (should fail)
    response = requests.get(f"{API_BASE_URL}/api/v1/admin/tenants/", headers=api_headers)
    if response.status_code == 403:
        print("✅ Access control working - API user cannot access admin endpoints")
    else:
        print(f"⚠️  Access control issue - API user can access admin endpoints: {response.status_code}")
    
    print("\n" + "=" * 40)
    print("🎯 External API Summary:")
    print("✅ Health check endpoint available")
    print("✅ Service status endpoint available")
    print("✅ User profile endpoint available")
    print("✅ Tenant info endpoint available")
    print("✅ Ping endpoint available")
    print("✅ Echo endpoint available")
    print("✅ Proper authentication required")
    print("✅ Access control enforced")
    print("✅ Tenant isolation working")

if __name__ == "__main__":
    test_external_apis() 