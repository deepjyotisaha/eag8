from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import json
import os
from fastmcp import FastMCP

mcp: FastMCP = FastMCP("App")

app = FastAPI()
messages = asyncio.Queue()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Set your bot token as an environment variable

# Handler for incoming Telegram messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    await messages.put({"user_id": user_id, "text": text})

def start_telegram_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(start_telegram_bot))

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

app.mount("/", mcp.sse_app())