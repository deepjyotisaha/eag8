from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import json
import os
from fastmcp import FastMCP

def load_telegram_token():
    with open(".telegram_token.txt", "r") as f:
        return f.read().strip()

mcp: FastMCP = FastMCP("App")

app = FastAPI()
messages = asyncio.Queue()

TELEGRAM_TOKEN = load_telegram_token()

# Handler for incoming Telegram messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    print(f"Received message from {user_id}: {text}")
    await messages.put({"user_id": user_id, "text": text})

@app.on_event("startup")
async def startup_event():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()
    asyncio.create_task(application.start())
    asyncio.create_task(application.updater.start_polling())

@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_generator():
        while True:
            msg = await messages.get()
            yield f"data: {json.dumps(msg)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/list_tools")
async def list_tools():
    # Expose a single tool: "telegram_query"
    return JSONResponse(content=[
        {
            "name": "telegram_query",
            "description": "Triggered by a Telegram message. Arguments: {'user_id': int, 'text': str}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "text": {"type": "string"}
                },
                "required": ["user_id", "text"]
            }
        }
    ])

@app.post("/send_message")
async def send_message(user_id: int, text: str):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.send_message(chat_id=user_id, text=text)
    return {"status": "sent"}

app.mount("/", mcp.sse_app())