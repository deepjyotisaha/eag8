#from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import json
from .gmail_mcp_server import GmailService, handle_list_tools 
import os


# Set up credential and token paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GMAIL_SERVER_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
SECRETS_DIR = os.path.join(GMAIL_SERVER_ROOT, ".google")
CREDS_FILE_PATH = os.path.join(SECRETS_DIR, "client_creds.json")
TOKEN_PATH = os.path.join(SECRETS_DIR, "app_tokens.json")

gmail_service = GmailService(CREDS_FILE_PATH, TOKEN_PATH)

# Set up FastMCP and FastAPI
mcp: FastMCP = FastMCP("GmailApp")
app = FastAPI()

@mcp.tool(name="send-email")
async def send_email(recipient_id: str, subject: str, message: str) -> str:
    """Send an email using GmailService."""
    result = await gmail_service.send_email(recipient_id, subject, message)
    if result["status"] == "success":
        return f"Email sent successfully. Message ID: {result['message_id']}"
    else:
        return f"Failed to send email: {result['error_message']}"

@mcp.tool(name="get-unread-emails")
async def get_unread_emails() -> str:
    """Get unread emails using GmailService."""
    result = await gmail_service.get_unread_emails()
    return str(result)

@mcp.tool(name="read-email")
async def read_email(email_id: str) -> str:
    """Read an email using GmailService."""
    result = await gmail_service.read_email(email_id)
    return str(result)

@mcp.tool(name="trash-email")
async def trash_email(email_id: str) -> str:
    """Trash an email using GmailService."""
    return await gmail_service.trash_email(email_id)

@mcp.tool(name="mark-email-as-read")
async def mark_email_as_read(email_id: str) -> str:
    """Mark an email as read using GmailService."""
    return await gmail_service.mark_email_as_read(email_id)

@mcp.tool(name="open-email")
async def open_email(email_id: str) -> str:
    """Open an email in the browser using GmailService."""
    return await gmail_service.open_email(email_id)

@app.get("/test")
async def test():
    """Test endpoint to verify the server is running."""
    return {"message": "Hello from Gmail SSE MCP server!"}


@app.get("/list_tools")
async def list_tools():
    # Call the same function used in your stdio server for tool listing
    tools = await handle_list_tools()
    # Convert Pydantic models or custom objects to dict if needed
    tools_dict = [t.dict() if hasattr(t, "dict") else t for t in tools]
    return JSONResponse(content=tools_dict)

# Mount the SSE MCP server
app.mount("/", mcp.sse_app())