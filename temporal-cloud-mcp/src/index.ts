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
    name: "create_namespace",
    description: "Create a new Temporal namespace for workflow orchestration",
    inputSchema: {
      type: "object",
      properties: {
        namespace: { type: "string", description: "Namespace name" },
        retention_days: { type: "number", default: 7 },
        description: { type: "string" },
      },
      required: ["namespace"],
    },
  },
  {
    name: "start_workflow",
    description: "Start a Temporal workflow execution",
    inputSchema: {
      type: "object",
      properties: {
        workflow_type: { type: "string" },
        task_queue: { type: "string" },
        input: { type: "object" },
        workflow_id: { type: "string" },
      },
      required: ["workflow_type", "task_queue"],
    },
  },
  {
    name: "query_workflow",
    description: "Query workflow status and state",
    inputSchema: {
      type: "object",
      properties: {
        workflow_id: { type: "string" },
        run_id: { type: "string" },
      },
      required: ["workflow_id"],
    },
  },
  {
    name: "signal_workflow",
    description: "Send signal to running workflow",
    inputSchema: {
      type: "object",
      properties: {
        workflow_id: { type: "string" },
        signal_name: { type: "string" },
        payload: { type: "object" },
      },
      required: ["workflow_id", "signal_name"],
    },
  },
  {
    name: "list_workflows",
    description: "List workflows in namespace",
    inputSchema: {
      type: "object",
      properties: {
        namespace: { type: "string" },
        status: { type: "string", enum: ["running", "completed", "failed", "all"] },
      },
    },
  },
  {
    name: "get_cluster_info",
    description: "Get Temporal cluster information and health",
    inputSchema: { type: "object", properties: {} },
  },
];

function createServer() {
  const server = new Server(
    { name: "temporal-cloud", version: "1.28.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    const responses: Record<string, any> = {
      create_namespace: {
        namespace: (args as any).namespace,
        retention_days: (args as any).retention_days || 7,
        status: "created",
        cost: "0.05 USD",
      },
      start_workflow: {
        workflow_id: (args as any).workflow_id || `wf-${Date.now()}`,
        status: "started",
        task_queue: (args as any).task_queue,
      },
      query_workflow: {
        workflow_id: (args as any).workflow_id,
        status: "running",
        current_step: "processing",
        cost: "0.001 USD",
      },
      signal_workflow: {
        workflow_id: (args as any).workflow_id,
        signal: (args as any).signal_name,
        delivered: true,
      },
      list_workflows: {
        namespace: (args as any).namespace || "default",
        workflows: [],
        count: 0,
      },
      get_cluster_info: {
        version: "1.28.0",
        health: "healthy",
        regions: ["us-east-1", "eu-west-1", "ap-southeast-1"],
        pricing: { per_workflow: "0.001 USD", per_hour: "0.05 USD" },
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
