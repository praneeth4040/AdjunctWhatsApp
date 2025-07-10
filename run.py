from flask import Flask, request, abort, jsonify
from webhook_server import extract_user_message,extract_sender
from test_gemini import ai_response
from message import send_message , get_text_message_input

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
            msg=extract_user_message(request.json)
            sender=extract_sender(request.json)
            print(msg,sender)
            ai_reponse=ai_response(msg)
            send_message(get_text_message_input(sender,ai_reponse))
        except Exception as e:
            print(e)

        return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
