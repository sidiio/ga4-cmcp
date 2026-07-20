# GA4 FastMCP Server

This is a custom Google Analytics 4 (GA4) MCP server built with Python and [FastMCP](https://github.com/fastmcp/mcp-python). It is designed to work with AI assistants like Claude Web and automation tools like n8n, exposing GA4 querying capabilities over Server-Sent Events (SSE). 

Unlike some other MCP implementations that rely strictly on service accounts, this server uses Google Cloud OAuth 2.0 Client ID and Secret (via environment variables) to authenticate.

## Features
- Provides a `run_report` tool for AI agents to pull specific metrics and dimensions from your GA4 property based on date ranges.
- Uses Server-Sent Events (SSE) transport natively (runs on port `8080`).
- Fully containerized and ready for deployment via Coolify or Docker Compose.

## Prerequisites
You need a Google Cloud project with the **Google Analytics Data API** enabled.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Analytics Data API**.
3. Create OAuth 2.0 Client Credentials (Desktop App or Web App).
4. Obtain a Refresh Token using your Client ID and Secret (you can use the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) with the scope `https://www.googleapis.com/auth/analytics.readonly`).

## Deployment on Coolify
1. Push this repository to your GitHub account.
2. In Coolify, create a new resource and point it to your repository.
3. Coolify will automatically detect the `Dockerfile` / `docker-compose.yml`.
4. In the Coolify environment variables section for this project, add:
   - `GOOGLE_CLIENT_ID`: Your Google Cloud Client ID.
   - `GOOGLE_CLIENT_SECRET`: Your Google Cloud Client Secret.
   - `GOOGLE_REFRESH_TOKEN`: The Refresh Token you generated.
5. Deploy! The server will start and expose the SSE endpoint on port `8080`.

## Local Testing
If you want to run the server locally without Docker:
```bash
pip install -r requirements.txt
export GOOGLE_CLIENT_ID="your_client_id"
export GOOGLE_CLIENT_SECRET="your_client_secret"
export GOOGLE_REFRESH_TOKEN="your_refresh_token"
python server.py --host 0.0.0.0 --port 8080
```

## Connecting to Claude / n8n
Once deployed, grab your Coolify instance URL (e.g., `https://ga4-mcp.yourdomain.com/sse`).
*   **For n8n:** Add the URL to an HTTP request node or a custom MCP connection.
*   **For Claude Web:** Add a Custom Server connection and provide the SSE URL. 

## Tools Available
- **`run_report`**: Extracts data from a GA4 property.
   - `property_id` (string): The GA4 property ID (e.g., '123456789').
   - `start_date` (string): e.g., '2023-01-01', 'today', '30daysAgo'.
   - `end_date` (string): e.g., '2023-12-31', 'today'.
   - `metrics` (list): e.g., `['activeUsers', 'screenPageViews']`.
   - `dimensions` (list, optional): e.g., `['city', 'date']`.
