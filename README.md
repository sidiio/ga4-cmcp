# GA4 FastMCP Server

This is a custom Google Analytics 4 (GA4) MCP server built with **TypeScript** and [FastMCP](https://github.com/punkpeye/fastmcp). It is designed to natively integrate with Claude Web and other AI assistants that support the Model Context Protocol OAuth flow.

Because it uses FastMCP's built-in `GoogleProvider`, it automatically exposes the `/.well-known/oauth-authorization-server` endpoints. This means **Claude will natively handle the OAuth connection** for you, exactly like the Google Ads MCP!

## Features
- Native Claude Web OAuth integration.
- Provides a `run_report` tool for AI agents to pull specific metrics and dimensions from your GA4 property based on date ranges.
- Uses Server-Sent Events (SSE) transport (port `8080`, SSE endpoint is at `/mcp/sse`).
- Fully containerized Node.js application ready for deployment via Coolify or Docker Compose.

## Prerequisites
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Analytics Data API**.
3. Create OAuth 2.0 Client Credentials (Web App). 
   - **Crucial Step:** When setting the **Authorized redirect URIs** in Google Cloud, you must provide the exact redirect URI that Claude uses for custom MCP connectors (e.g., `https://claude.ai/api/mcp/auth_callback` or whatever Claude specifies when you add the connector).

## Deployment on Coolify
1. Push this repository to your GitHub account.
2. In Coolify, create a new resource and point it to your repository.
3. In the Coolify environment variables section for this project, add:
   - `GOOGLE_CLIENT_ID`: Your Google Cloud Client ID.
   - `GOOGLE_CLIENT_SECRET`: Your Google Cloud Client Secret.
   - `BASE_URL`: The public URL of your server (e.g., `https://mcpga4.yourdomain.com`).
4. Deploy! 

## Connecting to Claude
1. In Claude Web, go to **Connectors** -> **Add Custom Server**.
2. URL: `https://mcpga4.yourdomain.com/mcp/sse`
3. Check **Requires Authentication (OAuth)**.
4. Claude will automatically discover the OAuth endpoints from your server!
5. When you click **Connect**, Claude will redirect you to Google to log in, and securely pass the token to your server.

## Tools Available
- **`run_report`**: Extracts data from a GA4 property.
   - `property_id` (string): The GA4 property ID (e.g., '123456789').
   - `start_date` (string): e.g., '2023-01-01', 'today', '30daysAgo'.
   - `end_date` (string): e.g., '2023-12-31', 'today'.
   - `metrics` (list): e.g., `['activeUsers', 'screenPageViews']`.
   - `dimensions` (list, optional): e.g., `['city', 'date']`.
