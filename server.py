from fastapi import FastAPI, HTTPException
import mysql.connector
from datetime import datetime
from pydantic import BaseModel
from fastapi.responses import Response
import os

app = FastAPI()

# Use environment variables for database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'), 
    'password': os.getenv('DB_PASSWORD', 'root'), 
    'database': os.getenv('DB_NAME', 'testdb'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

class SensorData(BaseModel):
    temperature: float
    humidity: float
    device_id: str = "sensor_001"
    timestamp: str

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.post("/data")
async def receive_data(data: SensorData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO sensor_data (temp, humidity, device_id, timestamp) 
        VALUES (%s, %s, %s, %s)
        """
        
        values = (
            data.temperature, 
            data.humidity, 
            data.device_id,
            data.timestamp
        )
        cursor.execute(query, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Stored data from {data.device_id}: Temp={data.temperature}, Humidity={data.humidity}")
        
        return {
            "status": "success", 
            "message": f"Data received and stored from {data.device_id}"
        }
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT device_id, temp, humidity, timestamp 
        FROM sensor_data 
        ORDER BY timestamp DESC
        """
        cursor.execute(query)
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
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