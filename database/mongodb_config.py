"""
MongoDB Connection Configuration for CTI-NLP System
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional, List
import logging

from .mongodb_models import (
    ThreatIntelligence,
    ExtractedEntity,
    AnalysisResult,
    SystemMetrics,
    DataIngestionLog
)

logger = logging.getLogger(__name__)

class MongoDBConfig:
    """MongoDB configuration and connection management"""
    
    def __init__(self):
        # MongoDB connection settings
        self.host = os.getenv("MONGODB_HOST", "localhost")
        self.port = int(os.getenv("MONGODB_PORT", 27017))
        self.database_name = os.getenv("MONGODB_DATABASE", "cti_nlp_system")
        self.username = os.getenv("MONGODB_USERNAME", None)
        self.password = os.getenv("MONGODB_PASSWORD", None)
        
        # Connection options
        self.max_pool_size = int(os.getenv("MONGODB_MAX_POOL_SIZE", 10))
        self.min_pool_size = int(os.getenv("MONGODB_MIN_POOL_SIZE", 1))
        self.timeout_ms = int(os.getenv("MONGODB_TIMEOUT_MS", 5000))
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    def get_connection_string(self) -> str:
        """Generate MongoDB connection string"""
        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        else:
            return f"mongodb://{self.host}:{self.port}/{self.database_name}"
    
    async def connect(self) -> bool:
        """Connect to MongoDB and initialize Beanie"""
        try:
            # Create MongoDB client
            connection_string = self.get_connection_string()
            logger.info(f"Connecting to MongoDB at {self.host}:{self.port}")
            
            self.client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                serverSelectionTimeoutMS=self.timeout_ms
            )
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.database,
                document_models=[
                    ThreatIntelligence,
                    ExtractedEntity,
                    AnalysisResult,
                    SystemMetrics,
                    DataIngestionLog
                ]
            )
            
            logger.info("Beanie ODM initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> dict:
        """Check MongoDB connection health"""
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No client connection"}
            
            # Ping database
            result = await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            # Get database stats
            db_stats = await self.database.command("dbStats")
            
            return {
                "status": "healthy",
                "server_version": server_info.get("version"),
                "database": self.database_name,
                "collections_count": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global MongoDB configuration instance
mongodb_config = MongoDBConfig()

async def get_database():
    """Get the MongoDB database instance"""
    if not mongodb_config.database:
        await mongodb_config.connect()
    return mongodb_config.database

async def startup_mongodb():
    """Startup function to initialize MongoDB connection"""
    success = await mongodb_config.connect()
    if not success:
        logger.warning("Failed to connect to MongoDB - running in file-based mode")
        return False
    return True

async def shutdown_mongodb():
    """Shutdown function to close MongoDB connection"""
    await mongodb_config.disconnect()

# Utility functions for database operations

async def ensure_indexes():
    """Ensure all required indexes are created"""
    try:
        # Threat Intelligence indexes
        await ThreatIntelligence.get_motor_collection().create_index([("text", "text")])
        await ThreatIntelligence.get_motor_collection().create_index([("timestamp", -1)])
        await ThreatIntelligence.get_motor_collection().create_index([("source", 1)])
        
        # Extracted Entities indexes
        await ExtractedEntity.get_motor_collection().create_index([("threat_id", 1)])
        await ExtractedEntity.get_motor_collection().create_index([("entity_type", 1)])
        
        # Analysis Results indexes
        await AnalysisResult.get_motor_collection().create_index([("threat_id", 1)])
        await AnalysisResult.get_motor_collection().create_index([("analysis_type", 1)])
        
        logger.info("All MongoDB indexes ensured successfully")
        
    except Exception as e:
        logger.error(f"Failed to ensure indexes: {str(e)}")

async def get_collection_stats() -> dict:
    """Get statistics for all collections"""
    try:
        database = await get_database()
        
        stats = {}
        collections = [
            "threat_intelligence",
            "extracted_entities", 
            "analysis_results",
            "system_metrics",
            "data_ingestion_logs"
        ]
        
        for collection_name in collections:
            collection = database[collection_name]
            count = await collection.count_documents({})
            stats[collection_name] = count
            
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {str(e)}")
        return {}

# Async context manager for database operations
class DatabaseSession:
    """Context manager for database operations with automatic connection handling"""
    
    async def __aenter__(self):
        if not mongodb_config.database:
            await mongodb_config.connect()
        return mongodb_config.database
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Keep connection open for reuse
        pass