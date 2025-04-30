# Cortex-R Agent (EAG8)

> **⚠️ Disclaimer**: This is an educational project created for learning purposes. While the system is designed to be functional, it is not guaranteed to work in all scenarios or environments. Users should exercise caution when using the system with real data and services.

A powerful, modular AI agent system that can process user queries through multiple interaction channels (CLI and Telegram) and execute complex tasks using a variety of tools.

## 🌟 Features

- **Multi-Channel Support**
  - Command Line Interface (CLI)
  - Telegram Bot Integration
  
- **Intelligent Processing**
  - Context-aware task handling
  - Memory management with semantic search
  - Step-by-step task decomposition
  - Tool-based problem solving

- **Core Components**
  - Perception Module (intent & entity extraction)
  - Memory Management (with FAISS integration)
  - Decision Making Engine
  - Flexible Tool Integration
  - Multi-MCP (Multiple Message Control Protocol) Support

## 🏗️ Project Structure

```bash
agent_e8/                   # Main Agent
├── README.md              # Project documentation
├── agent.py              # Main agent entry point
├── pyproject.toml        # Project dependencies
├── .python-version       # Python version spec
├── uv.lock              # Dependency lock file
├── .gitignore           # Git ignore rules
│
├── core/                # Core components
│   ├── context.py       # Session context
│   ├── loop.py          # Main agent loop
│   ├── session.py       # MCP session handling
│   ├── sse_client.py    # SSE client
│   └── strategy.py      # Decision strategies
│
├── modules/             # Functional modules
│   ├── action.py        # Tool execution
│   ├── decision.py      # Planning logic
│   ├── memory.py        # Memory management
│   ├── model_manager.py # ML model management
│   ├── perception.py    # Input analysis
│   └── tools.py         # Tool definitions
│
├── mcp_server/          # MCP server implementations
│   ├── mcp_server_1.py  # Server implementation 1
│   ├── mcp_server_2.py  # Server implementation 2
│   ├── mcp_server_3.py  # Server implementation 3
│   ├── models.py        # Server models
│   ├── documents/       # Document storage
│   └── faiss_index/     # FAISS index storage
│
├── config/              # Configurations
│   ├── profiles.yaml    # Agent and server profiles
│   ├── log_config.py    # Logging configuration
│   └── models.json      # Model configurations
│
├── logs/               # Log files
│
├── How to use Canvas LMS.pdf  # Documentation
└── sample.zip          # Sample files

mcp-sse-telegram/           # Telegram SSE Server
├── telegram_sse_server.py  # Main Telegram server
├── telegram_sse_test_client.py  # Test client
└── .telegram_token.txt     # Telegram bot token

mcp-sse-gmail/              # Gmail SSE Server
├── src/
│   └── gmail/
│       ├── gmail_sse_server.py    # Main Gmail server
│       ├── gmail_mcp_server.py    # MCP server implementation
│       └── gmail_sse_test_client.py  # Test client
└── .google/               # Google credentials
    ├── client_creds.json  # OAuth credentials
    └── tokens.json        # Access tokens

mcp-sse-gdrive/            # Google Drive SSE Server
├── src/
│   └── mcp_sse_gdrive/
│       ├── google_drive_sse_server.py  # Main Drive server
│       └── google_drive_service.py     # Drive service implementation
├── google_drive_sse_test_client.py     # Test client
└── .google/               # Google credentials
    ├── client_creds.json  # OAuth credentials
    └── drive_tokens.json  # Drive access tokens
```

## 🚀 Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent_e8
   ```

2. **Validate server settings in `config/profiles.yaml`**
   ```yaml
   agent:
     name: "Cortex-R"
     id: "cortex-r-1"
     description: "Intelligent agent for task processing"
   
   interaction_channel: "Telegram"  # Set to Telegram for this example
   
   mcp_servers:
     - url: "http://localhost:8001"  # Gmail SSE Server
       type: "sse"
       name: "gmail"
     - url: "http://localhost:8002"  # Telegram SSE Server
       type: "sse"
       name: "telegram"
     - url: "http://localhost:8003"  # Google Drive SSE Server
       type: "sse"
       name: "drive"
   ```

3. **Set up authentication**
   ```bash
   # Create .google directory and place credentials
   mkdir .google
   # Place client_creds.json in .google/
   
   # Set up Telegram token
   echo "your_telegram_bot_token" > .telegram_token.txt
   
   # Set up Gemini API key
   echo "GEMINI_API_KEY=your_key_here" > .env
   ```

4. **Install dependencies using UV**
   ```bash
   uv pip install -r requirements.txt
   ```

### Example Usage

1. **Start the system** (in separate terminal windows):
   ```bash
   # Terminal 1 - Gmail Server
   uv run uvicorn mcp-sse-gmail.src.gmail.gmail_sse_server:app --port 8001

   # Terminal 2 - Telegram Server
   uv run uvicorn mcp-sse-telegram.telegram_sse_server:app --port 8002

   # Terminal 3 - Google Drive Server
   uv run uvicorn mcp-sse-gdrive.src.mcp_sse_gdrive.google_drive_sse_server:app --port 8003

   # Terminal 4 - Main Agent
   uv run python agent.py
   ```

2. **Interact with the agent**:
   - Open Telegram and find your bot
   - Send the following message:
   ```
   Find the current point standings of F1 Racers from the internet and update the results into a spreadsheet in Google Drive, and then share the link to this spreadsheet with me on deepjyoti.saha@gmail.com.
   ```

3. **Monitor the process**:
   - The agent will:
     1. Search for F1 standings
     2. Create/update a Google Spreadsheet
     3. Send you an email with the spreadsheet link
   - Check your email for the results

### Troubleshooting

- If servers fail to start:
  - Check if ports 8001-8003 are available
  - Verify all API keys and credentials are set
  - Ensure all required dependencies are installed with UV


```