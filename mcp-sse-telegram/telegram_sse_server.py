from fastapi import FastAPI, Request, Body
from fastapi.responses import StreamingResponse, JSONResponse
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import json
import os
from fastmcp import FastMCP
#from fastmcp.models import ToolCall
#from fastmcp.types import ToolCall

def load_telegram_token():
    with open(".telegram_token.txt", "r") as f:
        return f.read().strip()

mcp: FastMCP = FastMCP("TelegramApp")
app = FastAPI()
messages = asyncio.Queue()
pending_telegram_messages = asyncio.Queue()

TELEGRAM_TOKEN = load_telegram_token()

last_chat_id = None

# Handler for incoming Telegram messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    text = update.message.text
    last_chat_id = update.message.chat_id
    print(f"Received message from {last_chat_id}: {text}")
    await pending_telegram_messages.put({"user_id": last_chat_id, "text": text})

@app.on_event("startup")
async def startup_event():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()
    asyncio.create_task(application.start())
    asyncio.create_task(application.updater.start_polling())


@mcp.tool(name="telegram-query")
async def telegram_query(user_id: int, text: str) -> str:
    """
    Triggered by a Telegram message.

    Arguments:
        user_id (int): The Telegram user ID who sent the message.
        text (str): The message text.

    Usage:
        telegram-query|user_id=123456|text="Hello"
    """
    return f"Received from {user_id}: {text}"

@mcp.tool(name="send-telegram-message")
async def send_telegram_message(text: str) -> str:
    """
    Send a message to the Telegram bot's chat.

    Arguments:
        text (str): The message to send.

    Usage:
        send-telegram-message|text="Hello from the agent!"
    """
    global last_chat_id
    if not last_chat_id:
        return "No chat_id available"
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.send_message(chat_id=last_chat_id, text=text)
    #await messages.put({"user_id": last_chat_id, "text": f"[BOT]: {text}"})
    return f"The following message: {text} was sent to user_id:{last_chat_id}"

@mcp.tool(name="get-next-telegram-message")
async def get_next_telegram_message() -> dict:
    """
    Fetch the next pending Telegram message.

    Usage:
        get-next-telegram-message

    Returns:
        dict: {"user_id": int, "text": str}
    """
    msg = await pending_telegram_messages.get()
    print("msg:", msg)
    return msg

@app.get("/test")
async def test():
    """Test endpoint to verify the server is running."""
    return {"message": "Hello from Telegram SSE MCP server!"}

@app.get("/list_tools")
async def list_tools():
    # List all registered MCP tools
    tools = mcp.list_tools()
    # Convert to dict if needed
    tools_dict = [t.dict() if hasattr(t, "dict") else t for t in tools]
    return JSONResponse(content=tools_dict)

app.mount("/", mcp.sse_app())