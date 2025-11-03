"""
Updated FastAPI main application using MongoDB instead of SQLAlchemy
"""

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from scripts.ingest_all_sources import main as ingest_all_sources_main

import asyncio
import pandas as pd
import tempfile
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity

# Enhanced analyzer import
try:
    from backend.simple_enhanced_analyzer import (
        analyze_threat_comprehensive, 
        get_model_info,
        initialize_analyzer
    )
    ENHANCED_ANALYZER_AVAILABLE = True
    # Initialize the enhanced analyzer
    initialize_analyzer()
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhanced analyzer not available: {e}")
    ENHANCED_ANALYZER_AVAILABLE = False

# MongoDB Database imports
from database import (
    startup_mongodb,
    shutdown_mongodb,
    get_database,
    get_collection_stats,
    mongodb_config,
    ThreatIntelligence,
    ExtractedEntity,
    AnalysisResult,
    DataSource,
    ThreatCategory,
    SeverityLevel,
    ThreatAnalysisRequest,
    ThreatIntelResponse,
    DashboardStats
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CTI-NLP API",
    description="AI-Powered Cyber Threat Intelligence System with MongoDB",
    version="2.0.0"
)

# Global variables
USE_MONGODB = False

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "running",
                "mongodb": "unknown"
            }
        }
        
        if USE_MONGODB:
            # Test MongoDB connection
            mongo_health = await mongodb_config.health_check()
            health_status["services"]["mongodb"] = mongo_health["status"]
            health_status["mongodb_info"] = mongo_health
        else:
            health_status["services"]["mongodb"] = "disabled"
            health_status["mode"] = "file_based"
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# -------------------
# Background ingestion
# -------------------
async def ingestion_loop(interval_minutes=10):
    """Background task for periodic data ingestion"""
    while True:
        try:
            logger.info("Running real-time ingestion...")
            ingest_all_sources_main()
        except Exception as e:
            logger.error(f"Ingestion loop failed: {e}")
        await asyncio.sleep(interval_minutes * 60)

@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    global USE_MONGODB
    
    # Try to connect to MongoDB
    try:
        success = await startup_mongodb()
        if success:
            USE_MONGODB = True
            logger.info("✅ MongoDB connected successfully - Using database mode")
        else:
            USE_MONGODB = False
            logger.warning("⚠️ MongoDB connection failed - Using file-based mode")
    except Exception as e:
        USE_MONGODB = False
        logger.warning(f"⚠️ MongoDB startup failed: {e} - Using file-based mode")
    
    # Start background ingestion
    asyncio.create_task(ingestion_loop(interval_minutes=10))

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    if USE_MONGODB:
        await shutdown_mongodb()
        logger.info("MongoDB connection closed")

# -------------------
# CORS Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")

# -------------------
# Root endpoint with ingestion status
# -------------------
@app.get("/")
async def root():
    """Root endpoint with system status"""
    status_file = os.path.join("data", "last_ingestion.json")
    if os.path.exists(status_file):
        with open(status_file, "r", encoding="utf-8") as f:
            status_data = json.load(f)
    else:
        status_data = {
            "last_run": None,
            "summary": {},
            "total_records": 0,
            "errors": {}
        }
    
    # Add database statistics if MongoDB is available
    database_stats = {}
    if USE_MONGODB:
        try:
            database_stats = await get_collection_stats()
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
    
    return {
        "status": "CTI-NLP backend running with real-time ingestion",
        "database_mode": "mongodb" if USE_MONGODB else "file_based",
        "ingestion_status": status_data,
        "database_stats": database_stats
    }

@app.get("/feed")
async def get_feed(limit: int = 20):
    """Get latest threat intelligence feed"""
    if USE_MONGODB:
        try:
            # Get from MongoDB
            threats = await ThreatIntelligence.find_all().sort([("timestamp", -1)]).limit(limit).to_list(None)
            return [
                {
                    "id": str(threat.id),
                    "text": threat.text,
                    "source": threat.source,
                    "timestamp": threat.timestamp.isoformat(),
                    "threat_category": threat.threat_category,
                    "severity_level": threat.severity_level,
                    "processed": threat.processed
                }
                for threat in threats
            ]
        except Exception as e:
            logger.error(f"Failed to get feed from MongoDB: {e}")
            # Fallback to file-based
    
    # File-based fallback
    file_path = os.path.join("data", "ingested_cti.jsonl")
    if not os.path.exists(file_path):
        return []

    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except:
                continue

    # Return latest first
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return entries[:limit]

# -------------------
# Trigger ingestion manually
# -------------------
@app.post("/ingest_now")
async def ingest_now():
    """Manually trigger data ingestion"""
    try:
        logger.info("Manual ingestion triggered")
        await asyncio.create_task(asyncio.to_thread(ingest_all_sources_main))
        
        # Return updated stats
        status_file = os.path.join("data", "last_ingestion.json")
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)
        else:
            status_data = {"message": "Ingestion completed but no status file found"}
        
        return {
            "status": "success",
            "message": "Manual ingestion completed",
            "ingestion_result": status_data
        }
    except Exception as e:
        logger.error(f"Manual ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# -------------------
# Model information endpoint
# -------------------
@app.get("/models/info")
async def get_model_information():
    """Get information about loaded models"""
    try:
        if ENHANCED_ANALYZER_AVAILABLE:
            model_info = get_model_info()
            return {
                "enhanced_available": True,
                "models": model_info,
                "capabilities": {
                    "improved_classification": model_info.get("improved_classifier", False),
                    "comprehensive_analysis": True,
                    "basic_classification": True,
                    "severity_prediction": True,
                    "entity_extraction": True
                }
            }
        else:
            return {
                "enhanced_available": False,
                "capabilities": {
                    "basic_classification": True,
                    "severity_prediction": True,
                    "entity_extraction": True,
                    "improved_classification": False,
                    "comprehensive_analysis": False
                }
            }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return {"error": str(e)}

# -------------------
# Dashboard endpoint
# -------------------
@app.get("/dashboard")
def serve_dashboard(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "database_mode": "mongodb" if USE_MONGODB else "file_based"
    })

# -------------------
# API Endpoints
# -------------------

@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    if USE_MONGODB:
        try:
            # Get MongoDB statistics
            total_threats = await ThreatIntelligence.count()
            
            # Aggregate by category
            category_pipeline = [
                {"$group": {"_id": "$threat_category", "count": {"$sum": 1}}}
            ]
            category_results = await ThreatIntelligence.aggregate(category_pipeline).to_list(None)
            threats_by_category = {result["_id"]: result["count"] for result in category_results if result["_id"]}
            
            # Aggregate by severity
            severity_pipeline = [
                {"$group": {"_id": "$severity_level", "count": {"$sum": 1}}}
            ]
            severity_results = await ThreatIntelligence.aggregate(severity_pipeline).to_list(None)
            threats_by_severity = {result["_id"]: result["count"] for result in severity_results if result["_id"]}
            
            # Aggregate by source
            source_pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}}
            ]
            source_results = await ThreatIntelligence.aggregate(source_pipeline).to_list(None)
            threats_by_source = {result["_id"]: result["count"] for result in source_results if result["_id"]}
            
            # Get recent threats
            recent_threats = await ThreatIntelligence.find_all().sort([("timestamp", -1)]).limit(10).to_list(None)
            recent_threats_data = [
                ThreatIntelResponse(
                    id=str(threat.id),
                    text=threat.text[:200] + "..." if len(threat.text) > 200 else threat.text,
                    source=threat.source,
                    timestamp=threat.timestamp,
                    threat_category=threat.threat_category,
                    severity_level=threat.severity_level,
                    confidence_score=threat.confidence_score,
                    processed=threat.processed
                ).dict()
                for threat in recent_threats
            ]
            
            # Get top entities
            entity_pipeline = [
                {"$group": {"_id": "$entity_text", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            entity_results = await ExtractedEntity.aggregate(entity_pipeline).to_list(None)
            top_entities = [{"entity": result["_id"], "count": result["count"]} for result in entity_results]
            
            return DashboardStats(
                total_threats=total_threats,
                threats_by_category=threats_by_category,
                threats_by_severity=threats_by_severity,
                threats_by_source=threats_by_source,
                recent_threats=recent_threats_data,
                top_entities=top_entities,
                processing_stats={"database_mode": "mongodb"}
            ).dict()
            
        except Exception as e:
            logger.error(f"Failed to get MongoDB stats: {e}")
    
    # File-based fallback
    try:
        file_path = os.path.join("data", "ingested_cti.jsonl")
        if not os.path.exists(file_path):
            return DashboardStats(
                total_threats=0,
                threats_by_category={},
                threats_by_severity={},
                threats_by_source={},
                recent_threats=[],
                top_entities=[],
                processing_stats={"database_mode": "file_based", "data_file": "not_found"}
            ).dict()
        
        threats = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    threats.append(json.loads(line.strip()))
                except:
                    continue
        
        # Basic statistics from file data
        total_threats = len(threats)
        threats_by_source = {}
        recent_threats = sorted(threats, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        for threat in threats:
            source = threat.get("source", "unknown")
            threats_by_source[source] = threats_by_source.get(source, 0) + 1
        
        return DashboardStats(
            total_threats=total_threats,
            threats_by_category={},
            threats_by_severity={},
            threats_by_source=threats_by_source,
            recent_threats=[
                ThreatIntelResponse(
                    id=str(i),
                    text=threat.get("text", "")[:200] + "..." if len(threat.get("text", "")) > 200 else threat.get("text", ""),
                    source=threat.get("source", "unknown"),
                    timestamp=datetime.fromisoformat(threat.get("timestamp", datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                    processed=False
                ).dict()
                for i, threat in enumerate(recent_threats)
            ],
            top_entities=[],
            processing_stats={"database_mode": "file_based", "total_file_records": total_threats}
        ).dict()
        
    except Exception as e:
        logger.error(f"Failed to get file-based stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.post("/api/analyze")
async def analyze_threat_text(request: ThreatAnalysisRequest):
    """Analyze threat text using available models"""
    try:
        text = request.text
        source = request.source or DataSource.MANUAL
        
        start_time = datetime.utcnow()
        analysis_results = {}
        
        # Enhanced analysis if available
        if ENHANCED_ANALYZER_AVAILABLE:
            try:
                enhanced_result = analyze_threat_comprehensive(text)
                analysis_results["enhanced"] = enhanced_result
            except Exception as e:
                logger.error(f"Enhanced analysis failed: {e}")
        
        # Basic classification
        try:
            classification_result = classify_threat(text)
            analysis_results["classification"] = classification_result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            classification_result = {"category": "Other", "confidence": 0.0}
        
        # Severity prediction
        try:
            severity_result = predict_severity(text)
            analysis_results["severity"] = severity_result
        except Exception as e:
            logger.error(f"Severity prediction failed: {e}")
            severity_result = {"severity": "Medium", "confidence": 0.0}
        
        # Entity extraction
        try:
            entities_result = extract_threat_entities(text)
            analysis_results["entities"] = entities_result
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            entities_result = []
        
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Initialize storage counters
        threat_id = None
        entities_stored = 0
        analysis_results_stored = 0
        
        # Store in MongoDB if available
        if USE_MONGODB:
            try:
                # Map classification result to enum
                try:
                    threat_category = ThreatCategory(classification_result.get("category", "Other"))
                except ValueError:
                    threat_category = ThreatCategory.OTHER
                
                # Map severity result to enum
                try:
                    severity_level = SeverityLevel(severity_result.get("severity", "Medium"))
                except ValueError:
                    severity_level = SeverityLevel.MEDIUM
                
                threat_doc = ThreatIntelligence(
                    text=text,
                    source=source,
                    timestamp=start_time,
                    threat_category=threat_category,
                    severity_level=severity_level,
                    confidence_score=classification_result.get("confidence", 0.0),
                    processed=True,
                    processing_timestamp=end_time,
                    analysis_details=analysis_results
                )
                
                await threat_doc.insert()
                threat_id = str(threat_doc.id)
                
                # Store entities if any
                entities_stored = 0
                if entities_result:
                    for entity in entities_result:
                        try:
                            # Map entity type to enum
                            entity_type = entity.get("label", "MISC")
                            if entity_type not in ["PERSON", "ORG", "LOC", "MISC"]:
                                entity_type = "MISC"
                            
                            entity_doc = ExtractedEntity(
                                threat_id=threat_id,
                                entity_text=entity.get("text", ""),
                                entity_type=entity_type,
                                confidence_score=entity.get("confidence", 0.0),
                                start_position=entity.get("start"),
                                end_position=entity.get("end")
                            )
                            await entity_doc.insert()
                            entities_stored += 1
                        except Exception as e:
                            logger.error(f"Failed to store entity: {e}")
                
                # Store detailed analysis results
                analysis_results_stored = 0
                for analysis_type, result_data in analysis_results.items():
                    try:
                        analysis_result = AnalysisResult(
                            threat_id=threat_id,
                            analysis_type=analysis_type,
                            result=result_data,
                            confidence=result_data.get("confidence", 0.0) if isinstance(result_data, dict) else 0.0,
                            model_version="1.0",
                            processing_time_ms=processing_time_ms,
                            timestamp=end_time
                        )
                        await analysis_result.insert()
                        analysis_results_stored += 1
                    except Exception as e:
                        logger.error(f"Failed to store analysis result for {analysis_type}: {e}")
                
                logger.info(f"Analysis stored in MongoDB - Threat: {threat_id}, Entities: {entities_stored}, Analysis: {analysis_results_stored}")
                
            except Exception as e:
                logger.error(f"Failed to store analysis in MongoDB: {e}")
                threat_id = None
        
        # Return comprehensive analysis
        return {
            "threat_id": threat_id if USE_MONGODB else None,
            "threat_category": classification_result.get("category", "Other"),
            "severity_level": severity_result.get("severity", "Medium"),
            "confidence_score": classification_result.get("confidence", 0.0),
            "entities": entities_result,
            "analysis_details": analysis_results,
            "processing_time_ms": processing_time_ms,
            "database_stored": USE_MONGODB,
            "entities_stored": entities_stored if USE_MONGODB else 0,
            "analysis_results_stored": analysis_results_stored if USE_MONGODB else 0
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/bulk_analyze")
async def bulk_analyze_threats(file: UploadFile = File(...)):
    """Bulk analyze threats from uploaded CSV file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Read CSV file
        df = pd.read_csv(tmp_file_path)
        
        # Find text column
        text_columns = ['text', 'Text', 'content', 'Content', 'description', 'Description']
        text_column = None
        for col in text_columns:
            if col in df.columns:
                text_column = col
                break
        
        if not text_column:
            raise HTTPException(status_code=400, detail="No text column found in CSV file")
        
        results = []
        processed = 0
        
        for index, row in df.iterrows():
            try:
                text = str(row[text_column]).strip()
                if not text or len(text) < 10:
                    continue
                
                # Analyze each text
                request = ThreatAnalysisRequest(text=text, source=DataSource.CSV_UPLOAD)
                result = await analyze_threat_text(request)
                
                results.append({
                    "row": index + 1,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "analysis": result
                })
                
                processed += 1
                
                # Limit processing to avoid timeout
                if processed >= 100:
                    break
                    
            except Exception as e:
                logger.error(f"Failed to analyze row {index + 1}: {e}")
                continue
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "status": "success",
            "total_processed": processed,
            "total_rows": len(df),
            "results": results,
            "database_mode": "mongodb" if USE_MONGODB else "file_based"
        }
        
    except Exception as e:
        logger.error(f"Bulk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")

# -------------------
# Database management endpoints
# -------------------

@app.post("/api/migrate_to_mongodb")
async def trigger_migration():
    """Trigger data migration from files to MongoDB"""
    if not USE_MONGODB:
        raise HTTPException(status_code=503, detail="MongoDB not available")
    
    try:
        # Import and run migration
        from scripts.migrate_to_mongodb import DataMigrator
        
        migrator = DataMigrator()
        success = await migrator.migrate_all()
        
        if success:
            return {
                "status": "success",
                "message": "Data migration completed successfully",
                "stats": migrator.stats
            }
        else:
            return {
                "status": "error",
                "message": "Data migration failed",
                "errors": migrator.stats.get("errors", [])
            }
            
    except Exception as e:
        logger.error(f"Migration trigger failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.get("/api/database_stats")
async def get_database_statistics():
    """Get detailed database statistics"""
    if USE_MONGODB:
        try:
            stats = await get_collection_stats()
            health = await mongodb_config.health_check()
            
            return {
                "database_type": "mongodb",
                "connection_status": health["status"],
                "database_info": health,
                "collection_stats": stats
            }
        except Exception as e:
            logger.error(f"Failed to get MongoDB stats: {e}")
            return {"database_type": "mongodb", "error": str(e)}
    else:
        # File-based statistics
        file_stats = {}
        data_dir = Path("data")
        
        if data_dir.exists():
            for file_path in data_dir.glob("*.jsonl"):
                try:
                    with open(file_path, 'r') as f:
                        count = sum(1 for line in f if line.strip())
                    file_stats[file_path.name] = count
                except:
                    file_stats[file_path.name] = "error"
        
        return {
            "database_type": "file_based",
            "file_stats": file_stats
        }

@app.get("/analytics")
async def get_analytics(days: int = 30):
    """Get analytics data for the specified number of days"""
    try:
        if USE_MONGODB:
            # Calculate date range
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get total threats in date range
            total_threats = await ThreatIntelligence.find(
                ThreatIntelligence.timestamp >= start_date,
                ThreatIntelligence.timestamp <= end_date
            ).count()
            
            # Get threats by category
            category_pipeline = [
                {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {"_id": "$threat_category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            category_results = await ThreatIntelligence.aggregate(category_pipeline).to_list(None)
            threats_by_category = {}
            for result in category_results:
                category = result.get("_id")
                if category:
                    threats_by_category[str(category)] = result.get("count", 0)
            
            # Get threats by severity
            severity_pipeline = [
                {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {"_id": "$severity_level", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            severity_results = await ThreatIntelligence.aggregate(severity_pipeline).to_list(None)
            threats_by_severity = {}
            for result in severity_results:
                severity = result.get("_id")
                if severity:
                    threats_by_severity[str(severity)] = result.get("count", 0)
            
            # Get threats by source
            source_pipeline = [
                {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            source_results = await ThreatIntelligence.aggregate(source_pipeline).to_list(None)
            threats_by_source = {}
            for result in source_results:
                source = result.get("_id")
                if source:
                    threats_by_source[str(source)] = result.get("count", 0)
            
            # Get timeline data (threats per day)
            timeline_pipeline = [
                {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            timeline_results = await ThreatIntelligence.aggregate(timeline_pipeline).to_list(None)
            threats_timeline = [
                {"date": result["_id"], "count": result["count"]}
                for result in timeline_results
            ]
            
            # Get recent threats
            recent_threats = await ThreatIntelligence.find(
                ThreatIntelligence.timestamp >= start_date,
                ThreatIntelligence.timestamp <= end_date
            ).sort([("timestamp", -1)]).limit(10).to_list(None)
            
            recent_threats_data = []
            for threat in recent_threats:
                recent_threats_data.append({
                    "id": str(threat.id),
                    "text": threat.text[:100] + "..." if len(threat.text) > 100 else threat.text,
                    "source": str(threat.source),
                    "timestamp": threat.timestamp.isoformat(),
                    "threat_category": str(threat.threat_category) if threat.threat_category else None,
                    "severity_level": str(threat.severity_level) if threat.severity_level else None,
                    "processed": threat.processed
                })
            
            # Get top entities
            top_entities = []
            try:
                entity_pipeline = [
                    {"$group": {"_id": "$entity_text", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                entity_results = await ExtractedEntity.aggregate(entity_pipeline).to_list(None)
                top_entities = [
                    {"entity": result["_id"], "count": result["count"]}
                    for result in entity_results
                ]
            except Exception as e:
                logger.error(f"Failed to get entities: {e}")
                top_entities = []
            
            return {
                "total_threats": total_threats,
                "threats_by_category": threats_by_category,
                "threats_by_severity": threats_by_severity,
                "threats_by_source": threats_by_source,
                "threats_timeline": threats_timeline,
                "recent_threats": recent_threats_data,
                "top_entities": top_entities,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                },
                "database_mode": "mongodb"
            }
            
        else:
            # File-based fallback with mock analytics data
            return {
                "total_threats": 0,
                "threats_by_category": {},
                "threats_by_severity": {},
                "threats_by_source": {},
                "threats_timeline": [],
                "recent_threats": [],
                "top_entities": [],
                "date_range": {
                    "start": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                    "end": datetime.utcnow().isoformat(),
                    "days": days
                },
                "database_mode": "file_based"
            }
            
    except Exception as e:
        logger.error(f"Failed to get analytics data: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

# Additional API endpoints for dashboard sub-pages

@app.get("/api/threats")
async def get_threats(page: int = 1, limit: int = 20, category: str = None, severity: str = None, source: str = None):
    """Get paginated list of threats with filtering"""
    try:
        skip = (page - 1) * limit
        
        if USE_MONGODB:
            # Build filter query
            filter_query = {}
            if category:
                filter_query["threat_category"] = category
            if severity:
                filter_query["severity_level"] = severity
            if source:
                filter_query["source"] = source
            
            # Get threats with filters
            threats = await ThreatIntelligence.find(filter_query).skip(skip).limit(limit).sort([("timestamp", -1)]).to_list(None)
            total_count = await ThreatIntelligence.find(filter_query).count()
            
            threats_data = []
            for threat in threats:
                threats_data.append({
                    "id": str(threat.id),
                    "text": threat.text,
                    "source": str(threat.source),
                    "timestamp": threat.timestamp.isoformat(),
                    "threat_category": str(threat.threat_category) if threat.threat_category else None,
                    "severity_level": str(threat.severity_level) if threat.severity_level else None,
                    "confidence_score": threat.confidence_score,
                    "processed": threat.processed
                })
            
            return {
                "threats": threats_data,
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit
            }
        
        else:
            # File-based fallback
            return {
                "threats": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
                "message": "MongoDB not available"
            }
            
    except Exception as e:
        logger.error(f"Failed to get threats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get threats: {str(e)}")

@app.get("/api/threat/{threat_id}")
async def get_threat_details(threat_id: str):
    """Get detailed information about a specific threat"""
    try:
        if USE_MONGODB:
            threat = await ThreatIntelligence.get(threat_id)
            if not threat:
                raise HTTPException(status_code=404, detail="Threat not found")
            
            # Get associated entities
            entities = await ExtractedEntity.find(ExtractedEntity.threat_id == threat_id).to_list(None)
            
            # Get analysis results
            analysis_results = await AnalysisResult.find(AnalysisResult.threat_id == threat_id).to_list()
            
            return {
                "threat": {
                    "id": str(threat.id),
                    "text": threat.text,
                    "source": str(threat.source),
                    "timestamp": threat.timestamp.isoformat(),
                    "threat_category": str(threat.threat_category) if threat.threat_category else None,
                    "severity_level": str(threat.severity_level) if threat.severity_level else None,
                    "confidence_score": threat.confidence_score,
                    "processed": threat.processed,
                    "processing_timestamp": threat.processing_timestamp.isoformat() if threat.processing_timestamp else None,
                    "analysis_details": threat.analysis_details
                },
                "entities": [
                    {
                        "id": str(entity.id),
                        "text": entity.entity_text,
                        "type": str(entity.entity_type),
                        "confidence": entity.confidence_score,
                        "start": entity.start_position,
                        "end": entity.end_position
                    }
                    for entity in entities
                ],
                "analysis_results": [
                    {
                        "id": str(result.id),
                        "type": result.analysis_type,
                        "result": result.result,
                        "confidence": result.confidence,
                        "model_version": result.model_version,
                        "processing_time_ms": result.processing_time_ms,
                        "timestamp": result.timestamp.isoformat()
                    }
                    for result in analysis_results
                ]
            }
        else:
            raise HTTPException(status_code=503, detail="MongoDB not available")
            
    except Exception as e:
        logger.error(f"Failed to get threat details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get threat details: {str(e)}")

@app.get("/api/entities")
async def get_entities(limit: int = 50):
    """Get extracted entities with counts"""
    try:
        if USE_MONGODB:
            # Get top entities
            entity_pipeline = [
                {"$group": {"_id": {"text": "$entity_text", "type": "$entity_type"}, "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            entity_results = await ExtractedEntity.aggregate(entity_pipeline).to_list(None)
            
            entities = []
            for result in entity_results:
                entities.append({
                    "text": result["_id"]["text"],
                    "type": result["_id"]["type"],
                    "count": result["count"]
                })
            
            return {"entities": entities}
        else:
            return {"entities": []}
            
    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")

@app.get("/api/sources")
async def get_data_sources():
    """Get information about data sources"""
    try:
        if USE_MONGODB:
            # Get source statistics
            source_pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}, "last_update": {"$max": "$timestamp"}}},
                {"$sort": {"count": -1}}
            ]
            source_results = await ThreatIntelligence.aggregate(source_pipeline).to_list(None)
            
            sources = []
            for result in source_results:
                sources.append({
                    "source": str(result["_id"]),
                    "count": result["count"],
                    "last_update": result["last_update"].isoformat() if result["last_update"] else None,
                    "status": "active"
                })
            
            # Get ingestion logs
            recent_logs = await DataIngestionLog.find_all().sort([("start_time", -1)]).limit(10).to_list()
            
            logs = []
            for log in recent_logs:
                logs.append({
                    "id": str(log.id),
                    "source": str(log.source),
                    "type": log.ingestion_type,
                    "records_processed": log.records_processed,
                    "records_successful": log.records_successful,
                    "records_failed": log.records_failed,
                    "start_time": log.start_time.isoformat(),
                    "end_time": log.end_time.isoformat() if log.end_time else None,
                    "duration_seconds": log.duration_seconds,
                    "errors": log.errors[:5]  # Limit errors shown
                })
            
            return {
                "sources": sources,
                "recent_logs": logs,
                "total_records": sum(source["count"] for source in sources)
            }
        else:
            return {
                "sources": [],
                "recent_logs": [],
                "total_records": 0
            }
            
    except Exception as e:
        logger.error(f"Failed to get data sources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")

@app.post("/api/ingest")
async def trigger_data_ingestion():
    """Trigger manual data ingestion and store results in MongoDB"""
    try:
        start_time = datetime.utcnow()
        
        # Trigger ingestion
        logger.info("Manual data ingestion triggered via API")
        await asyncio.create_task(asyncio.to_thread(ingest_all_sources_main))
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Read the ingestion status
        status_file = os.path.join("data", "last_ingestion.json")
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)
        else:
            status_data = {"summary": {}, "total_records": 0, "errors": {}}
        
        # Store ingestion log in MongoDB if available
        if USE_MONGODB:
            try:
                ingestion_log = DataIngestionLog(
                    source=DataSource.MANUAL,
                    ingestion_type="api_triggered",
                    records_processed=status_data.get("total_records", 0),
                    records_successful=status_data.get("total_records", 0),
                    records_failed=0,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration,
                    summary=status_data,
                    errors=list(status_data.get("errors", {}).values()) if isinstance(status_data.get("errors"), dict) else []
                )
                await ingestion_log.insert()
                logger.info(f"Ingestion log stored in MongoDB: {ingestion_log.id}")
            except Exception as e:
                logger.error(f"Failed to store ingestion log: {e}")
        
        return {
            "status": "success",
            "message": "Data ingestion completed",
            "duration_seconds": duration,
            "ingestion_result": status_data,
            "stored_in_db": USE_MONGODB
        }
        
    except Exception as e:
        logger.error(f"Manual data ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)