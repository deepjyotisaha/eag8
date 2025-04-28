import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx

# === CONFIGURATION ===
SERVER_URL = "http://localhost:8002"  # Change this if your server runs elsewhere

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

            # Call the send-telegram-message tool
            print("Calling tool: send-telegram-message")
            send_result = await session.call_tool(
                name="send-telegram-message",
                arguments={
                    "text": "hi"
                }
            )
            print("Send telegram message result:")
            print(send_result.content[0].text)

            print("\nStandard API Call to /test endpoint")
            res = await httpx.AsyncClient().get(f"{SERVER_URL}/test")
            print(res.json())

            # Optionally, listen for incoming Telegram messages (from SSE)
            print("\nListening for incoming Telegram messages (Ctrl+C to exit)...")
            while True:
                msg = await read.receive()
                print("Received from SSE:", msg)

if __name__ == "__main__":
    asyncio.run(main())