# core/session.py

import os
import sys
import asyncio
from typing import Optional, Any, List, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import warnings


class MCP:
    """
    Lightweight wrapper for one-time MCP tool calls using stdio transport.
    Each call spins up a new subprocess and terminates cleanly.
    """

    def __init__(
        self,
        server_script: str = "mcp_server_2.py",
        working_dir: Optional[str] = None,
        server_command: Optional[str] = None,
    ):
        self.server_script = server_script
        self.working_dir = working_dir or os.getcwd()
        self.server_command = server_command or "uv"
        self._transport = None
        self._protocol = None
        self._process = None

    async def _cleanup(self):
        if self._process:
            try:
                self._process.terminate()
                await asyncio.sleep(0.1)
                if self._process.returncode is None:
                    self._process.kill()
            except Exception:
                pass
            self._process = None

        if self._transport:
            try:
                self._transport.close()
            except Exception:
                pass
            self._transport = None

    async def list_tools(self):
        server_params = StdioServerParameters(
            command=self.server_command,
            args=["run", self.server_script],
            cwd=self.working_dir
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    return tools_result.tools
        finally:
            await self._cleanup()

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        server_params = StdioServerParameters(
            command=self.server_command,
            args=["run", self.server_script],
            cwd=self.working_dir
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(tool_name, arguments=arguments)
        finally:
            await self._cleanup()


class MultiMCP:
    """
    Stateless version: discovers tools from multiple MCP servers, but reconnects per tool call.
    Each call_tool() uses a fresh session based on tool-to-server mapping.
    """

    def __init__(self, server_configs: List[dict]):
        self.server_configs = server_configs
        self.tool_map: Dict[str, Dict[str, Any]] = {}  # tool_name → {config, tool}
        self._processes = []
        self._transports = []

    async def _cleanup(self):
        for process in self._processes:
            try:
                process.terminate()
                await asyncio.sleep(0.1)
                if process.returncode is None:
                    process.kill()
            except Exception:
                pass
        self._processes.clear()

        for transport in self._transports:
            try:
                transport.close()
            except Exception:
                pass
        self._transports.clear()

    async def initialize(self):
        print("in MultiMCP initialize")
        for config in self.server_configs:
            try:
                params = StdioServerParameters(
                    command="uv",
                    args=["run", config["script"]],
                    cwd=config.get("cwd", os.getcwd())
                )
                print(f"→ Scanning tools from: {config['script']} in {params.cwd}")
                try:
                    async with stdio_client(params) as (read, write):
                        print("Connection established, creating session...")
                        try:
                            async with ClientSession(read, write) as session:
                                print("[agent] Session created, initializing...")
                                await session.initialize()
                                print("[agent] MCP session initialized")
                                tools = await session.list_tools()
                                print(f"→ Tools received: {[tool.name for tool in tools.tools]}")
                                for tool in tools.tools:
                                    self.tool_map[tool.name] = {
                                        "config": config,
                                        "tool": tool
                                    }
                        except Exception as se:
                            print(f"❌ Session error: {se}")
                except Exception as e:
                    print(f"❌ Connection error: {e}")
            except Exception as e:
                print(f"❌ Error initializing MCP server {config['script']}: {e}")
        await self._cleanup()

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        entry = self.tool_map.get(tool_name)
        if not entry:
            raise ValueError(f"Tool '{tool_name}' not found on any server.")

        config = entry["config"]
        params = StdioServerParameters(
            command="uv",
            args=["run", config["script"]],
            cwd=config.get("cwd", os.getcwd())
        )

        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(tool_name, arguments)
        finally:
            await self._cleanup()

    async def list_all_tools(self) -> List[str]:
        return list(self.tool_map.keys())

    def get_all_tools(self) -> List[Any]:
        return [entry["tool"] for entry in self.tool_map.values()]

    async def shutdown(self):
        await self._cleanup()