# Gmail SSE Server

> **⚠️ Disclaimer**: This is an educational project created for learning purposes. While the system is designed to be functional, it is not guaranteed to work in all scenarios or environments. Users should exercise caution when using the system with real data and services.

A Server-Sent Events (SSE) server implementation for Gmail integration, providing real-time email management capabilities through a Message Control Protocol (MCP) interface.

## 🌟 Features

- **Email Management**
  - Send emails with HTML support
  - Retrieve unread emails
  - Read email contents
  - Mark emails as read
  - Open emails in browser
  - Move emails to trash

- **Technical Features**
  - Server-Sent Events (SSE) support
  - FastAPI-based implementation
  - OAuth 2.0 authentication
  - Real-time email processing
  - HTML and plain text email support

## 🏗️ Project Structure

```bash
mcp-sse-gmail/
├── src/
│   └── gmail/
│       ├── gmail_sse_server.py    # Main SSE server implementation
│       ├── gmail_mcp_server.py    # MCP server implementation
│       └── gmail_sse_test_client.py  # Test client
└── .google/               # Google credentials
    ├── client_creds.json  # OAuth credentials
    └── tokens.json        # Access tokens
```

## 🚀 Getting Started

### Prerequisites

1. **Google Cloud Project Setup**
   - Create a Google Cloud Project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials as `client_creds.json`

2. **Required Files**
   - `.google/client_creds.json` (OAuth credentials)
   - `.google/tokens.json` (will be created on first run)

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
   uv run uvicorn src.gmail.gmail_sse_server:app --reload --port 8001
   ```

### Testing the Server

1. **Run the test client**
   ```bash
   uv run python src/gmail/gmail_sse_test_client.py
   ```

2. **Test endpoints**
   - `/test` - Basic server test
   - `/list_tools` - List available tools
   - `/sse` - SSE endpoint for MCP communication

## 🛠️ Available Tools

1. **send-email**
   ```bash
   Usage: send-email|recipient_id="someone@example.com"|subject="Hello"|message="Body text"
   ```

2. **get-unread-emails**
   ```bash
   Usage: get-unread-emails
   ```

3. **read-email**
   ```bash
   Usage: read-email|email_id="abc123"
   ```

4. **mark-email-as-read**
   ```bash
   Usage: mark-email-as-read|email_id="abc123"
   ```

5. **open-email**
   ```bash
   Usage: open-email|email_id="abc123"
   ```

## 🔧 Configuration

The server can be configured through environment variables:

- `PORT` - Server port (default: 8001)
- `GMAIL_SCOPES` - Gmail API scopes (default: ['https://www.googleapis.com/auth/gmail.modify'])

## 🚨 Troubleshooting

- If authentication fails:
  - Check if `client_creds.json` is properly placed
  - Verify OAuth scopes are correct
  - Delete `app_tokens.json` to force re-authentication

- If server fails to start:
  - Check if port 8001 is available
  - Verify all dependencies are installed
  - Check Google API quota limits

## 📝 Notes

- The server requires initial OAuth authentication on first run
- Email operations are performed in real-time
- HTML emails are supported with fallback to plain text
- All operations are logged for debugging purposes