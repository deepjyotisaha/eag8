from typing import List, Optional
from modules.perception import PerceptionResult
from modules.memory import MemoryItem
from modules.model_manager import ModelManager
from dotenv import load_dotenv
from google import genai
import os
import asyncio

# Optional: import logger if available
try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

model = ModelManager()


async def generate_plan(
    perception: PerceptionResult,
    memory_items: List[MemoryItem],
    tool_descriptions: Optional[str] = None,
    step_num: int = 1,
    max_steps: int = 3
) -> str:
    """Generates the next step plan for the agent: either tool usage or final answer."""

    memory_texts = "\n".join(f"- {m.text}" for m in memory_items) or "None"
    tool_context = f"\nYou have access to the following tools:\n{tool_descriptions}" if tool_descriptions else ""

    prompt = f"""
Role:
You are a reasoning-driven AI agent with access to tools and memory.

Your job is to solve the user's request step-by-step by reasoning through the problem, selecting a tool if needed, and continuing until the FINAL_ANSWER is produced.

Goal:
Your end goal is to solve the following user's request: "{perception.user_input}"

Here is the approach to solve the user's request:

- Step 1: You first analyze the user's request and break down the user's request into smaller sub-queries.
- Step 2: You then solve each sub-query one by one.
- Step 3: You then save the results of each sub-query in the working memory.
- Step 4: You then combine the results of each sub-query to form the final answer.

Here is how you approach to solve the sub-queries:

- You first analyze the sub-query and determine if you already have the all the information you need from one of the following sources:
  - Factual answer in the working memory
  - Response from the previous tool call
- Next, if needed, you break down the sub-query into smaller sub-queries and solve each sub-query one by one.
- If you need to use a tool, you call the tool with the appropriate parameters, and save the result in the working memory.
- If you already have the final answer in the working memory, you summarize the result and respond with FINAL_ANSWER.
- If you don't have the final answer in the working memory, you continue to solve the next sub-query.


You must also follow these tool specific rules strictly while using the tools:

- Tools which help search information or extract information from sources like documents, pdfs, urls, web etc. 
    - If the question may relate to public/factual knowledge (like companies, people, places), use these tools to extract information.
    - Never use these tools twice for the same source or parameter unless the information obtained is empty
    - Never use these tools to fetch information which is already available in the working memory
    - Never use these tools to fetch information which is already available in the response from the previous tool call unless the information obtained is outdated by more than 1 day, this is applicable only for tools which fetch information from the web.
- Tools which are related to emails:
    - The email should always be well formatted in HTML format., and be very readable.
    - The email should always have a subject, and a body and a message around the content of the email.
- Tools which are related to handling documents in google drive:
    - Never use these tools to fetch or search information
    - Always add a timestamp to the document content so that you/we/everyone knows when the document was created or updated. For spreadsheets, add a timestamp column; for documents, add a timestamp at the end of the document.
    - Before creating a new document, always check if a document with similar name already exists, if it does, use it and udpdate the new information instead of creating a new one. If needed read the information from exsiting document and determine what and where to update - if this is net new information, update in a different location, else if it is the same information, update in the same location.
    - If you are updating a document, always understand the current structure of the document and update the document accordingly. 
    - Your document content should always be formatted. For spreadsheets add column names; For documents, add the header, subheader, paragraph title, etc.
- Math tools:
    - If the question is mathematical, use the appropriate math tool.

You must follow these GENERAL rules strictly:

- 🚫 NEVER invent tools. Use only the tools listed below in the Available Tools section. Tool description has useage pattern, only use that.
- ❌ NEVER repeat tool calls with the same parameters unless the result of the previous tool call with the same parameters was empty. 
- ❌ NEVER repeat tool calls with the same parameters if you have already got a good factual result from memory.
- ❌ NEVER output explanation text — only structured FUNCTION_CALL or FINAL_ANSWER.
- ✅ Use nested keys like `input.string` or `input.int_list`, and square brackets for lists.
- 💡 If no tool fits or you're unsure, end with: FINAL_ANSWER: [unknown]
- ⏳ You have {max_steps} attempts. Final attempt must end with FINAL_ANSWER. Give FINAL_ANSWER only once you have completed all the tasks mentioned in the user's request.

Available Memory:
Now, you have access to the following working memory:
{memory_texts}

Available Tools:
You have access to the following tools:
{tool_context}

Here is some additional context to help you:
- Intent: {perception.intent}
- Entities: {', '.join(perception.entities)}
- Tool hint: {perception.tool_hint or 'None'}

You are currently at step: {step_num} of {max_steps}

Respond in **exactly one line** using one of the following formats:

- FUNCTION_CALL: tool_name|param1=value1|param2=value2
- FINAL_ANSWER: [your final result] *(Not description, but actual final answer)

✅ Examples:
- FUNCTION_CALL: add|input.a=5|input.b=3
- FUNCTION_CALL: strings_to_chars_to_int|input.string=INDIA
- FUNCTION_CALL: int_list_to_exponential_sum|input.int_list=[73,78,68,73,65]
- FINAL_ANSWER: [42] → Always mention final answer to the query, not that some other description.
Follow the examples, and look into the error messages to improve the plan.

✅ Examples:
- User asks: "What’s the relationship between Cricket and Sachin Tendulkar"
  - FUNCTION_CALL: search_documents|query="relationship between Cricket and Sachin Tendulkar"
  - [receives a detailed document]
  - FINAL_ANSWER: [Sachin Tendulkar is widely regarded as the "God of Cricket" due to his exceptional skills, longevity, and impact on the sport in India. He is the leading run-scorer in both Test and ODI cricket, and the first to score 100 centuries in international cricket. His influence extends beyond his statistics, as he is seen as a symbol of passion, perseverance, and a national icon. ]

---

📏 IMPORTANT Rules: YOU MUST FOLLOW THESE RULES STRICTLY.


VERY IMPORTANT RULE:
- ❌ NEVER NEVER USE "|" inside argument values for function calls; if you encounter argument values with "|" especially in the list format, dealing with emails, web content etc., you MUST CHOOSE ALTERNATE SEPERATOR OR FORMATs
For Example:

NEVER SEND THIS:
1. Max Verstappen - 437 | Lando Norris - 374

SEND THIS INSTEAD:

  1. Max Verstappen - 437
  2. Lando Norris - 374
  ...
"""

    #print(f"plan prompt: {prompt}")

    try:
        raw = (await model.generate_text(prompt)).strip()
        log("plan", f"LLM output: {raw}")

        for line in raw.splitlines():
            if line.strip().startswith("FUNCTION_CALL:") or line.strip().startswith("FINAL_ANSWER:"):
                return line.strip()

        return "FINAL_ANSWER: [unknown]"

    except Exception as e:
        log("plan", f"⚠️ Planning failed: {e}")
        return "FINAL_ANSWER: [unknown]"

