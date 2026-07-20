import { FastMCP, GoogleProvider, getAuthSession, requireAuth } from "fastmcp";
import { BetaAnalyticsDataClient } from "@google/analytics-data";
import { OAuth2Client } from "google-auth-library";
import { z } from "zod";

const server = new FastMCP({
  name: "GA4 MCP Server",
  version: "1.0.0",
  auth: new GoogleProvider({
    baseUrl: process.env.BASE_URL!,
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    scopes: ["https://www.googleapis.com/auth/analytics.readonly"],
  }),
});

server.addTool({
  name: "run_report",
  description: "Run a customized GA4 report",
  parameters: z.object({
    property_id: z.string().describe("The GA4 property ID (e.g., '123456789')"),
    start_date: z.string().describe("Start date (e.g. '2023-01-01', 'today', '30daysAgo')"),
    end_date: z.string().describe("End date (e.g. '2023-12-31', 'today')"),
    metrics: z.array(z.string()).describe("List of metrics (e.g., ['activeUsers'])"),
    dimensions: z.array(z.string()).optional().describe("List of dimensions (e.g., ['city', 'date'])"),
  }),
  canAccess: requireAuth,
  execute: async (args, { session }) => {
    const { accessToken } = getAuthSession(session);
    
    const authClient = new OAuth2Client();
    authClient.setCredentials({ access_token: accessToken });
    
    const analyticsDataClient = new BetaAnalyticsDataClient({
      authClient: authClient,
    });

    try {
      const [response] = await analyticsDataClient.runReport({
        property: `properties/${args.property_id}`,
        dateRanges: [
          {
            startDate: args.start_date,
            endDate: args.end_date,
          },
        ],
        dimensions: (args.dimensions || []).map(name => ({ name })),
        metrics: args.metrics.map(name => ({ name })),
      });
      
      const result = { rows: [] as any[] };
      
      if (response.rows) {
        for (const row of response.rows) {
          const rowDict: any = {};
          if (args.dimensions && row.dimensionValues) {
            args.dimensions.forEach((dim, i) => {
              rowDict[dim] = row.dimensionValues![i].value;
            });
          }
          if (row.metricValues) {
            args.metrics.forEach((metric, i) => {
              rowDict[metric] = row.metricValues![i].value;
            });
          }
          result.rows.push(rowDict);
        }
      }
      
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return `Error running report: ${error.message}`;
    }
  },
});

async function main() {
  const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 8080;
  
  await server.start({
    transportType: "sse",
    sse: {
      endpoint: "/mcp/sse",
      port: port
    }
  });
  
  console.log(`GA4 MCP Server running on port ${port} via SSE`);
}

main().catch(console.error);
