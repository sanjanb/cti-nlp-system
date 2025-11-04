myenv/Scripts/activate

pip install -r requirements.txt

uvicorn backend.main_mongodb:app --host 0.0.0.0 --port 8001

