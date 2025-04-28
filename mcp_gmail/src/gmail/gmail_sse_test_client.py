"""Test client for Gmail SSE MCP server."""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx

# === CONFIGURATION ===
SERVER_URL = "http://localhost:8001"  # Change this if your server runs elsewhere

async def main():
    # Connect to the SSE endpoint
    async with sse_client(url=f"{SERVER_URL}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            print("Initializing session...")
            await session.initialize()
            print("Session initialized.\n")

            print("Sending ping...")
            await session.send_ping()
            print("Ping sent.\n")

            print("Listing available tools...")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"Name: {tool.name}")
                print(f"Description: {tool.description}\n")

            # Call the send_email tool
            print("Calling tool: send_email")
            send_result = await session.call_tool(
                name="send_email",
                arguments={
                    "recipient_id": "deepjyoti.saha@gmail.com",
                    "subject": "Test Email from MCP SSE Client",
                    "message": "hi"
                }
            )
            print("Send email result:")
            print(send_result.content[0].text)

            print("\nStandard API Call to /test endpoint")
            res = await httpx.AsyncClient().get(f"{SERVER_URL}/test")
            print(res.json())

if __name__ == "__main__":
    asyncio.run(main())