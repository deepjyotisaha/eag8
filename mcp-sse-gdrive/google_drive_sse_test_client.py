# google_drive_sse_test_client.py

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx
import json
from datetime import datetime
import ast

# Configuration
SERVER_URL = "http://localhost:8003"

def format_timestamp(timestamp_str):
    """Convert ISO timestamp to readable format"""
    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_file_list(files_str):
    """Format the file list in a readable way"""
    try:
        # Convert string representation of list to actual list
        if isinstance(files_str, str):
            files = ast.literal_eval(files_str)
        else:
            files = files_str

        # Group files by type
        docs = []
        sheets = []
        others = []

        for file in files:
            file_info = {
                'name': file['name'],
                'id': file['id'],
                'created': format_timestamp(file['createdTime']),
                'modified': format_timestamp(file['modifiedTime'])
            }
            
            if file['mimeType'] == 'application/vnd.google-apps.document':
                docs.append(file_info)
            elif file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                sheets.append(file_info)
            else:
                others.append(file_info)

        # Print formatted results
        output = []
        
        if docs:
            output.append("\n📄 Google Docs:")
            for doc in sorted(docs, key=lambda x: x['modified'], reverse=True):
                output.append(f"  • {doc['name']}")
                output.append(f"    ID: {doc['id']}")
                output.append(f"    Created: {doc['created']}")
                output.append(f"    Last Modified: {doc['modified']}\n")

        if sheets:
            output.append("\n📊 Google Sheets:")
            for sheet in sorted(sheets, key=lambda x: x['modified'], reverse=True):
                output.append(f"  • {sheet['name']}")
                output.append(f"    ID: {sheet['id']}")
                output.append(f"    Created: {sheet['created']}")
                output.append(f"    Last Modified: {sheet['modified']}\n")

        if others:
            output.append("\n📁 Other Files:")
            for other in sorted(others, key=lambda x: x['modified'], reverse=True):
                output.append(f"  • {other['name']}")
                output.append(f"    ID: {other['id']}")
                output.append(f"    Created: {other['created']}")
                output.append(f"    Last Modified: {other['modified']}\n")

        return "\n".join(output)
    except Exception as e:
        return f"Error formatting file list: {str(e)}"

def format_creation_result(result_str):
    """Format the creation result in a readable way"""
    try:
        if isinstance(result_str, str):
            result = ast.literal_eval(result_str)
        else:
            result = result_str
            
        if result.get("status") == "success":
            output = [
                f"✅ {result['message']}",
                f"📋 ID: {result['spreadsheet_id']}",
                f"🔗 URL: {result['url']}"
            ]
        else:
            output = [f"❌ Error: {result.get('error', 'Unknown error')}"]
            
        return "\n".join(output)
    except Exception as e:
        return f"Error formatting result: {str(e)}"

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

            # Test searching files in Google Drive
            print("Searching files in Google Drive...")
            print("1. Recent Documents and Spreadsheets:")
            search_result = await session.call_tool(
                name="search-files",
                arguments={
                    "query": "mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet' and modifiedTime > '2024-01-01T00:00:00'"
                }
            )
            print(format_file_list(search_result.content[0].text))

            # Test creating a spreadsheet
            print("\nCreating a test spreadsheet...")
            create_result = await session.call_tool(
                name="create-spreadsheet",
                arguments={
                    "title": "Test Spreadsheet",
                    "initial_data": [["Header1", "Header2"], ["Value1", "Value2"]]
                }
            )
            print(format_creation_result(create_result.content[0].text))

            # Test creating a document
            print("\nCreating a test document...")
            doc_result = await session.call_tool(
                name="create-document",
                arguments={
                    "title": "Test Document",
                    "content": "This is a test document created by the SSE client."
                }
            )
            print("Create document result:")
            print(doc_result.content[0].text)

            # Search again to see the newly created files
            print("\nSearching for newly created files:")
            search_result = await session.call_tool(
                name="search-files",
                arguments={
                    "query": f"name contains 'Test' and modifiedTime > '{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}'"
                }
            )
            print(format_file_list(search_result.content[0].text))

            print("\nStandard API Call to /test endpoint")
            res = await httpx.AsyncClient().get(f"{SERVER_URL}/test")
            print(res.json())

if __name__ == "__main__":
    asyncio.run(main())