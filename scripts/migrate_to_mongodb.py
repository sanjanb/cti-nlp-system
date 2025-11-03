"""
Data Migration Script for CTI-NLP System
Migrates existing data from JSON/CSV files to MongoDB
"""

import asyncio
import json
import csv
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database import (
    startup_mongodb,
    shutdown_mongodb,
    ThreatIntelligence,
    DataSource,
    ThreatCategory,
    SeverityLevel,
    DataIngestionLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigrator:
    """Handles migration of existing data to MongoDB"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.stats = {
            "total_migrated": 0,
            "sources": {},
            "errors": []
        }
    
    async def migrate_all(self):
        """Migrate all data sources to MongoDB"""
        logger.info("Starting data migration to MongoDB...")
        
        # Connect to MongoDB
        success = await startup_mongodb()
        if not success:
            logger.error("Failed to connect to MongoDB. Cannot proceed with migration.")
            return False
        
        try:
            # Migrate ingested CTI data
            await self.migrate_ingested_cti()
            
            # Migrate CSV datasets
            await self.migrate_csv_datasets()
            
            # Create migration log
            await self.log_migration()
            
            logger.info(f"Migration completed successfully. Total records: {self.stats['total_migrated']}")
            logger.info(f"Sources migrated: {self.stats['sources']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.stats["errors"].append(str(e))
            return False
        
        finally:
            await shutdown_mongodb()
    
    async def migrate_ingested_cti(self):
        """Migrate data from ingested_cti.jsonl"""
        file_path = self.data_dir / "ingested_cti.jsonl"
        
        if not file_path.exists():
            logger.warning(f"File {file_path} not found, skipping...")
            return
        
        logger.info(f"Migrating data from {file_path}...")
        
        count = 0
        source_counts = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line.strip())
                    
                    # Map source to enum
                    source_str = data.get('source', 'manual')
                    source = self._map_source(source_str)
                    
                    # Parse timestamp
                    timestamp = self._parse_timestamp(data.get('timestamp'))
                    
                    # Create ThreatIntelligence document
                    threat_doc = ThreatIntelligence(
                        text=data.get('text', ''),
                        source=source,
                        timestamp=timestamp,
                        processed=False,
                        analysis_details={
                            "original_data": data,
                            "migration_source": "ingested_cti.jsonl",
                            "migration_line": line_num
                        }
                    )
                    
                    # Save to MongoDB
                    await threat_doc.insert()
                    
                    count += 1
                    source_counts[source] = source_counts.get(source, 0) + 1
                    
                    if count % 100 == 0:
                        logger.info(f"Migrated {count} records from ingested_cti.jsonl...")
                
                except Exception as e:
                    error_msg = f"Error processing line {line_num} in ingested_cti.jsonl: {str(e)}"
                    logger.error(error_msg)
                    self.stats["errors"].append(error_msg)
        
        logger.info(f"Completed migration of {count} records from ingested_cti.jsonl")
        self.stats["total_migrated"] += count
        self.stats["sources"]["ingested_cti"] = source_counts
    
    async def migrate_csv_datasets(self):
        """Migrate data from CSV files"""
        csv_files = [
            "cyber-threat-intelligence_all.csv",
            "Cybersecurity_Dataset.csv",
            "cyber-threat-intelligence-splited_train.csv",
            "cyber-threat-intelligence-splited_test.csv",
            "cyber-threat-intelligence-splited_validate.csv"
        ]
        
        for csv_file in csv_files:
            await self.migrate_csv_file(csv_file)
    
    async def migrate_csv_file(self, filename: str):
        """Migrate data from a specific CSV file"""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File {file_path} not found, skipping...")
            return
        
        logger.info(f"Migrating data from {filename}...")
        
        try:
            # Read CSV with pandas for better handling
            df = pd.read_csv(file_path)
            
            if df.empty:
                logger.warning(f"CSV file {filename} is empty")
                return
            
            count = 0
            
            for index, row in df.iterrows():
                try:
                    # Extract text (try common column names)
                    text = self._extract_text_from_row(row)
                    if not text:
                        continue
                    
                    # Extract category if available
                    category = self._extract_category_from_row(row)
                    
                    # Extract severity if available
                    severity = self._extract_severity_from_row(row)
                    
                    # Create ThreatIntelligence document
                    threat_doc = ThreatIntelligence(
                        text=text,
                        source=DataSource.CSV_UPLOAD,
                        timestamp=datetime.utcnow(),
                        threat_category=category,
                        severity_level=severity,
                        processed=category is not None or severity is not None,
                        analysis_details={
                            "original_row": row.to_dict(),
                            "migration_source": filename,
                            "migration_row": index + 1
                        }
                    )
                    
                    # Save to MongoDB
                    await threat_doc.insert()
                    count += 1
                    
                    if count % 500 == 0:
                        logger.info(f"Migrated {count} records from {filename}...")
                
                except Exception as e:
                    error_msg = f"Error processing row {index + 1} in {filename}: {str(e)}"
                    logger.error(error_msg)
                    self.stats["errors"].append(error_msg)
            
            logger.info(f"Completed migration of {count} records from {filename}")
            self.stats["total_migrated"] += count
            self.stats["sources"][filename] = count
        
        except Exception as e:
            error_msg = f"Error reading CSV file {filename}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    def _map_source(self, source_str: str) -> DataSource:
        """Map source string to DataSource enum"""
        source_mapping = {
            "twitter": DataSource.TWITTER,
            "darkweb": DataSource.DARKWEB,
            "mitre_attack": DataSource.MITRE_ATTACK,
            "manual": DataSource.MANUAL,
            "csv": DataSource.CSV_UPLOAD
        }
        return source_mapping.get(source_str.lower(), DataSource.MANUAL)
    
    def _parse_timestamp(self, timestamp_str) -> datetime:
        """Parse timestamp string to datetime"""
        if not timestamp_str:
            return datetime.utcnow()
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except:
                return datetime.utcnow()
    
    def _extract_text_from_row(self, row) -> str:
        """Extract text content from CSV row"""
        text_columns = ['text', 'Text', 'content', 'Content', 'description', 'Description', 'message', 'Message']
        
        for col in text_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # If no standard text column, use the first non-null string column
        for col, value in row.items():
            if pd.notna(value) and isinstance(value, str) and len(str(value).strip()) > 10:
                return str(value).strip()
        
        return ""
    
    def _extract_category_from_row(self, row) -> ThreatCategory:
        """Extract threat category from CSV row"""
        category_columns = ['category', 'Category', 'threat_type', 'ThreatType', 'class', 'Class', 'label', 'Label']
        
        category_mapping = {
            'malware': ThreatCategory.MALWARE,
            'phishing': ThreatCategory.PHISHING,
            'ransomware': ThreatCategory.RANSOMWARE,
            'ddos': ThreatCategory.DDOS,
            'other': ThreatCategory.OTHER
        }
        
        for col in category_columns:
            if col in row and pd.notna(row[col]):
                value = str(row[col]).lower().strip()
                for key, category in category_mapping.items():
                    if key in value:
                        return category
        
        return None
    
    def _extract_severity_from_row(self, row) -> SeverityLevel:
        """Extract severity level from CSV row"""
        severity_columns = ['severity', 'Severity', 'level', 'Level', 'priority', 'Priority']
        
        severity_mapping = {
            'very low': SeverityLevel.VERY_LOW,
            'low': SeverityLevel.LOW,
            'medium': SeverityLevel.MEDIUM,
            'high': SeverityLevel.HIGH,
            'critical': SeverityLevel.CRITICAL
        }
        
        for col in severity_columns:
            if col in row and pd.notna(row[col]):
                value = str(row[col]).lower().strip()
                for key, severity in severity_mapping.items():
                    if key in value:
                        return severity
        
        return None
    
    async def log_migration(self):
        """Log the migration activity"""
        migration_log = DataIngestionLog(
            source=DataSource.MANUAL,
            ingestion_type="migration",
            records_processed=self.stats["total_migrated"],
            records_successful=self.stats["total_migrated"],
            records_failed=len(self.stats["errors"]),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            summary=self.stats,
            errors=self.stats["errors"][:100]  # Limit errors to first 100
        )
        
        await migration_log.insert()
        logger.info("Migration log saved to database")

async def main():
    """Main migration function"""
    print("🔄 Starting data migration to MongoDB...")
    
    migrator = DataMigrator()
    success = await migrator.migrate_all()
    
    if success:
        print("✅ Data migration completed successfully!")
        print(f"📊 Total records migrated: {migrator.stats['total_migrated']}")
        print(f"📁 Sources: {migrator.stats['sources']}")
    else:
        print("❌ Data migration failed!")
        print(f"🚫 Errors: {migrator.stats['errors']}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the migration
    exit_code = asyncio.run(main())