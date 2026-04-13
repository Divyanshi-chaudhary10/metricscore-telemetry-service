import logging
from services.dynamodb_client import get_recent_metrics

logger = logging.getLogger(__name__)

# Threshold values for different metrics
THRESHOLDS = {
    'cpu_usage': 80.0,           # Critical at 80%
    'api_latency': 1000.0,       # Critical at 1000ms
    'error_rate': 5.0,           # Critical at 5%
    'memory_usage': 85.0,        # Critical at 85%
}

def check_anomalies(metric_name, current_value):
    """
    Analyze incoming metrics for anomalies and threshold breaches.
    Returns alert status and message if anomaly is detected.
    """
    alert = None
    
    # Check if metric has a defined threshold
    if metric_name in THRESHOLDS:
        threshold = THRESHOLDS[metric_name]
        
        if current_value >= threshold:
            alert_message = (
                f'CRITICAL ALERT: {metric_name} has exceeded threshold! '
                f'Current value: {current_value}, Threshold: {threshold}'
            )
            logger.critical(alert_message)
            alert = {
                'severity': 'CRITICAL',
                'metric': metric_name,
                'message': alert_message,
                'current_value': current_value,
                'threshold': threshold
            }
    
    # Check for anomalies by comparing with recent trends
    if not alert:
        alert = check_trend_anomaly(metric_name, current_value)
    
    return alert

def check_trend_anomaly(metric_name, current_value):
    """
    Detect anomalies by comparing current value with historical trend.
    An anomaly is detected if the current value deviates significantly.
    """
    try:
        recent_metrics = get_recent_metrics(metric_name, limit=10)
        
        if len(recent_metrics) < 3:
            return None  # Not enough data for trend analysis
        
        values = [float(item.get('value', 0)) for item in recent_metrics]
        avg_value = sum(values) / len(values)
        
        # Calculate standard deviation
        variance = sum((x - avg_value) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Alert if value is more than 3 standard deviations from mean (statistical anomaly)
        if std_dev > 0 and abs(current_value - avg_value) > 3 * std_dev:
            alert_message = (
                f'ANOMALY DETECTED: {metric_name} shows unusual behavior! '
                f'Current: {current_value}, Historical avg: {avg_value:.2f}, Std Dev: {std_dev:.2f}'
            )
            logger.warning(alert_message)
            return {
                'severity': 'WARNING',
                'metric': metric_name,
                'message': alert_message,
                'current_value': current_value,
                'historical_average': avg_value,
                'standard_deviation': std_dev
            }
    except Exception as e:
        logger.error(f'Error checking trend anomaly for {metric_name}: {str(e)}')
    
    return None
