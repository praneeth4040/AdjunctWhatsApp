# =========================
# Standard Library Imports
# =========================
import os
import logging

# =========================
# Third-Party Imports
# =========================
import google.generativeai as genai

# =========================
# Local Imports
# =========================
from gemini_prompt import SYSTEM_PROMPT
from llm.tool_dispatcher import dispatch_tool_call
from tools.reminder import set_reminder

# =========================
# Logging Configuration
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Gemini API Configuration
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# =========================
# Gemini Tool Registration
# =========================
tools = [
    {
        "function": set_reminder,
        "name": "set_reminder",
        "description": "Set a reminder for the user. Supports absolute and relative times.",
        "parameters": {
            "event": {
                "type": "string",
                "description": "The event to remind the user about."
            },
            "time_str": {
                "type": "string",
                "description": "The time for the reminder, e.g., '5:30pm', 'after 1 min', 'in 2 hours'."
            }
        }
    }
]

# =========================
# Gemini Model Initialization
# =========================
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=tools,
    system_instruction=SYSTEM_PROMPT
)

# =========================
# AI Response Function
# =========================
def ai_response(user_message: str):
    try:
        logger.info(f"User message: {user_message}")
        
        response = model.generate_content(user_message)

        # Check for tool calls
        if response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "function_call") and candidate.function_call:
                    tool_call = candidate.function_call
                    tool_name = tool_call.name
                    tool_args = tool_call.args
                    logger.info(f"Tool call detected: {tool_name} with args: {tool_args}")
                    # Dispatch the tool call
                    result = dispatch_tool_call(tool_name, tool_args)
                    return {
                        "response": f"Tool `{tool_name}` executed.",
                        "tool_result": result
                    }

        # If no tool call, return normal text
        return {
            "response": response.text
        }

    except Exception as e:
        logger.exception("Error generating AI response")
        return {
            "error": f"An error occurred: {str(e)}"
        }
