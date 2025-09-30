from fastapi import FastAPI, HTTPException
from pymongo import MongoClient, DESCENDING
from datetime import datetime
from pydantic import BaseModel
from fastapi.responses import Response
import os

app = FastAPI()

# Use environment variables for database configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_USER = os.getenv('MONGO_USER', 'root')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'g74QKVXi5T85VoMNfSM44C8KDhdIm7Fi2DzIcsOtxB7CpyJpQCJCwVzPJ7POLiMH')
DB_NAME = os.getenv('DB_NAME', 'default')
COLLECTION_NAME = 'sensor_data'

# Construct MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"

class SensorData(BaseModel):
    temperature: float
    humidity: float
    device_id: str = "sensor_001"

def get_db_connection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

@app.post("/data")
async def receive_data(data: SensorData):
    try:
        db = get_db_connection()
        collection = db[COLLECTION_NAME]
        
        document = {
            "temp": data.temperature,
            "humidity": data.humidity,
            "device_id": data.device_id,
            "timestamp": datetime.now()
        }
        
        result = collection.insert_one(document)
        
        print(f"Stored data from {data.device_id}: Temp={data.temperature}, Humidity={data.humidity}")
        
        return {
            "status": "success", 
            "message": f"Data received and stored from {data.device_id}",
            "id": str(result.inserted_id)
        }
    
    except Exception as e:
        print(f"Error storing data: {e}")
        raise HTTPException(status_code=500, detail="Error storing sensor data")

@app.get("/")
async def root():
    return {"message": "Sensor Data API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Coolify"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/download/csv")
async def download_all_data_csv():
    """Download all sensor data as CSV file"""
    try:
        db = get_db_connection()
        collection = db[COLLECTION_NAME]
        
        # Fetch all records sorted by timestamp descending
        records = list(collection.find({}).sort("timestamp", DESCENDING))
        
        if not records:
            raise HTTPException(status_code=404, detail="No data found")
        
        csv_content = "Device ID,Temperature (°C),Humidity (%),Timestamp\n"
        
        for record in records:
            formatted_time = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            csv_content += f"{record['device_id']},{record['temp']},{record['humidity']},{formatted_time}\n"
        
        filename = f"sensor_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating CSV export: {e}")
        raise HTTPException(status_code=500, detail="Error creating CSV export")

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    # Use port 8080 and get port from environment if available
    port = int(os.getenv('PORT', '8080'))
    uvicorn.run(app, host="0.0.0.0", port=port)