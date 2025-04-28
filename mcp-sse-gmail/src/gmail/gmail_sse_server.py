#from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import json
from .gmail_mcp_server import GmailService, get_gmail_tools 
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
    """
    Sends email to recipient.
    Do not use if user only asked to draft email.
    Drafts must be approved before sending.
    Usage: send-email|recipient_id="someone@example.com"|subject="Hello"|message="Body text"
    """
    result = await gmail_service.send_email(recipient_id, subject, message)
    if result["status"] == "success":
        return f"Email sent successfully. Message ID: {result['message_id']}"
    else:
        return f"Failed to send email: {result['error_message']}"

@mcp.tool(name="get-unread-emails")
async def get_unread_emails() -> str:
    """
    Retrieve unread emails.
    Usage: get-unread-emails
    """
    result = await gmail_service.get_unread_emails()
    return str(result)

@mcp.tool(name="read-email")
async def read_email(email_id: str) -> str:
    """
    Retrieves given email content.
    Usage: read-email|email_id="abc123"
    """
    result = await gmail_service.read_email(email_id)
    return str(result)

@mcp.tool(name="trash-email")
async def trash_email(email_id: str) -> str:
    """
    Moves email to trash. Confirm before moving email to trash.
    Usage: trash-email|email_id="abc123"
    """
    return await gmail_service.trash_email(email_id)

@mcp.tool(name="mark-email-as-read")
async def mark_email_as_read(email_id: str) -> str:
    """
    Marks given email as read.
    Usage: mark-email-as-read|email_id="abc123"
    """
    return await gmail_service.mark_email_as_read(email_id)

@mcp.tool(name="open-email")
async def open_email(email_id: str) -> str:
    """
    Open email in browser.
    Usage: open-email|email_id="abc123"
    """
    return await gmail_service.open_email(email_id)

@app.get("/test")
async def test():
    """Test endpoint to verify the server is running."""
    return {"message": "Hello from Gmail SSE MCP server!"}


@app.get("/list_tools")
async def list_tools():
    tools = get_gmail_tools()
    print("tools:", tools)
    tools_dict = [t.dict() if hasattr(t, "dict") else t for t in tools]
    print("tools_dict:", tools_dict)
    return JSONResponse(content=tools_dict)

# Mount the SSE MCP server
app.mount("/", mcp.sse_app())