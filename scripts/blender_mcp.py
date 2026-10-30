"""Call the locally installed official Blender MCP over MCP stdio.

Run with a Python environment containing `mcp` and `blmcp`. Blender must
already be running with its local MCP bridge enabled. No scene is cleared.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script", nargs="?", type=Path)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--blend", type=Path, help="Use MCP's background Blender tool to inspect a saved file")
    args = parser.parse_args()
    params = StdioServerParameters(command=sys.executable, args=["-m", "blmcp"],
                                  env={"BLENDER_PATH": "/Applications/Blender.app/Contents/MacOS/Blender"})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if args.list:
                listing = await session.list_tools()
                payload = {"tools": [t.name for t in listing.tools]}
            else:
                code = (f"__file__ = {str(args.script.resolve())!r}\n" + args.script.read_text()) if args.script else "import bpy\nresult = {'version': bpy.app.version_string, 'filepath': bpy.data.filepath, 'dirty': bpy.data.is_dirty, 'scenes': [{'name': s.name, 'objects': len(s.objects)} for s in bpy.data.scenes]}"
                if args.blend:
                    response = await session.call_tool("execute_blender_code_for_cli", {"blend_file":str(args.blend.resolve()),"code":code})
                else:
                    response = await session.call_tool("execute_blender_code", {"code": code})
                payload = response.model_dump(mode="json")
            output = json.dumps(payload, indent=2)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(output + "\n")
            print(output)
            structured = payload.get("structuredContent") or {}
            if payload.get("isError") or structured.get("status") == "error":
                raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
