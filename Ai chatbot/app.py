from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -------- Simple Knowledge Base --------
faq_answers = {
    "hello": "Hello! 👋 How can I assist you today?",
    "hi": "Hi 👋! What's up?",
    "who are you": "I'm your local AI chatbot — no API needed 😎",
    "your name": "I'm Flask-Bot 🤖 running completely offline!",
    "bye": "Goodbye! 👋 Keep learning & keep building!",
    "help": "Sure! I can chat, answer basic questions, and help with study topics."
}

# -------- Simple Domain Knowledge --------
dsai_knowledge = {
    "python": "Python is widely used in data science, AI, automation & web development.",
    "machine learning": "Machine Learning lets computers learn patterns from data without explicit programming.",
    "data science": "Data Science involves collecting, cleaning, analyzing & visualizing data to make decisions.",
    "flask": "Flask is a lightweight Python web framework — perfect for small APIs & projects.",
    "html": "HTML stands for HyperText Markup Language — used for website structure."
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user = data.get("message", "").lower()

    # FAQ replies
    for keyword, reply in faq_answers.items():
        if keyword in user:
            return jsonify({"reply": reply})

    # Domain knowledge replies
    for keyword, reply in dsai_knowledge.items():
        if keyword in user:
            return jsonify({"reply": reply})

    # fallback simple response
    return jsonify({"reply": f"I didn’t fully get that 😅 but you said: {user}"})


if __name__ == '__main__':
    app.run(debug=True)
