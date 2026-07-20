# GA4 MCP Server

Google Analytics 4 MCP server with OAuth authentication. Connects Claude.ai and other MCP clients directly to your GA4 data via Google login — no server-side OAuth credentials required.

Built with Python [FastMCP](https://github.com/jlowin/fastmcp) using `RemoteAuthProvider`, following the same pattern as the [Google Search Console MCP](https://github.com/sidiio/google-search-console-mcp).

## How it works

The server uses FastMCP's `RemoteAuthProvider` which advertises Google as the authorization server. When you click **Connect** in Claude.ai, Claude handles the Google OAuth flow itself and passes the token to the server. The server validates the token via Google's tokeninfo endpoint — no client credentials needed on the server side.

## Tools

- **`list_properties`** — Lists all GA4 accounts and properties you have access to
- **`run_report`** — Run a report with custom date ranges, metrics, and dimensions
- **`run_realtime_report`** — See users active in the last 30 minutes
- **`get_metadata`** — Discover all available dimensions and metrics for a property

## Deployment on Coolify

### 1. Push to GitHub and connect in Coolify

Point Coolify at this repository. Set **Build Pack** to `Dockerfile`.

### 2. Set environment variables

| Variable | Value |
|---|---|
| `PORT` | `8080` |
| `MCP_BASE_URL` | Your public URL, e.g. `https://ga4-mcp.yourdomain.com` |

That's it. No Google client credentials needed.

### 3. Connect in Claude.ai

1. Go to **Settings → Integrations → Add custom integration**
2. URL: `https://ga4-mcp.yourdomain.com/mcp`
3. Click **Connect** → Google login appears → sign in → done

## Local development

```bash
pip install -e .
MCP_BASE_URL=http://localhost:8080 python -m ga4_mcp
```

## Docker

```bash
docker build -t ga4-mcp .
docker run -p 8080:8080 -e MCP_BASE_URL=http://localhost:8080 ga4-mcp
```
