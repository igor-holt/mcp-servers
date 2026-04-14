# Genesis Conductor MCP Servers

Multi-registry MCP server packages for AI agent skill deployment.

## Servers

| Server | Version | Description | Registry |
|--------|---------|-------------|----------|
| apple-toolchain | 1.0.1 | LLVM compile/link/inspect for Apple platforms | Smithery, Glama, MCP.so |
| contract-deployer | 1.0.1 | Solidity deployment & verification on EVM chains | Smithery, Glama, MCP.so |
| defi-arbitrage | 1.0.1 | DEX price scanning & flash loan arbitrage | Smithery, Glama, MCP.so |
| keeper-manager | 1.1.0 | Aave V4 eMode liquidation keeper on Base | Smithery, Glama, MCP.so |

## Installation

### Smithery
```bash
npx @smithery/cli@latest setup
smithery mcp add apple-toolchain
```

### Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "apple-toolchain": {
      "command": "uvx",
      "args": ["apple-toolchain-mcp"]
    },
    "contract-deployer": {
      "command": "uvx",
      "args": ["contract-deployer-mcp"]
    },
    "defi-arbitrage": {
      "command": "uvx",
      "args": ["defi-arbitrage-mcp"]
    },
    "keeper-manager": {
      "command": "uvx",
      "args": ["keeper-manager-mcp"]
    }
  }
}
```

## Registry Links

- [Smithery Profile](https://smithery.ai/@genesis-conductor)
- [Glama Directory](https://glama.ai/mcp/servers)
- [MCP.so Marketplace](https://mcp.so)

## Revenue Model

| Skill | Pricing | Treasury Share |
|-------|---------|----------------|
| apple-toolchain | $0.001 ETH/compile | 5% |
| contract-deployer | $0.002 ETH/deploy | 5% |
| defi-arbitrage | 20% profit share | 5% |
| keeper-manager | Subscription tiers | 5% |

## Author

Genesis Conductor — Kovach Enterprises
Principal Investigator: Igor Holt

## License

MIT
