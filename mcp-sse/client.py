"""Client for the MCP server using Server-Sent Events (SSE)."""

import asyncio

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    """
    Main function to demonstrate MCP client functionality.

    Establishes an SSE connection to the server, initializes a session,
    and demonstrates basic operations like sending pings, listing tools,
    and calling a weather tool.
    """
    async with sse_client(url="http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await session.send_ping()
            tools = await session.list_tools()

            for tool in tools.tools:
                print("Name:", tool.name)
                print("Description:", tool.description)
            print()

            weather = await session.call_tool(
                name="get_weather", arguments={"city": "Tokyo"}
            )
            print("Tool Call")
            print(weather.content[0].text)

            print()

            print("Standard API Call")
            res = await httpx.AsyncClient().get("http://localhost:8000/test")
            print(res.json())


asyncio.run(main())