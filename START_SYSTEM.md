# How to Start the CTI-NLP System

## ⚠️ Database Connection Error Fix

If you're seeing database connection errors like:

```
connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

You have **2 options** to run the system:

## Option 1: Test Mode (Easiest - No Database Required)

**For Development and Testing:**

```powershell
# 1. Activate virtual environment
myenv\Scripts\activate

# 2. Set test mode
$env:TEST_MODE="true"

# 3. Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**What Test Mode Provides:**

- ✅ All ML models work (NER, Classification, Severity)
- ✅ Single text analysis works perfectly
- ✅ CSV batch upload works
- ✅ All API endpoints respond
- ✅ Interactive dashboard at http://localhost:8000/dashboard
- ⚠️ Data is NOT saved to database (returns mock IDs)
- ⚠️ Threat database and analytics show empty

## Option 2: Full Mode (Production-like with Database)

**For Full System with Database Persistence:**

### Step 1: Start PostgreSQL Database

```powershell
# Start PostgreSQL using Docker
docker run -d --name cti-postgres \
  -e POSTGRES_DB=cti_nlp \
  -e POSTGRES_USER=cti_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15-alpine

# Start Redis Cache
docker run -d --name cti-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Step 2: Configure Environment

Create or update `.env` file:

```env
TEST_MODE=false
DATABASE_URL=postgresql://cti_user:secure_password@localhost:5432/cti_nlp
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Step 3: Initialize Database

```powershell
# Activate environment
myenv\Scripts\activate

# Initialize database tables
python -c "
from database.database import init_database
init_database()
print('✅ Database initialized successfully')
"
```

### Step 4: Start the Server

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Option 3: Docker Compose (Complete Setup)

```powershell
# Start all services with one command
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Access at: http://localhost:8000/dashboard
```

## 🚀 Quick Start Commands

### For Testing/Development:

```powershell
myenv\Scripts\activate
$env:TEST_MODE="true"
uvicorn backend.main:app --reload
```

### For Production:

```powershell
docker-compose up -d
```

## 🌐 Access Points

- **Interactive Dashboard**: http://localhost:8000/dashboard
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Troubleshooting

### Database Connection Issues

1. **Check if PostgreSQL is running**: `docker ps | findstr postgres`
2. **Test connection**: `telnet localhost 5432`
3. **Use Test Mode**: Set `TEST_MODE=true` to bypass database

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F

# Or use different port
uvicorn backend.main:app --port 8001
```

### Model Loading Issues

```powershell
# Retrain models if missing
python scripts/train_threat_classifier.py
python scripts/train_severity_model.py

# Download spaCy model
python -m spacy download en_core_web_sm
```

## 📊 Dashboard Features

### When Database is Available:

- Real-time threat feed
- Comprehensive threat database
- Analytics and charts
- Data persistence
- Full CRUD operations

### In Test Mode:

- All ML analysis works
- CSV batch processing
- Sample data for demonstration
- Perfect for development and testing

---

**Recommendation**: Start with **Test Mode** for immediate use, then set up the full database when you need persistence.

& "D:/ATME/Major Project/cti-nlp-system/myenv/Scripts/uvicorn.exe" backend.main_mongodb:app --host 0.0.0.0 --port 8001
