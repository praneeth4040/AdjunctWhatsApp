from google import genai
from google.genai import types
from llm.tool_dispatcher import dispatch_tool_call

# Define the function declaration for the model
reminder_function = {
    "name": "set_reminder",
    "description": "Set a reminder for the user. Supports absolute and relative times.",
    "parameters": {
        "type": "object",
        "properties": {
            "event": {
                "type": "string",
                "description": "The event to remind the user about."
            },
            "time_str": {
                "type": "string",
                "description": "When to remind the user, e.g., 'in 10 minutes', 'at 5:00pm'."
            }
        },
        "required": ["event", "time_str"]
    }
}

# Configure the client and tools
client = genai.Client()
tools = types.Tool(function_declarations=[reminder_function])
config = types.GenerateContentConfig(tools=[tools])

# Send request with function declarations
def ai_response(user_message):
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_message,
    config=config,
)
    #handling the requested tools
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")
        result = dispatch_tool_call(function_call.name,function_call.args)
        return result
    else:
        print("No function call found in the response.")
        return response.text