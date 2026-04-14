#!/usr/bin/env python3
"""
Contract Deployer MCP Server
Deploy and verify Solidity smart contracts on EVM chains
"""

import asyncio
import json
import os
import subprocess
import tempfile
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("contract-deployer")

SUPPORTED_CHAINS = {
    "base": {"rpc": "https://mainnet.base.org", "explorer": "https://api.basescan.org"},
    "ethereum": {"rpc": "https://eth.llamarpc.com", "explorer": "https://api.etherscan.io"},
    "polygon": {"rpc": "https://polygon.llamarpc.com", "explorer": "https://api.polygonscan.com"},
    "arbitrum": {"rpc": "https://arb1.arbitrum.io/rpc", "explorer": "https://api.arbiscan.io"},
    "optimism": {
        "rpc": "https://mainnet.optimism.io",
        "explorer": "https://api-optimistic.etherscan.io",
    },
}

TOOLS = [
    {
        "name": "compile_contract",
        "description": "Compile Solidity contract with solc",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_code": {"type": "string"},
                "contract_name": {"type": "string"},
                "solc_version": {"type": "string", "default": "0.8.24"},
                "optimization": {"type": "boolean", "default": True},
            },
            "required": ["source_code", "contract_name"],
        },
    },
    {
        "name": "deploy_contract",
        "description": "Deploy compiled contract to EVM chain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chain": {"type": "string", "enum": list(SUPPORTED_CHAINS.keys())},
                "bytecode": {"type": "string"},
                "constructor_args": {"type": "array", "items": {"type": "string"}},
                "private_key_env": {"type": "string", "default": "DEPLOYER_PRIVATE_KEY"},
            },
            "required": ["chain", "bytecode"],
        },
    },
    {
        "name": "verify_contract",
        "description": "Verify deployed contract on block explorer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chain": {"type": "string", "enum": list(SUPPORTED_CHAINS.keys())},
                "contract_address": {"type": "string"},
                "contract_name": {"type": "string"},
                "source_code": {"type": "string"},
                "compiler_version": {"type": "string"},
                "api_key_env": {"type": "string", "default": "ETHERSCAN_API_KEY"},
            },
            "required": [
                "chain",
                "contract_address",
                "contract_name",
                "source_code",
                "compiler_version",
            ],
        },
    },
    {
        "name": "estimate_gas",
        "description": "Estimate gas for contract deployment",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chain": {"type": "string", "enum": list(SUPPORTED_CHAINS.keys())},
                "bytecode": {"type": "string"},
            },
            "required": ["chain", "bytecode"],
        },
    },
    {
        "name": "get_chain_info",
        "description": "Get supported chain information",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(**t) for t in TOOLS]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "compile_contract":
        return await handle_compile(arguments)
    elif name == "deploy_contract":
        return await handle_deploy(arguments)
    elif name == "verify_contract":
        return await handle_verify(arguments)
    elif name == "estimate_gas":
        return await handle_estimate_gas(arguments)
    elif name == "get_chain_info":
        return await handle_chain_info()
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_compile(args: dict) -> list[TextContent]:
    source_code = args["source_code"]
    contract_name = args["contract_name"]
    solc_version = args.get("solc_version", "0.8.24")

    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, f"{contract_name}.sol")
        with open(source_path, "w") as f:
            f.write(source_code)

        try:
            result = subprocess.run(
                ["solc", "--bin", "--abi", "--optimize", source_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return [TextContent(type="text", text=f"Compilation failed:\n{result.stderr}")]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "success",
                            "contract": contract_name,
                            "compiler_version": solc_version,
                            "output": result.stdout,
                        },
                        indent=2,
                    ),
                )
            ]
        except FileNotFoundError:
            return [
                TextContent(type="text", text="solc not found. Install with: pip install py-solc-x")
            ]


async def handle_deploy(args: dict) -> list[TextContent]:
    chain = args["chain"]
    bytecode = args["bytecode"]
    constructor_args = args.get("constructor_args", [])

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "simulation",
                    "chain": chain,
                    "bytecode_length": len(bytecode),
                    "constructor_args": constructor_args,
                    "note": "Actual deployment requires Web3 provider and private key",
                    "rpc": SUPPORTED_CHAINS[chain]["rpc"],
                },
                indent=2,
            ),
        )
    ]


async def handle_verify(args: dict) -> list[TextContent]:
    chain = args["chain"]
    contract_address = args["contract_address"]

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "ready",
                    "chain": chain,
                    "contract_address": contract_address,
                    "explorer_api": SUPPORTED_CHAINS[chain]["explorer"],
                    "note": "Set ETHERSCAN_API_KEY environment variable for verification",
                },
                indent=2,
            ),
        )
    ]


async def handle_estimate_gas(args: dict) -> list[TextContent]:
    bytecode = args["bytecode"]
    gas_estimate = len(bytecode) * 10 + 21000

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "bytecode_size": len(bytecode),
                    "estimated_gas": gas_estimate,
                    "estimated_gas_eth": f"{gas_estimate * 0.00000002:.6f}",
                    "note": "Estimate based on bytecode size",
                },
                indent=2,
            ),
        )
    ]


async def handle_chain_info() -> list[TextContent]:
    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "supported_chains": SUPPORTED_CHAINS,
                    "pricing": {
                        "deploy": "0.002 ETH",
                        "verify": "0.0005 ETH",
                        "optimize": "0.001 ETH",
                    },
                },
                indent=2,
            ),
        )
    ]


def main():
    asyncio.run(stdio_server(server).serve())


if __name__ == "__main__":
    main()
