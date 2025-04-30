# Google Drive SSE Server

> **⚠️ Disclaimer**: This is an educational project created for learning purposes. While the system is designed to be functional, it is not guaranteed to work in all scenarios or environments. Users should exercise caution when using the system with real data and services.

A Server-Sent Events (SSE) server implementation for Google Drive integration, providing real-time file management capabilities through a Message Control Protocol (MCP) interface.

## 🌟 Features

- **File Management**
  - Search files with advanced query syntax
  - Create and update Google Spreadsheets
  - Create and update Google Documents
  - Read spreadsheet and document contents
  - Real-time file operations

- **Technical Features**
  - Server-Sent Events (SSE) support
  - FastAPI-based implementation
  - OAuth 2.0 authentication
  - Support for multiple Google APIs (Drive, Sheets, Docs)
  - Advanced file search capabilities

## 🏗️ Project Structure

```bash
mcp-sse-gdrive/
├── src/
│   └── mcp_sse_gdrive/
│       ├── google_drive_sse_server.py  # 🤖 Main SSE server implementation
│       ├── google_drive_service.py     # Drive service implementation
│       └── __init__.py                 # Package initialization
├── google_drive_sse_test_client.py     # Test client
└── .google/               # Google credentials
    ├── client_creds.json  # OAuth credentials
    └── drive_tokens.json  # Drive access tokens
```

## 🚀 Getting Started

### Prerequisites

1. **Google Cloud Project Setup**
   - Create a Google Cloud Project
   - Enable Google Drive API
   - Enable Google Sheets API
   - Enable Google Docs API
   - Create OAuth 2.0 credentials
   - Download credentials as `client_creds.json`

2. **Required Files**
   - `.google/client_creds.json` (OAuth credentials)
   - `.google/drive_tokens.json` (will be created on first run)

### Installation

1. **Set up credentials**
   ```bash
   mkdir .google
   # Place your client_creds.json in .google/
   ```

2. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   uv run uvicorn src.mcp_sse_gdrive.google_drive_sse_server:app --reload --port 8003
   ```

### Testing the Server

1. **Run the test client**
   ```bash
   uv run python google_drive_sse_test_client.py
   ```

2. **Test endpoints**
   - `/test` - Basic server test
   - `/list_tools` - List available tools
   - `/sse` - SSE endpoint for MCP communication

## 🛠️ Available Tools

1. **search-files**
   ```bash
   Usage: search-files|query="mimeType='application/vnd.google-apps.spreadsheet' and name contains 'F1 Standings'"
   ```

2. **create-spreadsheet**
   ```bash
   Usage: create-spreadsheet|title="My Spreadsheet"|initial_data=[["Header1", "Header2"], ["Value1", "Value2"]]
   ```

3. **create-document**
   ```bash
   Usage: create-document|title="My Document"|content="Initial content"
   ```

4. **read-spreadsheet**
   ```bash
   Usage: read-spreadsheet|spreadsheet_id="1234..."|range_name="Sheet1!A1:B10"
   ```

5. **read-document**
   ```bash
   Usage: read-document|document_id="1234..."
   ```

6. **update-spreadsheet**
   ```bash
   Usage: update-spreadsheet|spreadsheet_id="1234..."|range_name="Sheet1!A1"|values=[["New", "Values"]]
   ```

7. **update-document**
   ```bash
   Usage: update-document|document_id="1234..."|content="New content"
   ```

## 🔧 Configuration

The server can be configured through environment variables:

- `PORT` - Server port (default: 8003)
- `DRIVE_SCOPES` - Google Drive API scopes (default includes drive.file, drive.readonly, spreadsheets, and documents)

## 🚨 Troubleshooting

- If authentication fails:
  - Check if `client_creds.json` is properly placed
  - Verify OAuth scopes are correct
  - Delete `app_tokens.json` to force re-authentication

- If server fails to start:
  - Check if port 8003 is available
  - Verify all dependencies are installed
  - Check Google API quota limits

## 📝 Notes

- The server requires initial OAuth authentication on first run
- File operations are performed in real-time
- Advanced search queries are supported using Google Drive API syntax
- All operations are logged for debugging purposes
- The server supports both Google Sheets and Google Docs operations