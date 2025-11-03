#!/usr/bin/env python3
"""
Simple test script to check if the fixed analytics and sources endpoints are working
"""
import requests
import json

def test_endpoint(url, endpoint_name):
    """Test an endpoint and return the result"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print(f"✅ {endpoint_name}: SUCCESS (200 OK)")
            # Show first 200 chars of response for verification
            content = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"   Response: {content}")
            return True
        else:
            print(f"❌ {endpoint_name}: FAILED ({response.status_code})")
            print(f"   Error: {response.text[:200]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name}: CONNECTION ERROR - {str(e)}")
        return False

def main():
    base_url = "http://localhost:8001"
    
    print("Testing CTI-NLP System Endpoints...")
    print("=" * 50)
    
    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/api/threats?page=1&limit=5", "Threats API"),
        (f"{base_url}/analytics?days=30", "Analytics API"),
        (f"{base_url}/api/sources", "Data Sources API"),
    ]
    
    results = []
    for url, name in endpoints:
        print(f"\nTesting {name}...")
        success = test_endpoint(url, name)
        results.append((name, success))
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The aggregation fixes worked!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()