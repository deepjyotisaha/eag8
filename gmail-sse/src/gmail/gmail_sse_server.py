#from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import json
from .gmail_mcp_server import GmailService, handle_list_tools  # Adjust import if needed
import os

mcp: FastMCP = FastMCP("App")
app = FastAPI()

# Get the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up to the gmail server root if needed
GMAIL_SERVER_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# Paths to credentials and token files
SECRETS_DIR = os.path.join(GMAIL_SERVER_ROOT, ".google")
CREDS_FILE_PATH = os.path.join(SECRETS_DIR, "client_creds.json")
TOKEN_PATH = os.path.join(SECRETS_DIR, "app_tokens.json")

gmail_service = GmailService(CREDS_FILE_PATH, TOKEN_PATH)

@app.get("/tool_call")
async def tool_call(request: Request):
    tool_name = request.query_params.get("tool")
    arguments = dict(request.query_params)
    arguments.pop("tool", None)

    async def event_generator():
        # Map tool_name to the actual GmailService method
        if tool_name == "send-email":
            result = await gmail_service.send_email(
                recipient_id=arguments["recipient_id"],
                subject=arguments["subject"],
                message=arguments["message"]
            )
            yield f"data: {json.dumps(result)}\n\n"
        elif tool_name == "get-unread-emails":
            result = await gmail_service.get_unread_emails()
            yield f"data: {json.dumps(result)}\n\n"
        elif tool_name == "read-email":
            result = await gmail_service.read_email(arguments["email_id"])
            yield f"data: {json.dumps(result)}\n\n"
        # Add other tools as needed
        else:
            yield f"data: {json.dumps({'error': 'Unknown tool'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/list_tools")
async def list_tools():
    # Call the same function used in your stdio server for tool listing
    tools = await handle_list_tools()
    # Convert Pydantic models or custom objects to dict if needed
    tools_dict = [t.dict() if hasattr(t, "dict") else t for t in tools]
    return JSONResponse(content=tools_dict)


app.mount("/", mcp.sse_app())