import boto3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000'),
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
)

TABLE_NAME = 'MetricsData'

def get_table():
    """Get reference to the metrics table."""
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.load()  # Check if table exists
        return table
    except Exception as e:
        logger.warning(f'Table {TABLE_NAME} may not exist yet: {str(e)}')
        return create_table()

def create_table():
    """Create the metrics table if it doesn't exist."""
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'metric_name', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'metric_name', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'N'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        logger.info(f'Table {TABLE_NAME} created successfully')
        return table
    except Exception as e:
        logger.error(f'Error creating table: {str(e)}')
        raise

def insert_metric(metric_name, value, timestamp=None):
    """Insert time-series metric data into DynamoDB."""
    if timestamp is None:
        timestamp = int(datetime.utcnow().timestamp())
    
    try:
        table = get_table()
        table.put_item(
            Item={
                'metric_name': metric_name,
                'timestamp': int(timestamp),
                'value': float(value),
                'inserted_at': int(datetime.utcnow().timestamp())
            }
        )
        logger.info(f'Metric {metric_name} inserted: value={value}')
    except Exception as e:
        logger.error(f'Error inserting metric {metric_name}: {str(e)}')
        raise

def get_recent_metrics(metric_name, limit=10):
    """Retrieve recent metrics for a given metric name."""
    try:
        table = get_table()
        response = table.query(
            KeyConditionExpression='metric_name = :name',
            ExpressionAttributeValues={':name': metric_name},
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f'Error retrieving metrics for {metric_name}: {str(e)}')
        return []
