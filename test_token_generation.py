#!/usr/bin/env python3
"""
Test script to verify token generation and API access
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@yourcompany.com"
ADMIN_PASSWORD = "your-super-admin-password"

def get_admin_token():
    """Get admin access token"""
    response = requests.post(
        f"{API_BASE_URL}/auth/token",
        data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to get admin token: {response.status_code}")
        return None

def generate_user_token(admin_token, user_id):
    """Generate a bearer token for the API user"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.post(
        f"{API_BASE_URL}/admin/users/{user_id}/generate-token",
        headers=headers
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Generated token for user {user_id}")
        print(f"   Token: {token_data['access_token'][:50]}...")
        print(f"   User ID: {token_data['user_id']}")
        print(f"   Tenant ID: {token_data['tenant_id']}")
        return token_data
    else:
        print(f"❌ Failed to generate token: {response.status_code}")
        print(response.text)
        return None

def test_api_user_access(api_token):
    """Test that the API user can access external APIs"""
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # Test health check
    response = requests.get(
        f"{API_BASE_URL}/external/health",
        headers=headers
    )
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ API user can access health check")
        print(f"   Status: {health_data['status']}")
        print(f"   User ID: {health_data['user_id']}")
        print(f"   Tenant ID: {health_data['tenant_id']}")
        return True
    else:
        print(f"❌ API user cannot access health check: {response.status_code}")
        print(response.text)
        return False

def test_admin_api_access(api_token):
    """Test that API user cannot access admin APIs"""
    headers = {"Authorization": f"Bearer {api_token}"}
    
    response = requests.get(
        f"{API_BASE_URL}/admin/tenants/",
        headers=headers
    )
    
    if response.status_code == 403:
        print("✅ API user correctly denied access to admin APIs")
        return True
    else:
        print(f"❌ API user should not have admin access: {response.status_code}")
        return False

def main():
    print("🧪 Testing Token Generation and API Access")
    print("=" * 50)
    
    # Step 1: Get admin token
    print("\n1. Getting admin token...")
    admin_token = get_admin_token()
    if not admin_token:
        return
    
    # Step 2: Generate token for the API user (ID: 4)
    print("\n2. Generating bearer token for API user...")
    token_data = generate_user_token(admin_token, 4)
    if not token_data:
        return
    
    # Step 3: Test API user access to external APIs
    print("\n3. Testing API user access to external APIs...")
    test_api_user_access(token_data['access_token'])
    
    # Step 4: Test that API user cannot access admin APIs
    print("\n4. Testing API user access restrictions...")
    test_admin_api_access(token_data['access_token'])
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print(f"📋 Summary:")
    print(f"   - API user ID: {token_data['user_id']}")
    print(f"   - Token generated: {token_data['access_token'][:50]}...")
    print(f"   - Tenant association: {'✅ Working' if token_data['tenant_id'] else '❌ Failed'}")

if __name__ == "__main__":
    main() 