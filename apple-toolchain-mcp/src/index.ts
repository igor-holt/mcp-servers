#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync } from "child_process";
import { existsSync } from "fs";

const TOOLS: Tool[] = [
  {
    name: "compile",
    description: "Compile C/C++/Objective-C source files for Apple platforms using clang",
    inputSchema: {
      type: "object",
      properties: {
        platform: { type: "string", enum: ["macos", "ios", "watchos", "tvos", "visionos", "catalyst"] },
        arch: { type: "array", items: { type: "string", enum: ["arm64", "arm64e", "x86_64", "arm64_32"] } },
        language: { type: "string", enum: ["c", "cpp", "objc", "objc++"] },
        optimization: { type: "string", enum: ["O0", "O1", "O2", "O3", "Os", "Oz", "Ofast"], default: "O2" },
        source_files: { type: "array", items: { type: "string" } },
        output: { type: "string" },
      },
      required: ["platform", "arch", "language", "source_files", "output"],
    },
  },
  {
    name: "link",
    description: "Link object files into executable or dynamic library",
    inputSchema: {
      type: "object",
      properties: {
        arch: { type: "string" },
        object_files: { type: "array", items: { type: "string" } },
        frameworks: { type: "array", items: { type: "string" } },
        libraries: { type: "array", items: { type: "string" } },
        output: { type: "string" },
      },
      required: ["arch", "object_files", "output"],
    },
  },
  {
    name: "inspect",
    description: "Inspect Mach-O binary with otool, nm, lipo, file",
    inputSchema: {
      type: "object",
      properties: {
        binary_path: { type: "string" },
        tools: { type: "array", items: { type: "string", enum: ["file", "otool", "nm", "lipo"] } },
      },
      required: ["binary_path"],
    },
  },
  {
    name: "diagnose",
    description: "Diagnose compiler/linker errors with actionable solutions",
    inputSchema: {
      type: "object",
      properties: {
        stderr_output: { type: "string" },
      },
      required: ["stderr_output"],
    },
  },
  {
    name: "makefile",
    description: "Generate POSIX Makefile for multi-architecture builds",
    inputSchema: {
      type: "object",
      properties: {
        platform: { type: "string" },
        arch: { type: "array", items: { type: "string" } },
        output: { type: "string" },
      },
      required: ["platform", "arch", "output"],
    },
  },
  {
    name: "sdk_info",
    description: "Get SDK paths and toolchain versions",
    inputSchema: { type: "object", properties: {} },
  },
];

function createServer() {
  const server = new Server(
    { name: "apple-toolchain", version: "1.0.1" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "compile": {
          const { platform, arch, language, optimization = "O2", source_files, output } = args as any;
          const compiler = language === "c" || language === "objc" ? "clang" : "clang++";
          const cmd = `xcrun ${compiler} -target=${arch[0]}-apple-${platform}14.0 -${optimization} -Wall -Wextra -o ${output} ${source_files.join(" ")}`;
          const result = execSync(cmd, { encoding: "utf-8", timeout: 60000 });
          return { content: [{ type: "text", text: JSON.stringify({ status: "success", output, flags: { target: `${arch[0]}-apple-${platform}14.0` } }, null, 2) }] };
        }
        case "link": {
          const { arch, object_files, frameworks = [], output } = args as any;
          const fwFlags = (frameworks as string[]).map((fw) => `-framework ${fw}`).join(" ");
          const cmd = `xcrun ld -arch ${arch} -o ${output} ${object_files.join(" ")} ${fwFlags}`;
          const result = execSync(cmd, { encoding: "utf-8" });
          return { content: [{ type: "text", text: JSON.stringify({ status: "success", output }, null, 2) }] };
        }
        case "inspect": {
          const { binary_path, tools = ["file", "otool", "nm", "lipo"] } = args as any;
          if (!existsSync(binary_path)) return { content: [{ type: "text", text: `Binary not found: ${binary_path}` }] };
          const inspection: Record<string, string> = {};
          (tools as string[]).forEach((tool) => {
            if (tool === "file") inspection.file = execSync(`file ${binary_path}`).toString();
            else if (tool === "otool") inspection.otool = execSync(`otool -l ${binary_path}`).toString();
            else if (tool === "nm") inspection.nm = execSync(`nm ${binary_path}`).toString();
            else if (tool === "lipo") inspection.lipo = execSync(`lipo -info ${binary_path}`).toString();
          });
          return { content: [{ type: "text", text: JSON.stringify(inspection, null, 2) }] };
        }
        case "diagnose": {
          const { stderr_output } = args as any;
          const stderr = stderr_output.toLowerCase();
          const diagnostics: Array<{ error_type: string; solution: string }> = [];
          if (stderr.includes("undefined symbols")) diagnostics.push({ error_type: "undefined_symbol", solution: "Add -framework <name> or -l<lib>" });
          else if (stderr.includes("file not found")) diagnostics.push({ error_type: "missing_header", solution: "Add -I<path> or install SDK" });
          return { content: [{ type: "text", text: JSON.stringify({ diagnostics }, null, 2) }] };
        }
        case "makefile": {
          const { platform, arch, output } = args as any;
          const makefile = `CC = xcrun clang\nARCHS = ${arch.join(" ")}\nOUTPUT = ${output}\n\nall: $(OUTPUT)\n\n$(OUTPUT): main.c\n\t$(CC) -arch $(ARCHS) -o $@ $<\n\nclean:\n\trm -f $(OUTPUT)\n`;
          return { content: [{ type: "text", text: makefile }] };
        }
        case "sdk_info": {
          const xcodePath = execSync("xcode-select -p 2>/dev/null || echo 'not found'").toString().trim();
          const xcodeVersion = execSync("xcodebuild -version 2>/dev/null | head -1 || echo 'Unknown'").toString().trim();
          return { content: [{ type: "text", text: JSON.stringify({ xcode_version: xcodeVersion, xcode_path: xcodePath, available_sdks: ["macosx", "iphoneos", "watchos", "appletvos", "xros"] }, null, 2) }] };
        }
        default:
          return { content: [{ type: "text", text: `Unknown tool: ${name}` }] };
      }
    } catch (error: any) {
      return { content: [{ type: "text", text: `Error: ${error.message}` }] };
    }
  });

  return server;
}

export { createServer };

export function createSandboxServer() {
  return createServer();
}

async function main() {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
