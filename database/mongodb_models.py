"""
MongoDB Models using Beanie ODM for the CTI-NLP System
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class DataSource(str, Enum):
    TWITTER = "twitter"
    DARKWEB = "darkweb"
    MITRE_ATTACK = "mitre_attack"
    MANUAL = "manual"
    CSV_UPLOAD = "csv_upload"

class ThreatCategory(str, Enum):
    MALWARE = "Malware"
    PHISHING = "Phishing"
    RANSOMWARE = "Ransomware"
    DDOS = "DDoS"
    OTHER = "Other"

class SeverityLevel(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    MISCELLANEOUS = "MISC"

# MongoDB Documents (Collections)

class ThreatIntelligence(Document):
    """Main threat intelligence document"""
    
    # Core fields
    text: Indexed(str)  # Original threat text
    source: DataSource
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis results
    threat_category: Optional[ThreatCategory] = None
    severity_level: Optional[SeverityLevel] = None
    confidence_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    
    # Extracted entities
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Additional metadata
    processed: bool = Field(default=False)
    processing_timestamp: Optional[datetime] = None
    
    # Analysis details
    analysis_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Settings:
        name = "threat_intelligence"
        indexes = [
            [("text", "text")],  # Text search index
            [("source", 1)],
            [("timestamp", -1)],
            [("threat_category", 1)],
            [("severity_level", 1)],
            [("processed", 1)]
        ]

class ExtractedEntity(Document):
    """Extracted entities from threat intelligence"""
    
    threat_id: Indexed(str)  # Reference to ThreatIntelligence document
    entity_text: str
    entity_type: EntityType
    confidence_score: float = Field(ge=0.0, le=1.0)
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    
    # Additional context
    context: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "extracted_entities"
        indexes = [
            [("threat_id", 1)],
            [("entity_type", 1)],
            [("entity_text", 1)],
            [("confidence_score", -1)]
        ]

class AnalysisResult(Document):
    """Detailed analysis results for threat intelligence"""
    
    threat_id: Indexed(str)  # Reference to ThreatIntelligence document
    analysis_type: str  # "classification", "severity", "ner"
    
    # Results
    result: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: Optional[str] = None
    
    # Processing info
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analysis_results"
        indexes = [
            [("threat_id", 1)],
            [("analysis_type", 1)],
            [("timestamp", -1)]
        ]

class SystemMetrics(Document):
    """System performance and usage metrics"""
    
    metric_name: str
    metric_value: float
    metric_type: str  # "counter", "gauge", "histogram"
    tags: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "system_metrics"
        indexes = [
            [("metric_name", 1)],
            [("timestamp", -1)],
            [("metric_type", 1)]
        ]

class DataIngestionLog(Document):
    """Log of data ingestion activities"""
    
    source: DataSource
    ingestion_type: str  # "scheduled", "manual", "real_time"
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Details
    summary: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "data_ingestion_logs"
        indexes = [
            [("source", 1)],
            [("start_time", -1)],
            [("ingestion_type", 1)]
        ]

# Response Models (for API)

class ThreatIntelResponse(BaseModel):
    """Response model for threat intelligence"""
    id: str
    text: str
    source: DataSource
    timestamp: datetime
    threat_category: Optional[ThreatCategory] = None
    severity_level: Optional[SeverityLevel] = None
    confidence_score: Optional[float] = None
    entities: List[Dict[str, Any]] = []
    processed: bool = False

class ThreatAnalysisResponse(BaseModel):
    """Response model for threat analysis"""
    threat_category: ThreatCategory
    severity_level: SeverityLevel
    confidence_score: float
    entities: List[Dict[str, Any]]
    analysis_details: Dict[str, Any]
    processing_time_ms: float

class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    total_threats: int
    threats_by_category: Dict[str, int]
    threats_by_severity: Dict[str, int]
    threats_by_source: Dict[str, int]
    recent_threats: List[ThreatIntelResponse]
    top_entities: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]

# Request Models

class ThreatAnalysisRequest(BaseModel):
    """Request model for threat analysis"""
    text: str
    source: Optional[DataSource] = DataSource.MANUAL

class BulkAnalysisRequest(BaseModel):
    """Request model for bulk threat analysis"""
    texts: List[str]
    source: Optional[DataSource] = DataSource.CSV_UPLOAD