# GA4 FastMCP Server

This is a custom Google Analytics 4 (GA4) MCP server built with Python, FastAPI, and [FastMCP](https://github.com/fastmcp/mcp-python). It is designed to work with AI assistants like Claude Web and automation tools like n8n, exposing GA4 querying capabilities over Server-Sent Events (SSE). 

This server includes a built-in interactive Google Cloud OAuth 2.0 flow. You simply visit the server's URL to log in, and it handles the token generation for you—just like the Google Ads MCP.

## Features
- Interactive Google OAuth 2.0 login (`/login`).
- Provides a `run_report` tool for AI agents to pull specific metrics and dimensions from your GA4 property based on date ranges.
- Uses Server-Sent Events (SSE) transport natively (runs on port `8080`, SSE endpoint is at `/mcp/sse`).
- Fully containerized and ready for deployment via Coolify or Docker Compose.

## Prerequisites
You need a Google Cloud project with the **Google Analytics Data API** enabled.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Analytics Data API**.
3. Create OAuth 2.0 Client Credentials (Web App). 
   - **Crucial Step:** In the Google Cloud Console, set the **Authorized redirect URIs** for your credential to exactly: `https://ga4-mcp.yourdomain.com/oauth2callback` (replace with your actual Coolify/deployment domain).

## Deployment on Coolify
1. Push this repository to your GitHub account.
2. In Coolify, create a new resource and point it to your repository.
3. Coolify will automatically detect the `Dockerfile` / `docker-compose.yml`.
4. In the Coolify environment variables section for this project, add:
   - `GOOGLE_CLIENT_ID`: Your Google Cloud Client ID.
   - `GOOGLE_CLIENT_SECRET`: Your Google Cloud Client Secret.
   - `BASE_URL`: The public URL of your server (e.g., `https://ga4-mcp.yourdomain.com`).
5. Deploy! The server will start and expose the web app on port `8080`.

## Connecting and Authenticating
1. **Authenticate:** Go to your server's base URL (e.g., `https://ga4-mcp.yourdomain.com`).
2. Click **Login with Google**. Follow the prompts to authorize access to your Google Analytics data.
3. The server will automatically save the connection tokens locally.
4. **Connect to Claude / n8n:** Grab your Coolify instance SSE URL (e.g., `https://ga4-mcp.yourdomain.com/mcp/sse`).
   *   **For n8n:** Add the URL to an HTTP request node or a custom MCP connection.
   *   **For Claude Web:** Add a Custom Server connection and provide the SSE URL. 

## Tools Available
- **`run_report`**: Extracts data from a GA4 property.
   - `property_id` (string): The GA4 property ID (e.g., '123456789').
   - `start_date` (string): e.g., '2023-01-01', 'today', '30daysAgo'.
   - `end_date` (string): e.g., '2023-12-31', 'today'.
   - `metrics` (list): e.g., `['activeUsers', 'screenPageViews']`.
   - `dimensions` (list, optional): e.g., `['city', 'date']`.
