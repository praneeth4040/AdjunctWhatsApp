
import os
import google.generativeai as genai
from gemini_prompt import SYSTEM_PROMPT

# If using environment variable or hardcoded key
GEMINI_API_KEY ="AIzaSyDwd6q4S4RjgbUzDAeq78rQjj0M3wXU6VU"
genai.configure(api_key=GEMINI_API_KEY)


def ai_response(user_message):
    prompt = SYSTEM_PROMPT + "\nUser: " + user_message
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    user_message = input("Enter your message: ")
    reply = ai_response(user_message)
    print("AI Response:", reply) 