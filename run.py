from flask import Flask, request, abort, jsonify
from webhook_server import extract_user_message,extract_sender
from test_gemini import ai_response
from message import send_message
from whatsapp_utils.message_types import get_text_message_input
from dbfunction import insertUser
from chat_db import save_message, get_recent_chat_history
from memory_db import store_user_memory, get_user_memories
from gemini_prompt import SYSTEM_PROMPT

app = Flask(__name__)

VERIFY_TOKEN = 'yoyo'  # Change this to your actual verify token

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        try:
            msg = extract_user_message(request.json)
            sender = extract_sender(request.json)
            insertUser(sender)
            save_message(sender, msg, True)
            # Fetch recent chat history for this user (last 10 messages, last 4 hours)
            history = get_recent_chat_history(sender, limit=10, hours=4)
            if not history:
                history = []
            # Build context: system prompt + history + current message
            context = [SYSTEM_PROMPT]
            for entry in history:
                role = "User" if entry["is_user"] else "Bot"
                context.append(f"{role}: {entry['message']}")
            context.append(f"User: {msg}")

            # --- Static memory logic: only store if user says 'remember' ---
            lowered = msg.lower()
            memory_reply = None
            if "remember this" in lowered:
                previous_message = history[-2]["message"] if len(history) > 1 else ""
                if previous_message:
                    store_user_memory(sender, previous_message)
                    memory_reply = "Okay, I've remembered that."
                else:
                    memory_reply = "There's nothing to remember."
            elif "remember" in lowered:
                to_remember = msg.split("remember",1)[-1].strip()
                if to_remember:
                    store_user_memory(sender, to_remember)
                    memory_reply = "Okay, I've remembered that."
                else:
                    memory_reply = "What would you like me to remember?"
            if memory_reply:
                send_message(get_text_message_input(sender, memory_reply))
                save_message(sender, memory_reply, False)
                return jsonify({'status': 'success'}), 200

            # Send context to LLM
            ai_reponse = ai_response(sender, context)
            save_message(sender, ai_reponse, False)
            if isinstance(ai_reponse, dict):
                message_text = str(ai_reponse.get("result", str(ai_reponse)))
            else:
                message_text = str(ai_reponse)
            send_message(get_text_message_input(sender, message_text))
        except Exception as e:
            print(e)
        return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
