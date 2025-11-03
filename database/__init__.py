"""
Database module for CTI-NLP System
Provides MongoDB integration using Beanie ODM and Motor async driver
"""

from .mongodb_config import (
    mongodb_config,
    get_database,
    startup_mongodb,
    shutdown_mongodb,
    ensure_indexes,
    get_collection_stats,
    DatabaseSession
)

from .mongodb_models import (
    # Documents
    ThreatIntelligence,
    ExtractedEntity,
    AnalysisResult,
    SystemMetrics,
    DataIngestionLog,
    
    # Enums
    DataSource,
    ThreatCategory,
    SeverityLevel,
    EntityType,
    
    # Response Models
    ThreatIntelResponse,
    ThreatAnalysisResponse,
    DashboardStats,
    
    # Request Models
    ThreatAnalysisRequest,
    BulkAnalysisRequest
)

__all__ = [
    # Config and utilities
    "mongodb_config",
    "get_database", 
    "startup_mongodb",
    "shutdown_mongodb",
    "ensure_indexes",
    "get_collection_stats",
    "DatabaseSession",
    
    # Documents
    "ThreatIntelligence",
    "ExtractedEntity", 
    "AnalysisResult",
    "SystemMetrics",
    "DataIngestionLog",
    
    # Enums
    "DataSource",
    "ThreatCategory",
    "SeverityLevel", 
    "EntityType",
    
    # Response Models
    "ThreatIntelResponse",
    "ThreatAnalysisResponse",
    "DashboardStats",
    
    # Request Models  
    "ThreatAnalysisRequest",
    "BulkAnalysisRequest"
]