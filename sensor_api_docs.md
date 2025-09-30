# Sensor Data API Documentation

## Overview

This is a FastAPI-based REST API service designed to collect, store, and export sensor data (temperature and humidity readings) to a MySQL database. The application is containerized using Docker for easy deployment.

## Architecture

The system consists of:
- **FastAPI** web server for handling HTTP requests
- **MySQL database** for persistent data storage
- **Docker container** for isolated deployment
- Environment-based configuration for flexibility

## API Endpoints

### `POST /data`
Receives and stores sensor readings in the database.

**Request Body:**
```json
{
  "temperature": 25.5,
  "humidity": 60.2,
  "device_id": "sensor_001",
  "timestamp": "2025-09-29T14:30:00"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data received and stored from sensor_001"
}
```

### `GET /`
Root endpoint confirming the API is running.

**Response:**
```json
{
  "message": "Sensor Data API is running"
}
```

### `GET /health`
Health check endpoint for monitoring and deployment platforms (like Coolify).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T14:30:00"
}
```

### `GET /download/csv`
Downloads all sensor data as a CSV file.

**Response:**
- CSV file download with columns: Device ID, Temperature (°C), Humidity (%), Timestamp
- Filename format: `sensor_data_export_YYYYMMDD_HHMMSS.csv`
- Data sorted by timestamp (newest first)

## Database Schema

The application expects a MySQL table named `sensor_data` with the following structure:

```sql
sensor_data (
  id INT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR,
  temp FLOAT,
  humidity FLOAT,
  timestamp DATETIME
)
```

## Configuration

The application uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | MySQL host address |
| `DB_USER` | root | Database username |
| `DB_PASSWORD` | root | Database password |
| `DB_NAME` | testdb | Database name |
| `DB_PORT` | 3306 | MySQL port |
| `PORT` | 8080 | API server port |

## Docker Deployment

### Building the Image
```bash
docker build -t sensor-api .
```

### Running the Container
```bash
docker run -p 8080:8080 \
  -e DB_HOST=mysql-host \
  -e DB_USER=username \
  -e DB_PASSWORD=password \
  -e DB_NAME=sensor_db \
  sensor-api
```

## Docker Configuration Details

**Base Image:** Python 3.11 slim (lightweight)

**System Dependencies:**
- gcc compiler
- MySQL client libraries
- pkg-config

**Security Features:**
- Non-root user (`appuser`) for running the application
- Minimal system dependencies to reduce attack surface

**Port:** Exposes port 8080 by default

## Python Dependencies

- **fastapi**: Web framework for building the API
- **uvicorn**: ASGI server for running FastAPI
- **mysql-connector-python**: MySQL database driver
- **pydantic**: Data validation using Python type annotations

## Use Cases

This API is ideal for:
- IoT sensor networks collecting environmental data
- Temperature and humidity monitoring systems
- Smart home automation data logging
- Industrial sensor data collection
- Research projects requiring sensor data aggregation

## Error Handling

The API includes comprehensive error handling:
- Database connection errors return HTTP 500
- Missing data returns HTTP 404
- Invalid data format returns HTTP 422 (automatic via Pydantic)
- All errors are logged to console for debugging