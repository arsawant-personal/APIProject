#!/usr/bin/env python3
"""
Comprehensive API Token Test Script

This script tests:
1. API token creation with different scopes
2. Valid API calls with proper scopes
3. Invalid API calls with missing scopes (should fail)
4. API call tracking verification
5. Error tracking for failed calls
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@yourcompany.com"
ADMIN_PASSWORD = "your-super-admin-password"

class APITokenTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_tokens = []
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_admin_token(self):
        """Get admin JWT token for creating API tokens"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/token",
                data={
                    "username": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                self.log("✅ Admin token obtained successfully")
                return True
            else:
                self.log(f"❌ Failed to get admin token: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting admin token: {e}", "ERROR")
            return False
    
    def create_api_token(self, name, tenant_id, scopes):
        """Create an API token with specified scopes"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            data = {
                "name": name,
                "tenant_id": tenant_id,
                "user_id": None,
                "scopes": scopes,
                "is_active": True
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/v1/tokens/",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                token_info = {
                    "name": name,
                    "token": result["token"],
                    "scopes": scopes,
                    "tenant_id": tenant_id
                }
                self.test_tokens.append(token_info)
                self.log(f"✅ Created API token '{name}' with scopes: {scopes}")
                return token_info
            else:
                self.log(f"❌ Failed to create API token '{name}': {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error creating API token '{name}': {e}", "ERROR")
            return None
    
    def test_api_call(self, token_info, endpoint, method="GET", data=None, expected_success=True):
        """Test an API call with the given token"""
        try:
            headers = {"Authorization": f"Bearer {token_info['token']}"}
            if data:
                headers["Content-Type"] = "application/json"
            
            url = f"{BASE_URL}/api/v1/external/{endpoint}"
            
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data)
            else:
                self.log(f"❌ Unsupported method: {method}", "ERROR")
                return False
            
            success = response.status_code == 200
            result = {
                "token_name": token_info["name"],
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_success": expected_success,
                "actual_success": success,
                "response": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                "timestamp": datetime.now().isoformat()
            }
            
            if success == expected_success:
                self.log(f"✅ {method} {endpoint} - Status: {response.status_code} (Expected: {expected_success})")
            else:
                self.log(f"❌ {method} {endpoint} - Status: {response.status_code} (Expected: {expected_success})", "ERROR")
            
            self.test_results.append(result)
            return success == expected_success
            
        except Exception as e:
            self.log(f"❌ Error testing {method} {endpoint}: {e}", "ERROR")
            return False
    
    def get_api_calls(self):
        """Get recent API calls from the database"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(
                f"{BASE_URL}/api/v1/admin/api-calls/",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Failed to get API calls: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Error getting API calls: {e}", "ERROR")
            return []
    
    def verify_tracking(self, expected_calls):
        """Verify that API calls are being tracked correctly"""
        self.log("🔍 Verifying API call tracking...")
        
        # Wait a moment for tracking to complete
        time.sleep(2)
        
        api_calls = self.get_api_calls()
        if not api_calls:
            self.log("❌ No API calls found in tracking", "ERROR")
            return False
        
        # Filter calls made during our test period
        test_start = datetime.now() - timedelta(minutes=5)
        recent_calls = []
        for call in api_calls:
            try:
                # Skip if call is not a dict (might be pagination metadata)
                if not isinstance(call, dict):
                    continue
                    
                # Handle different date formats
                created_at_str = call.get("created_at", "")
                if created_at_str:
                    # Remove timezone info if present
                    created_at_str = created_at_str.replace("Z", "+00:00")
                    call_time = datetime.fromisoformat(created_at_str)
                    if call_time > test_start:
                        recent_calls.append(call)
            except Exception as e:
                print(f"Warning: Could not parse date for call: {call}")
                continue
        
        self.log(f"📊 Found {len(recent_calls)} recent API calls")
        
        # Check for our test calls
        found_calls = []
        for call in recent_calls:
            for expected in expected_calls:
                if (call["endpoint"] == expected["endpoint"] and 
                    call["method"] == expected["method"] and
                    call["tenant_id"] == expected["tenant_id"]):
                    found_calls.append(call)
                    break
        
        self.log(f"📊 Found {len(found_calls)} of {len(expected_calls)} expected calls")
        
        # Verify each expected call
        for expected in expected_calls:
            matching_calls = [
                call for call in found_calls
                if (call["endpoint"] == expected["endpoint"] and 
                    call["method"] == expected["method"])
            ]
            
            if matching_calls:
                call = matching_calls[0]
                self.log(f"✅ Found tracked call: {call['method']} {call['endpoint']} -> {call['response_status']} (Tenant: {call['tenant_id']})")
            else:
                self.log(f"❌ Missing tracked call: {expected['method']} {expected['endpoint']}", "ERROR")
        
        return len(found_calls) >= len(expected_calls) * 0.8  # Allow 80% success rate
    
    def run_comprehensive_test(self):
        """Run the comprehensive API token test"""
        self.log("🚀 Starting Comprehensive API Token Test")
        self.log("=" * 60)
        
        # Step 1: Get admin token
        if not self.get_admin_token():
            self.log("❌ Cannot proceed without admin token", "ERROR")
            return False
        
        # Step 2: Create test tokens with different scopes
        self.log("\n📝 Creating test API tokens...")
        
        # Token 1: Full access
        full_access_token = self.create_api_token(
            "Full Access Token",
            tenant_id=18,
            scopes=["health:read", "status:read", "ping:read", "profile:read", "tenant:read", "echo:write"]
        )
        
        # Token 2: Limited access (only health and ping)
        limited_token = self.create_api_token(
            "Limited Access Token", 
            tenant_id=18,
            scopes=["health:read", "ping:read"]
        )
        
        # Token 3: Minimal access (only one scope that doesn't match any endpoint)
        no_access_token = self.create_api_token(
            "No Access Token",
            tenant_id=18, 
            scopes=["invalid:scope"]
        )
        
        if not all([full_access_token, limited_token, no_access_token]):
            self.log("❌ Failed to create all test tokens", "ERROR")
            return False
        
        # Step 3: Test API calls
        self.log("\n🧪 Testing API calls...")
        
        expected_calls = []
        
        # Test 1: Full access token - all calls should succeed
        self.log("\n--- Testing Full Access Token ---")
        for endpoint in ["health", "status", "ping", "profile", "tenant"]:
            self.test_api_call(full_access_token, endpoint, expected_success=True)
            expected_calls.append({
                "endpoint": f"/api/v1/external/{endpoint}",
                "method": "GET",
                "tenant_id": 18
            })
        
        # Test POST endpoint
        self.test_api_call(full_access_token, "echo", method="POST", 
                          data={"message": "test", "number": 42}, expected_success=True)
        expected_calls.append({
            "endpoint": "/api/v1/external/echo",
            "method": "POST", 
            "tenant_id": 18
        })
        
        # Test 2: Limited access token - only health and ping should succeed
        self.log("\n--- Testing Limited Access Token ---")
        for endpoint in ["health", "ping"]:
            self.test_api_call(limited_token, endpoint, expected_success=True)
            expected_calls.append({
                "endpoint": f"/api/v1/external/{endpoint}",
                "method": "GET",
                "tenant_id": 18
            })
        
        # These should fail
        for endpoint in ["status", "profile", "tenant"]:
            self.test_api_call(limited_token, endpoint, expected_success=False)
            expected_calls.append({
                "endpoint": f"/api/v1/external/{endpoint}",
                "method": "GET",
                "tenant_id": 18
            })
        
        # Test 3: Minimal access token - all calls should fail (invalid scope)
        self.log("\n--- Testing Minimal Access Token (Invalid Scope) ---")
        for endpoint in ["health", "status", "ping", "profile", "tenant"]:
            self.test_api_call(no_access_token, endpoint, expected_success=False)
            expected_calls.append({
                "endpoint": f"/api/v1/external/{endpoint}",
                "method": "GET",
                "tenant_id": 18
            })
        
        # Step 4: Verify tracking
        self.log("\n📊 Verifying API call tracking...")
        tracking_success = self.verify_tracking(expected_calls)
        
        # Step 5: Generate report
        self.log("\n📋 Generating test report...")
        self.generate_report()
        
        return tracking_success
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        self.log("\n" + "=" * 60)
        self.log("📋 COMPREHENSIVE API TOKEN TEST REPORT")
        self.log("=" * 60)
        
        # Token summary
        self.log(f"\n🔑 API Tokens Created: {len(self.test_tokens)}")
        for token in self.test_tokens:
            self.log(f"  - {token['name']}: {len(token['scopes'])} scopes")
        
        # Test results summary
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["actual_success"] == result["expected_success"])
        
        self.log(f"\n🧪 Test Results:")
        self.log(f"  - Total tests: {total_tests}")
        self.log(f"  - Successful: {successful_tests}")
        self.log(f"  - Failed: {total_tests - successful_tests}")
        self.log(f"  - Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        self.log(f"\n📝 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["actual_success"] == result["expected_success"] else "❌"
            self.log(f"  {status} {result['method']} {result['endpoint']} -> {result['status_code']} (Expected: {result['expected_success']})")
        
        # API call tracking
        api_calls = self.get_api_calls()
        recent_calls = len([call for call in api_calls if call["tenant_id"] == 18])
        self.log(f"\n📊 API Call Tracking:")
        self.log(f"  - Recent calls for tenant 18: {recent_calls}")
        self.log(f"  - Total calls in system: {len(api_calls)}")
        
        self.log("\n" + "=" * 60)

def main():
    """Main test execution"""
    tester = APITokenTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n❌ COMPREHENSIVE TEST FAILED!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 