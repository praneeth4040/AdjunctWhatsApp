
import os
import google.generativeai as genai

# Load your Gemini API key from .env

GEMINI_API_KEY = "AIzaSyDwd6q4S4RjgbUzDAeq78rQjj0M3wXU6VU"

def ai_response(user_message):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(user_message)
    return response.text

if __name__ == "__main__":
    user_message = input("give prompt : ")
    reply = ai_response(user_message)
    print("AI Response:", reply) 