import httpx

async def sse_tool_call(url, tool_name, arguments):
    async with httpx.AsyncClient(timeout=None) as client:
        params = {"tool": tool_name, **arguments}
        async with client.stream("GET", url, params=params) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]
