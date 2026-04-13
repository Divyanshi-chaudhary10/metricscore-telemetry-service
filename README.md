# MetricsCore

A cloud-native observability and telemetry service for collecting, analyzing, and alerting on system metrics in real-time.

## Architecture

MetricsCore is built with a microservices-ready architecture that provides:

- **Flask REST API**: Lightweight, scalable HTTP endpoints for metric ingestion and health checks
- **DynamoDB Time-Series Storage**: Persistent storage of metrics with partition keys (metric_name) and sort keys (timestamp) for efficient time-series queries
- **Automated Alerting System**: Dual-layer anomaly detection combining threshold-based and statistical trend analysis

## Key Features

### Time-Series Data Storage

The system uses **DynamoDB with a composite key structure**:
- **Partition Key (HASH)**: `metric_name` - Groups metrics by type (e.g., cpu_usage, api_latency)
- **Sort Key (RANGE)**: `timestamp` - Enables efficient time-range queries and maintains temporal ordering

This structure enables:
- Fast lookups by metric type
- Efficient time-range scans
- Natural support for TTL-based data expiration
- Seamless scalability to millions of data points

### Automated Alerting

The alerter operates on two levels:

1. **Threshold-Based Alerts**: Immediate alerts when metrics exceed predefined critical thresholds
   - CPU Usage > 80%
   - API Latency > 1000ms
   - Error Rate > 5%
   - Memory Usage > 85%

2. **Statistical Anomaly Detection**: Analyzes metric trends and detects abnormal deviations
   - Calculates rolling average and standard deviation
   - Flags values deviating >3 standard deviations from the mean
   - Prevents false positives from gradual trend changes

## API Endpoints

### POST `/metrics/ingest`

Ingest telemetry data into the system.

**Request:**
```json
{
  "metric_name": "cpu_usage",
  "value": 75.5,
  "timestamp": 1712973600
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Metric cpu_usage ingested",
  "alert": null
}
```

### GET `/metrics/health`

Check the health status of the MetricsCore service.

**Response:**
```json
{
  "status": "healthy",
  "service": "MetricsCore",
  "message": "Observability and telemetry service is running"
}
```

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **MetricsCore Flask API** on `http://localhost:5000`
- **DynamoDB Local** on `http://localhost:8000` (in-memory, no AWS account required)

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
export DYNAMODB_ENDPOINT=http://localhost:8000
export AWS_REGION=us-east-1

# Run Flask app
flask --app app.main run
```

## Usage Example

### Ingest a Metric

```bash
curl -X POST http://localhost:5000/metrics/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "value": 85.2
  }'
```

### Check Health

```bash
curl http://localhost:5000/metrics/health
```

## Technology Stack

- **Flask**: Lightweight web framework for REST API
- **Boto3**: AWS SDK for DynamoDB integration
- **Amazon DynamoDB Local**: Local development simulation of DynamoDB
- **Gunicorn**: Production-ready WSGI server
- **Python Dotenv**: Environment variable management

## Future Enhancements

- Multi-region DynamoDB replication
- CloudWatch integration for AWS deployments
- Advanced ML-based anomaly detection
- Grafana/Prometheus integration for visualization
- Custom alerting thresholds via API
- Webhook notifications for critical alerts
