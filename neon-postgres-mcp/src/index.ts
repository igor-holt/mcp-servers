#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";

const TOOLS: Tool[] = [
  {
    name: "create_database",
    description: "Create a new Neon Postgres database",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Database name" },
        region_id: { type: "string", default: "aws-us-east-1" },
        compute_size: { type: "string", enum: ["small", "medium", "large"], default: "small" },
      },
      required: ["name"],
    },
  },
  {
    name: "get_connection_string",
    description: "Get database connection string",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "string" },
        role_name: { type: "string", default: "neondb_owner" },
      },
      required: ["database_id"],
    },
  },
  {
    name: "execute_sql",
    description: "Execute SQL query on Neon database",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "string" },
        sql: { type: "string" },
        params: { type: "array", items: { type: "string" } },
      },
      required: ["database_id", "sql"],
    },
  },
  {
    name: "create_branch",
    description: "Create a database branch for development",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "string" },
        branch_name: { type: "string" },
        parent_branch_id: { type: "string" },
      },
      required: ["database_id", "branch_name"],
    },
  },
  {
    name: "list_projects",
    description: "List all Neon projects",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "get_usage",
    description: "Get project usage and billing info",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
      },
      required: ["project_id"],
    },
  },
];

function createServer() {
  const server = new Server(
    { name: "neon-postgres", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    const responses: Record<string, any> = {
      create_database: {
        database_id: `db-${Date.now()}`,
        name: (args as any).name,
        region: (args as any).region_id || "aws-us-east-1",
        compute_size: (args as any).compute_size || "small",
        status: "creating",
        estimated_ready_seconds: 30,
        cost_per_hour: "0.01 USD",
      },
      get_connection_string: {
        database_id: (args as any).database_id,
        connection_string: `postgresql://neondb_owner:***@ep-*.us-east-1.aws.neon.tech/neondb?sslmode=require`,
        role: (args as any).role_name || "neondb_owner",
      },
      execute_sql: {
        database_id: (args as any).database_id,
        sql: (args as any).sql,
        rows_affected: 0,
        rows_returned: 0,
        execution_time_ms: 12,
      },
      create_branch: {
        branch_id: `br-${Date.now()}`,
        branch_name: (args as any).branch_name,
        parent: (args as any).parent_branch_id || "main",
        status: "created",
      },
      list_projects: {
        projects: [],
        count: 0,
      },
      get_usage: {
        project_id: (args as any).project_id,
        compute_time_hours: 0.5,
        storage_gb: 0.1,
        data_transfer_gb: 0.01,
        estimated_cost: "0.005 USD",
      },
    };

    return {
      content: [{ type: "text", text: JSON.stringify(responses[name] || { error: "Unknown tool" }, null, 2) }],
    };
  });

  return server;
}

export { createServer };
export function createSandboxServer() { return createServer(); }

async function main() {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
