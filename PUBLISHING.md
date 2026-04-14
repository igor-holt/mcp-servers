# Multi-Registry Publishing Instructions

## Status

✅ **Completed:**
- MCP server wrappers created for all 4 skills
- Smithery CLI v4.8.0 installed
- Unified manifest created

⏳ **Pending:**
- Smithery authentication (requires browser)
- Publishing to Smithery
- GitHub repo creation for Glama/MCP.so auto-indexing

## Smithery Authentication

The CLI generated this auth URL. Visit it in your browser:

```
https://smithery.ai/auth/cli?s=d95fe0bf-d761-4e52-b405-49fa51f9f0fb
```

After authenticating, run:
```bash
cd /Users/igorholt/Desktop/openclaw/mcp-servers
smithery auth status
```

## Publishing Commands

Once authenticated, publish each server:

```bash
cd /Users/igorholt/Desktop/openclaw/mcp-servers

# Publish to Smithery
cd apple-toolchain-mcp && smithery server publish
cd ../contract-deployer-mcp && smithery server publish
cd ../defi-arbitrage-mcp && smithery server publish
cd ../keeper-manager-mcp && smithery server publish
```

## Glama Auto-Indexing

Glama automatically indexes GitHub repos with `mcp` topic:

1. Create GitHub repo: `openclaw/mcp-servers`
2. Push this directory
3. Add `mcp` topic to repo
4. Glama will auto-index within 24-48h

## MCP.so Submission

Submit manually at: https://mcp.so/submit

Required fields per server:
- Name: `apple-toolchain`, `contract-deployer`, etc.
- Description: From smithery.json
- GitHub URL: `https://github.com/openclaw/mcp-servers/tree/main/apple-toolchain-mcp`

## Files Created

```
/Users/igorholt/Desktop/openclaw/mcp-servers/
├── manifest.json              # Unified registry manifest
├── README.md                  # Documentation
├── apple-toolchain-mcp/
│   ├── pyproject.toml
│   ├── smithery.json
│   ├── README.md
│   └── src/apple_toolchain_mcp.py
├── contract-deployer-mcp/
│   ├── pyproject.toml
│   ├── smithery.json
│   └── src/contract_deployer_mcp.py
├── defi-arbitrage-mcp/
│   ├── pyproject.toml
│   ├── smithery.json
│   └── src/defi_arbitrage_mcp.py
└── keeper-manager-mcp/
    ├── pyproject.toml
    ├── smithery.json
    └── src/keeper_manager_mcp.py
```

## Revenue Tracking

All servers integrate with:
- Treasury: `0x3E97190CddC508778BdE37E52005f8Da7F4D476F`
- Fee rate: 5% automatic
- Distribution: 30% ops / 50% reserve / 20% staking
