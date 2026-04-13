from flask import Flask, request, jsonify
from services.dynamodb_client import insert_metric
from services.alerter import check_anomalies
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/metrics/ingest', methods=['POST'])
def ingest_metrics():
    """Endpoint to receive telemetry data."""
    try:
        data = request.get_json()
        
        if not data or 'metric_name' not in data or 'value' not in data:
            return jsonify({'error': 'Missing required fields: metric_name, value'}), 400
        
        metric_name = data.get('metric_name')
        value = data.get('value')
        timestamp = data.get('timestamp')
        
        # Insert metric into DynamoDB
        insert_metric(metric_name, value, timestamp)
        
        # Check for anomalies
        anomaly_alert = check_anomalies(metric_name, value)
        
        return jsonify({
            'status': 'success',
            'message': f'Metric {metric_name} ingested',
            'alert': anomaly_alert
        }), 200
    
    except Exception as e:
        logger.error(f'Error ingesting metric: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/metrics/health', methods=['GET'])
def health_check():
    """Endpoint to check system status."""
    return jsonify({
        'status': 'healthy',
        'service': 'MetricsCore',
        'message': 'Observability and telemetry service is running'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
