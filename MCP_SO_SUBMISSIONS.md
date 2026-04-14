# MCP.so Submission Details

Submit each server at: https://mcp.so/submit

---

## 1. Apple Toolchain MCP

**Type:** MCP Server
**Name:** apple-toolchain
**URL:** https://github.com/igor-holt/mcp-servers/tree/main/apple-toolchain-mcp
**Server Config:**
```json
{
  "mcpServers": {
    "apple-toolchain": {
      "command": "npx",
      "args": ["-y", "https://github.com/igor-holt/mcp-servers.git#main:apple-toolchain-mcp"]
    }
  }
}
```

---

## 2. Contract Deployer MCP

**Type:** MCP Server
**Name:** contract-deployer
**URL:** https://github.com/igor-holt/mcp-servers/tree/main/contract-deployer-mcp
**Server Config:**
```json
{
  "mcpServers": {
    "contract-deployer": {
      "command": "uvx",
      "args": ["--from", "https://github.com/igor-holt/mcp-servers.git#main:contract-deployer-mcp", "contract-deployer-mcp"]
    }
  }
}
```

---

## 3. DeFi Arbitrage MCP

**Type:** MCP Server
**Name:** defi-arbitrage
**URL:** https://github.com/igor-holt/mcp-servers/tree/main/defi-arbitrage-mcp
**Server Config:**
```json
{
  "mcpServers": {
    "defi-arbitrage": {
      "command": "uvx",
      "args": ["--from", "https://github.com/igor-holt/mcp-servers.git#main:defi-arbitrage-mcp", "defi-arbitrage-mcp"]
    }
  }
}
```

---

## 4. Keeper Manager MCP

**Type:** MCP Server
**Name:** keeper-manager
**URL:** https://github.com/igor-holt/mcp-servers/tree/main/keeper-manager-mcp
**Server Config:**
```json
{
  "mcpServers": {
    "keeper-manager": {
      "command": "uvx",
      "args": ["--from", "https://github.com/igor-holt/mcp-servers.git#main:keeper-manager-mcp", "keeper-manager-mcp"]
    }
  }
}
```

---

## Quick Submission Links

1. https://mcp.so/submit (apple-toolchain)
2. https://mcp.so/submit (contract-deployer)
3. https://mcp.so/submit (defi-arbitrage)
4. https://mcp.so/submit (keeper-manager)

Fill in:
- Type: MCP Server
- Name: [server name]
- URL: [GitHub URL above]
- Server Config: [JSON above]
