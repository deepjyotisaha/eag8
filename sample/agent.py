# agent.py

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
import warnings

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

    multi_mcp = MultiMCP(server_configs=mcp_servers)
    print("Agent before initialize")
    await multi_mcp.initialize()

    print("🧠 Cortex-R Agent is now ready to go!")

    while True:
        user_input = input("🧑 What do you want to solve today? (type 'exit' to quit) → ")
        if user_input.strip().lower() in {"exit", "quit", ""}:
            print("👋 Goodbye!")
            break

        agent = AgentLoop(
            user_input=user_input,
            dispatcher=multi_mcp
        )

        try:
            final_response = await agent.run()
            print("\n💡 Final Answer:\n", final_response.replace("FINAL_ANSWER:", "").strip())
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
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?
# which course are we teaching on Canvas LMS?

# 