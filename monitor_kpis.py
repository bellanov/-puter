import os
import time
import logging
from google.cloud import monitoring_v3

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration for metric types
METRICS = {
    'cpu': 'compute.googleapis.com/instance/disk/write_bytes_count',  # Change to CPU metric
    'memory': 'compute.googleapis.com/instance/memory/usage',
    'disk_io': 'compute.googleapis.com/instance/disk/read_bytes_count'
}

def initialize_client():
    """Initialize the Monitoring client."""
    return monitoring_v3.MetricServiceClient()

def get_project_name():
    """Get the project name from the environment variable."""
    project_id = os.environ.get('GCP_PROJECT_ID')
    if not project_id:
        logging.error("GCP_PROJECT_ID environment variable is not set.")
        raise EnvironmentError("GCP_PROJECT_ID is not set.")
    return f"projects/{project_id}"

def fetch_time_series(client, project_name, metric_type):
    """Fetch time series data for the specified metric type."""
    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type="{metric_type}"',
                "interval": {
                    "end_time": {"seconds": int(time.time())},
                    "start_time": {"seconds": int(time.time()) - 3600},
                },
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        return list(results)  # Convert to list for easier processing
    except Exception as e:
        logging.error(f"Error fetching data for {metric_type}: {e}")
        return []

def monitor_kpis(metric_key):
    """Monitor KPIs based on the specified metric key."""
    client = initialize_client()
    project_name = get_project_name()
    metric_type = METRICS.get(metric_key)

    if not metric_type:
        logging.error(f"Metric type for key '{metric_key}' not found.")
        return {"error": f"Metric type for key '{metric_key}' not found."}

    kpi_data = fetch_time_series(client, project_name, metric_type)
    logging.info(f"Retrieved {len(kpi_data)} data points for {metric_type}")

    return {metric_type.split('/')[-1]: kpi_data}  # Return data with metric name as key

if __name__ == "__main__":
    # Example of calling one of the monitoring functions
    try:
        print(monitor_kpis('cpu'))  # Call the CPU monitoring function
        print(monitor_kpis('memory'))  # Call the Memory monitoring function
        print(monitor_kpis('disk_io'))  # Call the Disk I/O monitoring function
    except Exception as e:
        logging.error(f"Failed to monitor KPIs: {e}")