"""
Simple API test to verify the MongoDB-enabled dashboard
"""

import requests
import json

def test_api_endpoints():
    """Test the main API endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/health",
        "/api/stats", 
        "/api/database_stats",
        "/feed",
        "/"
    ]
    
    print("🔄 Testing API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                
                # Show some data for specific endpoints
                if endpoint == "/api/stats":
                    data = response.json()
                    print(f"   📊 Total threats: {data.get('total_threats', 'N/A')}")
                    print(f"   🗃️ Database mode: {data.get('processing_stats', {}).get('database_mode', 'N/A')}")
                    
                elif endpoint == "/api/database_stats":
                    data = response.json()
                    print(f"   🗄️ Database type: {data.get('database_type', 'N/A')}")
                    print(f"   🔗 Connection: {data.get('connection_status', 'N/A')}")
                    
                elif endpoint == "/health":
                    data = response.json()
                    print(f"   🏥 Status: {data.get('status', 'N/A')}")
                    print(f"   🗃️ MongoDB: {data.get('services', {}).get('mongodb', 'N/A')}")
                    
                elif endpoint == "/feed":
                    data = response.json()
                    print(f"   📰 Feed items: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                elif endpoint == "/":
                    data = response.json()
                    print(f"   🗃️ Database mode: {data.get('database_mode', 'N/A')}")
                    
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection failed - Server might not be running")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_analyze_endpoint():
    """Test the analyze endpoint"""
    base_url = "http://localhost:8000"
    
    print(f"\n🧪 Testing threat analysis...")
    print("-" * 30)
    
    test_data = {
        "text": "Malicious phishing email detected targeting banking credentials",
        "source": "manual"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analysis successful!")
            print(f"   🎯 Category: {data.get('threat_category', 'N/A')}")
            print(f"   ⚠️ Severity: {data.get('severity_level', 'N/A')}")
            print(f"   🎰 Confidence: {data.get('confidence_score', 'N/A')}")
            print(f"   🗃️ Stored in DB: {data.get('database_stored', 'N/A')}")
            print(f"   ⏱️ Processing time: {data.get('processing_time_ms', 'N/A')}ms")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 CTI-NLP API Integration Test")
    print("=" * 50)
    
    # Test basic endpoints
    test_api_endpoints()
    
    # Test analysis endpoint
    test_analyze_endpoint()
    
    print(f"\n🎉 API testing completed!")