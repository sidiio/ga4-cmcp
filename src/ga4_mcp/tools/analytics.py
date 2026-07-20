"""Google Analytics 4 tools: list properties, run reports, realtime, metadata."""

import json
import logging
from typing import Annotated

import httpx
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken
from fastmcp.server.dependencies import CurrentAccessToken

logger = logging.getLogger(__name__)

_DATA_API = "https://analyticsdata.googleapis.com/v1beta"
_ADMIN_API = "https://analyticsadmin.googleapis.com/v1beta"


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_analytics_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def list_properties(
        token: AccessToken = CurrentAccessToken(),
    ) -> str:
        """List all Google Analytics 4 accounts and properties the user has access to."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{_ADMIN_API}/accountSummaries",
                headers=_headers(token.token),
            )

        if resp.status_code != 200:
            return f"Error listing properties: {resp.status_code} {resp.text}"

        results = []
        for account in resp.json().get("accountSummaries", []):
            for prop in account.get("propertySummaries", []):
                results.append({
                    "account": account.get("displayName"),
                    "property": prop.get("displayName"),
                    "propertyId": prop.get("property", "").replace("properties/", ""),
                })

        return json.dumps(results, indent=2)

    @mcp.tool()
    async def run_report(
        property_id: Annotated[str, "GA4 property ID, e.g. '123456789' (use list_properties to find it)"],
        start_date: Annotated[str, "Start date: 'YYYY-MM-DD', 'today', '7daysAgo', '30daysAgo', '90daysAgo'"],
        end_date: Annotated[str, "End date: 'YYYY-MM-DD', 'today', 'yesterday'"],
        metrics: Annotated[list[str], "Metrics list, e.g. ['activeUsers', 'sessions', 'screenPageViews', 'bounceRate']"],
        dimensions: Annotated[list[str] | None, "Optional dimensions, e.g. ['date', 'country', 'city', 'deviceCategory', 'pagePath', 'sessionSource']"] = None,
        limit: Annotated[int, "Max rows to return, default 1000"] = 1000,
        token: AccessToken = CurrentAccessToken(),
    ) -> str:
        """Run a Google Analytics 4 report. Returns rows with the requested metrics and dimensions."""
        body: dict = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "metrics": [{"name": m} for m in metrics],
            "limit": min(limit, 100000),
        }
        if dimensions:
            body["dimensions"] = [{"name": d} for d in dimensions]

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{_DATA_API}/properties/{property_id}:runReport",
                headers=_headers(token.token),
                json=body,
            )

        if resp.status_code != 200:
            return f"Error running report: {resp.status_code} {resp.text}"

        data = resp.json()
        dim_headers = [h["name"] for h in data.get("dimensionHeaders", [])]
        met_headers = [h["name"] for h in data.get("metricHeaders", [])]

        rows = []
        for row in data.get("rows", []):
            row_dict = {}
            for i, val in enumerate(row.get("dimensionValues", [])):
                row_dict[dim_headers[i]] = val["value"]
            for i, val in enumerate(row.get("metricValues", [])):
                row_dict[met_headers[i]] = val["value"]
            rows.append(row_dict)

        return json.dumps({
            "rowCount": data.get("rowCount", len(rows)),
            "rows": rows,
        }, indent=2)

    @mcp.tool()
    async def run_realtime_report(
        property_id: Annotated[str, "GA4 property ID, e.g. '123456789'"],
        metrics: Annotated[list[str], "Realtime metrics, e.g. ['activeUsers']"],
        dimensions: Annotated[list[str] | None, "Optional dimensions, e.g. ['city', 'country', 'unifiedScreenName']"] = None,
        token: AccessToken = CurrentAccessToken(),
    ) -> str:
        """Run a Google Analytics 4 realtime report showing users active in the last 30 minutes."""
        body: dict = {"metrics": [{"name": m} for m in metrics]}
        if dimensions:
            body["dimensions"] = [{"name": d} for d in dimensions]

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{_DATA_API}/properties/{property_id}:runRealtimeReport",
                headers=_headers(token.token),
                json=body,
            )

        if resp.status_code != 200:
            return f"Error running realtime report: {resp.status_code} {resp.text}"

        data = resp.json()
        dim_headers = [h["name"] for h in data.get("dimensionHeaders", [])]
        met_headers = [h["name"] for h in data.get("metricHeaders", [])]

        rows = []
        for row in data.get("rows", []):
            row_dict = {}
            for i, val in enumerate(row.get("dimensionValues", [])):
                row_dict[dim_headers[i]] = val["value"]
            for i, val in enumerate(row.get("metricValues", [])):
                row_dict[met_headers[i]] = val["value"]
            rows.append(row_dict)

        return json.dumps({"rows": rows}, indent=2)

    @mcp.tool()
    async def get_metadata(
        property_id: Annotated[str, "GA4 property ID to inspect available dimensions and metrics"],
        token: AccessToken = CurrentAccessToken(),
    ) -> str:
        """Get all available dimensions and metrics for a GA4 property (useful for discovering what to query)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{_DATA_API}/properties/{property_id}/metadata",
                headers=_headers(token.token),
            )

        if resp.status_code != 200:
            return f"Error getting metadata: {resp.status_code} {resp.text}"

        data = resp.json()
        return json.dumps({
            "dimensions": [
                {"name": d["apiName"], "description": d.get("description", "")}
                for d in data.get("dimensions", [])
            ],
            "metrics": [
                {"name": m["apiName"], "description": m.get("description", "")}
                for m in data.get("metrics", [])
            ],
        }, indent=2)
