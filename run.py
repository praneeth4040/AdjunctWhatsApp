from flask import Flask, request, abort, jsonify
from webhook_server import extract_user_message,extract_sender
from test_gemini import ai_response
from message import send_message , get_text_message_input
from dbfunction import insertUser

from chat_db import save_message, get_recent_chat_history
from memory_db import store_user_memory, get_user_memories

app = Flask(__name__)

VERIFY_TOKEN = 'yoyo'  # Change this to your actual verify token

# Helper to build prompt from context

def build_prompt_from_context(context):
    prompt = ""
    for entry in context:
        role = entry.get("role", "user")
        content = entry.get("content", "")
        if role == "user":
            prompt += f"User: {content}\n"
        else:
            prompt += f"Bot: {content}\n"
    return prompt

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
            msg=extract_user_message(request.json)
            sender=extract_sender(request.json)
            insertUser(sender)
            save_message(sender, msg, True)
            # Use only recent chat history (last 4 hours)
            history = get_recent_chat_history(sender, limit=10, hours=4)
            previous_message = history[-1]["message"] if history else ""
            # Improved user-driven memory
            lowered = msg.lower()
            memory_reply = None
            if "remember this" in lowered:
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
            # Chat continuation: fetch last N messages (already done above)
            context = []
            for entry in history:
                role = "user" if entry["is_user"] else "assistant"
                context.append({"role": role, "content": entry["message"]})
            context.append({"role": "user", "content": msg})
            # Inject only stored memories and chat history
            memories = get_user_memories(sender)
            prompt = ""
            if memories:
                prompt += "Here are things the user asked you to remember:\n"
                for mem in memories:
                    prompt += f"- {mem}\n"
            prompt += build_prompt_from_context(context)
            ai_reponse=ai_response(sender, prompt)
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
