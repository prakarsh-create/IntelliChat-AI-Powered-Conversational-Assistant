from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend (JS) to talk with backend (Flask)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Dummy bot logic for now
    if "hello" in user_message.lower():
        bot_reply = "Hi there! 👋 How can I help you?"
    elif "name" in user_message.lower():
        bot_reply = "I’m your AI chatbot built with Flask + JS!"
    elif "bye" in user_message.lower():
        bot_reply = "Goodbye! 👋 Have a nice day!"
    else:
        bot_reply = f"You said: {user_message}"

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
