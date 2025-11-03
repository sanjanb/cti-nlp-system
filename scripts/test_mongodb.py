"""
Test script to verify MongoDB integration and check database statistics
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database import (
    startup_mongodb,
    shutdown_mongodb,
    get_collection_stats,
    ThreatIntelligence,
    mongodb_config
)

async def test_mongodb_integration():
    """Test MongoDB integration and display statistics"""
    print("🔄 Testing MongoDB integration...")
    
    # Connect to MongoDB
    success = await startup_mongodb()
    if not success:
        print("❌ Failed to connect to MongoDB")
        return False
    
    print("✅ MongoDB connection established")
    
    try:
        # Get collection statistics
        stats = await get_collection_stats()
        print("\n📊 Database Statistics:")
        print("-" * 40)
        for collection, count in stats.items():
            print(f"  {collection}: {count:,} records")
        
        # Get total threat intelligence records
        total_threats = await ThreatIntelligence.count()
        print(f"\n📈 Total Threat Intelligence Records: {total_threats:,}")
        
        # Get sample records
        print("\n📋 Sample Records:")
        print("-" * 40)
        sample_threats = await ThreatIntelligence.find_all().limit(3).to_list()
        
        for i, threat in enumerate(sample_threats, 1):
            print(f"\n{i}. ID: {threat.id}")
            print(f"   Source: {threat.source}")
            print(f"   Text: {threat.text[:100]}...")
            print(f"   Category: {threat.threat_category}")
            print(f"   Severity: {threat.severity_level}")
            print(f"   Processed: {threat.processed}")
        
        # Test health check
        health = await mongodb_config.health_check()
        print(f"\n💚 MongoDB Health Check:")
        print("-" * 40)
        print(f"  Status: {health['status']}")
        print(f"  Database: {health.get('database', 'N/A')}")
        print(f"  Collections: {health.get('collections_count', 'N/A')}")
        print(f"  Data Size: {health.get('data_size', 'N/A')} bytes")
        
        # Test aggregation
        print(f"\n🔍 Source Distribution:")
        print("-" * 40)
        source_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        source_results = await ThreatIntelligence.aggregate(source_pipeline).to_list()
        
        for result in source_results:
            source = result.get("_id", "Unknown")
            count = result.get("count", 0)
            print(f"  {source}: {count:,} records")
        
        print("\n✅ MongoDB integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        await shutdown_mongodb()

async def main():
    """Main test function"""
    print("🚀 CTI-NLP MongoDB Integration Test")
    print("=" * 50)
    
    success = await test_mongodb_integration()
    
    if success:
        print("\n🎉 All tests passed! MongoDB integration is working correctly.")
        return 0
    else:
        print("\n💥 Tests failed! Please check your MongoDB setup.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())