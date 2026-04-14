#!/usr/bin/env python3
"""
Apple Toolchain MCP Server
MCP wrapper for Apple LLVM toolchain operations
"""

import asyncio
import json
import os
import subprocess
import shutil
import tempfile
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("apple-toolchain")

MERCHANT_BOT_URL = os.getenv("MERCHANT_BOT_URL", "http://localhost:8202")
SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS", "0xAppleToolchainService")
COMPILE_PRICE_WEI = int(os.getenv("COMPILE_PRICE_WEI", "1000000000000000"))
LINK_PRICE_WEI = int(os.getenv("LINK_PRICE_WEI", "500000000000000"))

TOOLS = [
    {
        "name": "compile",
        "description": "Compile C/C++/Objective-C source files for Apple platforms using clang",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["macos", "ios", "watchos", "tvos", "visionos", "catalyst"],
                },
                "arch": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["arm64", "arm64e", "x86_64", "arm64_32"]},
                },
                "language": {"type": "string", "enum": ["c", "cpp", "objc", "objc++"]},
                "optimization": {
                    "type": "string",
                    "enum": ["O0", "O1", "O2", "O3", "Os", "Oz", "Ofast"],
                    "default": "O2",
                },
                "source_files": {"type": "array", "items": {"type": "string"}},
                "output": {"type": "string"},
            },
            "required": ["platform", "arch", "language", "source_files", "output"],
        },
    },
    {
        "name": "link",
        "description": "Link object files into executable or dynamic library",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string"},
                "arch": {"type": "string"},
                "object_files": {"type": "array", "items": {"type": "string"}},
                "frameworks": {"type": "array", "items": {"type": "string"}},
                "libraries": {"type": "array", "items": {"type": "string"}},
                "output": {"type": "string"},
                "output_type": {
                    "type": "string",
                    "enum": ["executable", "dylib"],
                    "default": "executable",
                },
            },
            "required": ["arch", "object_files", "output"],
        },
    },
    {
        "name": "inspect",
        "description": "Inspect Mach-O binary with otool, nm, lipo, file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "binary_path": {"type": "string"},
                "tools": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["file", "otool", "nm", "lipo"]},
                },
            },
            "required": ["binary_path"],
        },
    },
    {
        "name": "diagnose",
        "description": "Diagnose compiler/linker errors with actionable solutions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stderr_output": {"type": "string"},
                "compiler": {"type": "string", "default": "ld"},
            },
            "required": ["stderr_output"],
        },
    },
    {
        "name": "makefile",
        "description": "Generate POSIX Makefile for multi-architecture builds",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string"},
                "arch": {"type": "array", "items": {"type": "string"}},
                "language": {"type": "string"},
                "output": {"type": "string"},
                "frameworks": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["platform", "arch", "language", "output"],
        },
    },
    {
        "name": "sdk_info",
        "description": "Get SDK paths, toolchain versions, and pricing information",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(**t) for t in TOOLS]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "compile":
        return await handle_compile(arguments)
    elif name == "link":
        return await handle_link(arguments)
    elif name == "inspect":
        return await handle_inspect(arguments)
    elif name == "diagnose":
        return await handle_diagnose(arguments)
    elif name == "makefile":
        return await handle_makefile(arguments)
    elif name == "sdk_info":
        return await handle_sdk_info()
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_compile(args: dict) -> list[TextContent]:
    platform = args["platform"]
    arch = args["arch"]
    language = args["language"]
    optimization = args.get("optimization", "O2")
    source_files = args["source_files"]
    output = args["output"]

    with tempfile.TemporaryDirectory() as tmpdir:
        sources_in_tmp = []
        for src in source_files:
            if not os.path.isabs(src):
                src = os.path.abspath(src)
            if not os.path.exists(src):
                return [TextContent(type="text", text=f"Source not found: {src}")]
            shutil.copy(src, tmpdir)
            sources_in_tmp.append(os.path.basename(src))

        compiler = "clang" if language in ["c", "objc"] else "clang++"
        cmd = [
            "xcrun",
            compiler,
            f"-target={arch[0]}-apple-{platform}14.0",
            f"-{optimization}",
            "-Wall",
            "-Wextra",
            "-o",
            output,
        ] + sources_in_tmp

        try:
            result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return [TextContent(type="text", text=f"Compilation failed:\n{result.stderr}")]

            if os.path.exists(os.path.join(tmpdir, output)):
                shutil.copy(os.path.join(tmpdir, output), os.getcwd())

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "success",
                            "output": output,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "flags": {
                                "target": f"{arch[0]}-apple-{platform}14.0",
                                "optimization": optimization,
                            },
                        },
                        indent=2,
                    ),
                )
            ]
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="Compilation timeout")]


async def handle_link(args: dict) -> list[TextContent]:
    arch = args["arch"]
    object_files = args["object_files"]
    frameworks = args.get("frameworks", [])
    libraries = args.get("libraries", [])
    output = args["output"]

    with tempfile.TemporaryDirectory() as tmpdir:
        objs_in_tmp = []
        for obj in object_files:
            if not os.path.isabs(obj):
                obj = os.path.abspath(obj)
            shutil.copy(obj, tmpdir)
            objs_in_tmp.append(os.path.basename(obj))

        cmd = ["xcrun", "ld", "-arch", arch, "-o", output] + objs_in_tmp
        for fw in frameworks:
            cmd += ["-framework", fw]
        for lib in libraries:
            cmd += ["-l", lib]

        result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True)
        if result.returncode != 0:
            return [TextContent(type="text", text=f"Link failed:\n{result.stderr}")]

        if os.path.exists(os.path.join(tmpdir, output)):
            shutil.copy(os.path.join(tmpdir, output), os.getcwd())

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"status": "success", "output": output, "stderr": result.stderr}, indent=2
                ),
            )
        ]


async def handle_inspect(args: dict) -> list[TextContent]:
    binary_path = args["binary_path"]
    tools = args.get("tools", ["file", "otool", "nm", "lipo"])

    if not os.path.exists(binary_path):
        return [TextContent(type="text", text=f"Binary not found: {binary_path}")]

    inspection = {}
    for tool in tools:
        if tool == "file":
            inspection["file"] = subprocess.getoutput(f"file {binary_path}")
        elif tool == "otool":
            inspection["otool_header"] = subprocess.getoutput(f"otool -l {binary_path}")
        elif tool == "nm":
            inspection["nm_symbols"] = subprocess.getoutput(f"nm {binary_path}")
        elif tool == "lipo":
            inspection["lipo_archs"] = subprocess.getoutput(f"lipo -info {binary_path}")

    return [TextContent(type="text", text=json.dumps(inspection, indent=2))]


async def handle_diagnose(args: dict) -> list[TextContent]:
    stderr = args["stderr_output"].lower()
    diagnostics = []

    if "undefined symbols" in stderr:
        diagnostics.append(
            {
                "error_type": "undefined_symbol",
                "solution": "Add missing -framework <name> or -l<lib> to linker flags",
            }
        )
    elif "file not found" in stderr:
        diagnostics.append(
            {
                "error_type": "missing_header",
                "solution": "Add -I<path> or install missing SDK components",
            }
        )
    elif "framework not found" in stderr:
        diagnostics.append(
            {
                "error_type": "missing_framework",
                "solution": "Add -framework <name> to linker flags or install framework",
            }
        )

    return [TextContent(type="text", text=json.dumps({"diagnostics": diagnostics}, indent=2))]


async def handle_makefile(args: dict) -> list[TextContent]:
    platform = args["platform"]
    arch = args["arch"]
    language = args["language"]
    output = args["output"]
    frameworks = args.get("frameworks", [])

    makefile = f"""# Auto-generated POSIX Makefile for {platform} universal build
CC = xcrun clang
ARCHS = {" ".join(arch)}
OUTPUT = {output}
FRAMEWORKS = {" ".join(f"-framework {fw}" for fw in frameworks)}

all: $(OUTPUT)

$(OUTPUT): main.c
\t$(CC) -arch $(ARCHS) $(FRAMEWORKS) -o $@ $<

clean:
\trm -f $(OUTPUT)
"""
    return [TextContent(type="text", text=makefile)]


async def handle_sdk_info() -> list[TextContent]:
    xcode_path = subprocess.getoutput("xcode-select -p 2>/dev/null || echo 'Xcode not found'")
    xcode_version = subprocess.getoutput(
        "xcodebuild -version 2>/dev/null | head -1 || echo 'Unknown'"
    )

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "xcode_version": xcode_version,
                    "xcode_path": xcode_path,
                    "available_sdks": ["macosx", "iphoneos", "watchos", "appletvos", "xros"],
                    "pricing": {"compile": "0.001 ETH", "link": "0.0005 ETH"},
                },
                indent=2,
            ),
        )
    ]


def main():
    asyncio.run(stdio_server(server).serve())


if __name__ == "__main__":
    main()
