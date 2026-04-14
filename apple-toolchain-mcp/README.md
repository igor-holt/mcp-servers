# Apple Toolchain MCP Server

MCP server for Apple LLVM toolchain operations - compile, link, and inspect Mach-O binaries with automatic payment processing.

## Features

- **Compile**: C/C++/Objective-C/Objective-C++ source files with clang/clang++
- **Link**: Object files into executables or dynamic libraries
- **Inspect**: Mach-O binaries with otool, nm, lipo, file
- **Diagnose**: Parse compiler/linker errors with actionable solutions
- **Makefile**: Generate POSIX Makefiles for multi-architecture builds

## Installation

```bash
pip install apple-toolchain-mcp
```

Or with uv:

```bash
uvx apple-toolchain-mcp
```

## Usage

### Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "apple-toolchain": {
      "command": "uvx",
      "args": ["apple-toolchain-mcp"]
    }
  }
}
```

### Cursor / Windsurf

Add to your MCP settings.

## Tools

| Tool | Description |
|------|-------------|
| `compile` | Compile source files for Apple platforms |
| `link` | Link object files into executables/dylibs |
| `inspect` | Inspect Mach-O binaries |
| `diagnose` | Diagnose compiler/linker errors |
| `makefile` | Generate POSIX Makefile |
| `sdk_info` | Get SDK and toolchain information |

## Supported Platforms

- macOS (arm64, x86_64)
- iOS (arm64, arm64e)
- watchOS (arm64_32)
- tvOS (arm64)
- visionOS (arm64)

## License

MIT

## Author

Genesis Conductor
