# Telegram SSE Server

> **⚠️ Disclaimer**: This is an educational project created for learning purposes. While the system is designed to be functional, it is not guaranteed to work in all scenarios or environments. Users should exercise caution when using the system with real data and services.

A Server-Sent Events (SSE) server implementation for Telegram integration, providing real-time messaging capabilities through a Message Control Protocol (MCP) interface.

## 🌟 Features

- **Messaging**
  - Send messages to Telegram users
  - Receive messages from Telegram users
  - Real-time message processing
  - Chat ID management
  - Message queue handling

- **Technical Features**
  - Server-Sent Events (SSE) support
  - FastAPI-based implementation
  - Python-telegram-bot integration
  - Asynchronous message handling
  - Real-time message queuing

## 🏗️ Project Structure

```bash
mcp-sse-telegram/
├── telegram_sse_server.py    # Main SSE server implementation
├── telegram_sse_test_client.py  # Test client
├── chat_ids.json            # Chat ID storage
└── .telegram_token.txt      # Telegram bot token
```

## 🚀 Getting Started

### Prerequisites

1. **Telegram Bot Setup**
   - Create a new bot using BotFather on Telegram
   - Get the bot token
   - Save the token in `.telegram_token.txt`

2. **Required Files**
   - `.telegram_token.txt` (Telegram bot token)
   - `chat_ids.json` (will be created automatically)

### Installation

1. **Set up Telegram token**
   ```bash
   echo "your_telegram_bot_token" > .telegram_token.txt
   ```

2. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   uv run uvicorn telegram_sse_server:app --reload --port 8002
   ```

### Testing the Server

1. **Run the test client**
   ```bash
   uv run python telegram_sse_test_client.py
   ```

2. **Test endpoints**
   - `/test` - Basic server test
   - `/list_tools` - List available tools
   - `/sse` - SSE endpoint for MCP communication

## 🛠️ Available Tools

1. **send-telegram-message**
   ```bash
   Usage: send-telegram-message|text="Hello from the agent!"
   ```

2. **get-next-telegram-message**
   ```bash
   Usage: get-next-telegram-message
   Returns: {"user_id": int, "text": str}
   ```

## 🔧 Configuration

The server can be configured through environment variables:

- `PORT` - Server port (default: 8002)
- `TELEGRAM_TOKEN` - Telegram bot token (can be set in `.telegram_token.txt`)

## 🚨 Troubleshooting

- If authentication fails:
  - Check if `.telegram_token.txt` is properly placed
  - Verify the bot token is valid
  - Ensure the bot is properly initialized with BotFather

- If server fails to start:
  - Check if port 8002 is available
  - Verify all dependencies are installed
  - Check if the bot token is properly formatted

- If messages aren't being received:
  - Verify the bot is running
  - Check if the chat ID is properly stored
  - Ensure the message queue is functioning

## 📝 Notes

- The server requires a valid Telegram bot token
- Chat IDs are stored automatically when messages are received
- Messages are processed in real-time
- The server maintains a message queue for incoming messages
- All operations are logged for debugging purposes
- The server supports both sending and receiving messages