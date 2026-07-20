import os
import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastmcp import FastMCP
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configuration
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

app = FastAPI(title="GA4 MCP Server with OAuth")
mcp = FastMCP("GA4 MCP Server")

def get_flow():
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"{BASE_URL}/oauth2callback"]
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=f"{BASE_URL}/oauth2callback"
    )

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                creds_data = json.load(f)
                return Credentials(
                    token=creds_data.get("token"),
                    refresh_token=creds_data.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    scopes=SCOPES
                )
        except Exception:
            pass
    return None

def get_ga4_client():
    creds = get_credentials()
    if creds:
        return BetaAnalyticsDataClient(credentials=creds)
    return BetaAnalyticsDataClient()

@app.get("/")
def index():
    creds = get_credentials()
    if creds:
        return HTMLResponse(f"<h3>GA4 MCP Server is Connected!</h3><p>SSE Endpoint is active at: <code>{BASE_URL}/mcp/sse</code></p>")
    else:
        return HTMLResponse(f"<h3>GA4 MCP Server</h3><p>Not connected. <a href='/login'>Login with Google</a></p>")

@app.get("/login")
def login():
    if not CLIENT_ID or not CLIENT_SECRET:
        return HTMLResponse("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment.", status_code=500)
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return RedirectResponse(auth_url)

@app.get("/oauth2callback")
def oauth2callback(request: Request):
    try:
        flow = get_flow()
        flow.fetch_token(authorization_response=str(request.url).replace("http://", "https://") if "https" in BASE_URL else str(request.url))
        credentials = flow.credentials
        
        creds_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(creds_data, f)
            
        return HTMLResponse("Successfully authenticated! You can close this window and use the MCP server.")
    except Exception as e:
        return HTMLResponse(f"Error during authentication: {str(e)}", status_code=500)

@mcp.tool()
def run_report(property_id: str, start_date: str, end_date: str, metrics: list[str], dimensions: list[str] = None) -> str:
    """
    Run a customized GA4 report.
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
        
    result = {"rows": []}
    for row in response.rows:
        row_dict = {}
        if dimensions:
            for i, dimension_value in enumerate(row.dimension_values):
                row_dict[dimensions[i]] = dimension_value.value
        for i, metric_value in enumerate(row.metric_values):
            row_dict[metrics[i]] = metric_value.value
        result["rows"].append(row_dict)
        
    return json.dumps(result, indent=2)

try:
    mcp_app = mcp.http_app(path="/")
    app.mount("/mcp", mcp_app)
    app.router.lifespan_context = mcp_app.lifespan
except AttributeError:
    # Fallback if fastmcp version doesn't expose it exactly like this
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)
