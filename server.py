import os
import json
from fastmcp import FastMCP
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.credentials import Credentials

# Initialize FastMCP server
mcp = FastMCP("GA4 MCP Server")

def get_ga4_client():
    """Helper to initialize the GA4 client using OAuth 2.0 credentials from environment variables."""
    # Try to construct credentials from explicit env vars (Client ID, Secret, Refresh Token)
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
    
    if client_id and client_secret and refresh_token:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        return BetaAnalyticsDataClient(credentials=creds)
    
    # Fallback to Application Default Credentials
    return BetaAnalyticsDataClient()

@mcp.tool()
def run_report(property_id: str, start_date: str, end_date: str, metrics: list[str], dimensions: list[str] = None) -> str:
    """
    Run a customized GA4 report.
    
    Args:
        property_id: The GA4 property ID (e.g., '123456789')
        start_date: Start date in YYYY-MM-DD format, or 'today', 'yesterday', '30daysAgo'
        end_date: End date in YYYY-MM-DD format, or 'today', 'yesterday'
        metrics: List of metrics (e.g., ['activeUsers', 'screenPageViews'])
        dimensions: Optional list of dimensions (e.g., ['city', 'date'])
    """
    client = get_ga4_client()
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in (dimensions or [])],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    
    try:
        response = client.run_report(request)
    except Exception as e:
        return f"Error running report: {str(e)}"
        
    result = {
        "rows": []
    }
    
    for row in response.rows:
        row_dict = {}
        if dimensions:
            for i, dimension_value in enumerate(row.dimension_values):
                row_dict[dimensions[i]] = dimension_value.value
        for i, metric_value in enumerate(row.metric_values):
            row_dict[metrics[i]] = metric_value.value
        result["rows"].append(row_dict)
        
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()
    
    # Run the server using SSE transport
    mcp.run(transport="sse", host=args.host, port=args.port)
