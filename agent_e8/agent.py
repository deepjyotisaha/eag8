# agent.py

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
import warnings
import os

from config.log_config import setup_logging

logger = setup_logging(__name__)

warnings.filterwarnings("ignore", category=ResourceWarning)

def log(stage: str, msg: str):
    """Simple timestamped console logger."""
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")


async def main():
    print("🧠 Cortex-R Agent getting ready...")

    # Load MCP server configs from profiles.yaml
    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers = profile.get("mcp_servers", [])
        interaction_channel = profile.get("interaction_channel", "CLI")

    print("interaction_channel:", interaction_channel)

    multi_mcp = MultiMCP(server_configs=mcp_servers)
    print("Agent before initialize")
    await multi_mcp.initialize()

    print("🧠 Cortex-R Agent is now ready to go and is listening for messages from the user at:", interaction_channel)

    while True:
        if interaction_channel == "CLI":
            user_input = input("🧑 What do you want to solve today? (type 'exit' to quit) → ")
            # === CLI Mode ===
        elif interaction_channel == "Telegram":
            try:
                user_input = input("🧑 What do you want to solve today? (type 'exit' to quit) → ")
                result = await multi_mcp.call_tool("get-next-telegram-message", {})
                user_input = result.content[0].text
                print(f"Telegram message: {user_input}")
            except Exception as e:
                print(f"Error polling Telegram: {e}")
                await asyncio.sleep(2)  

        if user_input.strip().lower() in {"exit", "quit", ""}:
            print("👋 Goodbye!")
            break

        agent = AgentLoop(
            user_input=user_input,
            dispatcher=multi_mcp
        )

        try:
            final_response = await agent.run()
            print("final_response:", final_response)
            if interaction_channel == "CLI":
                print("\n💡 Final Answer:\n", final_response.replace("FINAL_ANSWER:", "").strip())
            elif interaction_channel == "Telegram":
                print("Attempting to send telegram message")
                try:
                    print(f"Calling send-telegram-message with message: {final_response.replace('FINAL_ANSWER:', '').strip()}")
                    await multi_mcp.call_tool("send-telegram-message", {
                        "text": final_response.replace("FINAL_ANSWER:", "").strip()
                    })
                    print("Sending message to telegram completed")
                except Exception as e:
                    print(f"Error in sending telegram message: {str(e)}")
        except Exception as e:
            log("fatal", f"Agent failed: {e}")
            raise

    await multi_mcp.shutdown()



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))  # Give time for cleanup
        loop.close()

# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? (This uses RAG)
# What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? (This runs the log funtion via python code)
# Summarize this page: https://theschoolof.ai/ (This uses search and summarize)
# What is this document all about? Can you summarize it for me? "C:\Users\dsaha\OneDrive - Microsoft\Documents\Personal\deep\study\artificial intelligence\eagv1\eag8\sample\How to use Canvas LMS.pdf" (This uses PDF)
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?
# which course are we teaching on Canvas LMS?
# Find the current point standings of F1 Racers from the internet, and update the results into a spreadsheet in Google Drive, and then share the link to this spreadsheet with me on deepjyoti.saha@gmail.com. While wriiing the result into the spreadsheet, first check if a spreadsheet already exists in Google Drive, with a similar name, if yes, then update the results in the existing spreadsheet with the new results, make sure to update the exact cells; else if no spreadsheet exists, then create a new spreadsheet and update the results; Your email should be well formatted in HTML format.

#- ✅ When searching rely on first reponse from tools, as that is the best response probably. However, ALWAYS check if the response is already available in memory via a previous tool call with same parameters, as that is the most efficient use of time and resources.

#Find the current point standings of F1 Racers from the internet and update the results into a spreadsheet in Google Drive, and then share the link to this spreadsheet with me on deepjyoti.saha@gmail.com. Update the final answer with the text only message in Telegram.


