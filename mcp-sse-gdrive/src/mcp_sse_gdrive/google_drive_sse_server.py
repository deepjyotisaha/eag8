# google_drive_sse_server.py

from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi.responses import JSONResponse
import os
from typing import Optional, List
from mcp_sse_gdrive.google_drive_service import GoogleDriveService


# Set up credential and token paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRETS_DIR = os.path.join(BASE_DIR, ".google")
CREDS_FILE_PATH = os.path.join(SECRETS_DIR, "client_creds.json")
TOKEN_PATH = os.path.join(SECRETS_DIR, "drive_tokens.json")

# Create .google directory if it doesn't exist
os.makedirs(SECRETS_DIR, exist_ok=True)

# Check if credentials exist
if not os.path.exists(CREDS_FILE_PATH):
    print(f"""
    Error: Google credentials file not found at {CREDS_FILE_PATH}
    
    Please follow these steps:
    1. Go to Google Cloud Console (https://console.cloud.google.com)
    2. Create a project or select an existing one
    3. Enable the Google Drive API
    4. Create OAuth 2.0 credentials
    5. Download the credentials and save as 'client_creds.json' in the .google directory
    
    The .google directory should be at: {SECRETS_DIR}
    """)
    raise FileNotFoundError(f"Google credentials file not found at {CREDS_FILE_PATH}")

# Initialize FastMCP and FastAPI
mcp: FastMCP = FastMCP("GoogleDriveApp")
app = FastAPI()

# Initialize Google Drive service
drive_service = GoogleDriveService(CREDS_FILE_PATH, TOKEN_PATH)

# Register MCP tools
@mcp.tool(name="search-files")
async def search_files(query: str) -> str:
    """
    Search for files in Google Drive using Google Drive API query syntax.
    
    Common query patterns:
    1. Search by file type:
       - For Spreadsheets: query="mimeType='application/vnd.google-apps.spreadsheet'"
       - For Docs: query="mimeType='application/vnd.google-apps.document'"
       
    2. Search by name:
       - Exact match: query="name='example.txt'"
       - Contains: query="name contains 'example'"
       
    3. Search by modification time:
       - Recent files: query="modifiedTime > '2024-01-01T00:00:00'"
       
    4. Combined searches:
       - Recent spreadsheets: query="mimeType='application/vnd.google-apps.spreadsheet' and modifiedTime > '2024-01-01T00:00:00'"
       - Named docs: query="mimeType='application/vnd.google-apps.document' and name contains 'Report'"
       
    5. Owner-based search:
       - Files owned by you: query="'me' in owners"
       
    Usage examples:
    - search-files|query="mimeType='application/vnd.google-apps.spreadsheet' and name contains 'F1 Standings'"
    - search-files|query="mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet'"
    - search-files|query="name contains 'Project' and modifiedTime > '2024-01-01T00:00:00'"
    """
    result = await drive_service.search_files(query)
    return str(result)

@mcp.tool(name="create-spreadsheet")
async def create_spreadsheet(title: str, initial_data: Optional[List[List]] = None) -> str:
    """
    Create a new Google Spreadsheet and return the spreadsheet ID and URL.
    Usage: create-spreadsheet|title="My Spreadsheet"|initial_data=[["Header1", "Header2"], ["Value1", "Value2"]]
    """
    result = await drive_service.create_spreadsheet(title, initial_data)
    return str(result)

@mcp.tool(name="create-document")
async def create_document(title: str, content: Optional[str] = None) -> str:
    """
    Create a new Google Doc.
    Usage: create-document|title="My Document"|content="Initial content"
    """
    result = await drive_service.create_document(title, content)
    return str(result)

@mcp.tool(name="read-spreadsheet")
async def read_spreadsheet(spreadsheet_id: str, range_name: str = 'Sheet1') -> str:
    """
    Read content from an existing Google Spreadsheet.
    Usage: read-spreadsheet|spreadsheet_id="1234..."|range_name="Sheet1!A1:B10"
    """
    result = await drive_service.read_spreadsheet(spreadsheet_id, range_name)
    return str(result)

@mcp.tool(name="read-document")
async def read_document(document_id: str) -> str:
    """
    Read content from a Google Doc.
    Usage: read-document|document_id="1234..."
    """
    result = await drive_service.read_document(document_id)
    return str(result)

@mcp.tool(name="update-spreadsheet")
async def update_spreadsheet(spreadsheet_id: str, range_name: str, values: List[List]) -> str:
    """
    Update content in an existing Google Spreadsheet.
    Usage: update-spreadsheet|spreadsheet_id="1234..."|range_name="Sheet1!A1"|values=[["New", "Values"]]
    """
    result = await drive_service.update_spreadsheet(spreadsheet_id, range_name, values)
    return str(result)

@mcp.tool(name="update-document")
async def update_document(document_id: str, content: str) -> str:
    """
    Update content in a Google Doc.
    Usage: update-document|document_id="1234..."|content="New content"
    """
    result = await drive_service.update_document(document_id, content)
    return str(result)

@app.get("/test")
async def test():
    """Test endpoint to verify the server is running."""
    return {"message": "Hello from Google Drive SSE MCP server!"}

@app.get("/list_tools")
async def list_tools():
    """List all registered MCP tools"""
    tools = mcp.list_tools()
    tools_dict = [t.dict() if hasattr(t, "dict") else t for t in tools]
    return JSONResponse(content=tools_dict)

# Mount the SSE MCP server
app.mount("/", mcp.sse_app())