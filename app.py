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
    "help": "Sure! I can chat, answer basic questions, and help with study topics.",
    "how are you": "I'm doing great! Thanks for asking 😊",
    "thank you": "You're welcome! Happy to help! 😊",
    "thanks": "No problem! Anytime! 👍"
}

# -------- Simple Domain Knowledge --------
dsai_knowledge = {
    "python": "Python is widely used in data science, AI, automation & web development.",
    "machine learning": "Machine Learning lets computers learn patterns from data without explicit programming.",
    "data science": "Data Science involves collecting, cleaning, analyzing & visualizing data to make decisions.",
    "flask": "Flask is a lightweight Python web framework — perfect for small APIs & projects.",
    "html": "HTML stands for HyperText Markup Language — used for website structure.",
    "javascript": "JavaScript adds interactivity to websites and runs in the browser.",
    "database": "Databases store and organize data. Popular ones include MySQL, PostgreSQL, and MongoDB.",
    "api": "API (Application Programming Interface) lets different software communicate with each other.",
    "algorithm": "An algorithm is a step-by-step procedure to solve a problem or perform a task."
}

# -------- Conversation Memory (Simple) --------
conversation_history = {}

# -------- AI Features (Pure Python - No External Libraries) --------

def simple_sentiment(text):
    """Detect sentiment using word lists - no external library needed"""
    positive_words = ['good', 'great', 'awesome', 'love', 'excellent', 'happy', 'nice', 'wonderful', 'amazing', 'best', 'perfect']
    negative_words = ['bad', 'hate', 'terrible', 'awful', 'worst', 'horrible', 'annoying', 'sad', 'angry', 'frustrated']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"

def calculate_similarity(str1, str2):
    """Calculate similarity between two strings (for typo detection)"""
    str1, str2 = str1.lower(), str2.lower()
    
    # Simple character matching
    matches = sum(1 for a, b in zip(str1, str2) if a == b)
    max_len = max(len(str1), len(str2))
    
    if max_len == 0:
        return 0
    
    return (matches / max_len) * 100

def fuzzy_match(user_input, knowledge_base, threshold=60):
    """Find closest match even with typos - pure Python implementation"""
    best_match = None
    best_score = 0
    
    for key in knowledge_base.keys():
        # Check if key is substring or vice versa
        if key in user_input or user_input in key:
            score = 90
        else:
            score = calculate_similarity(user_input, key)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = key
    
    if best_match:
        return knowledge_base[best_match], best_score
    return None, 0

def detect_question(text):
    """Check if text is a question"""
    question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'is', 'are', 'do', 'does']
    text_lower = text.lower()
    
    # Check for question mark
    if '?' in text:
        return True
    
    # Check if starts with question word
    first_word = text_lower.split()[0] if text_lower.split() else ''
    return first_word in question_words

def detect_greeting(text):
    """Check if text is a greeting"""
    greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    text_lower = text.lower()
    return any(greet in text_lower for greet in greetings)

def detect_farewell(text):
    """Check if text is a goodbye"""
    farewells = ['bye', 'goodbye', 'see you', 'later', 'bye bye']
    text_lower = text.lower()
    return any(fare in text_lower for fare in farewells)

def detect_gratitude(text):
    """Check if text is thanking"""
    thanks = ['thank', 'thanks', 'thx', 'appreciate']
    text_lower = text.lower()
    return any(thank in text_lower for thank in thanks)

def get_user_history(user_id):
    """Get conversation history for a user"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]

def add_to_history(user_id, message):
    """Add message to user's history (keep last 5)"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append(message.lower())
    
    # Keep only last 5 messages
    if len(conversation_history[user_id]) > 5:
        conversation_history[user_id] = conversation_history[user_id][-5:]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    user_id = data.get("user_id", "default_user")  # Simple user tracking
    
    if not user_message:
        return jsonify({"reply": "Please say something! 😊"})
    
    user_lower = user_message.lower()
    
    # Add to history
    add_to_history(user_id, user_message)
    history = get_user_history(user_id)
    
    # Analyze message
    sentiment = simple_sentiment(user_message)
    is_question = detect_question(user_message)
    is_greeting = detect_greeting(user_message)
    is_farewell = detect_farewell(user_message)
    is_gratitude = detect_gratitude(user_message)
    
    # -------- Response Logic --------
    
    # 1. Check greetings first
    if is_greeting:
        for keyword, reply in faq_answers.items():
            if keyword in user_lower:
                return jsonify({
                    "reply": reply,
                    "sentiment": sentiment,
                    "type": "greeting"
                })
    
    # 2. Check farewells
    if is_farewell:
        return jsonify({
            "reply": "Goodbye! 👋 Keep learning & keep building!",
            "sentiment": sentiment,
            "type": "farewell"
        })
    
    # 3. Check gratitude
    if is_gratitude:
        return jsonify({
            "reply": "You're very welcome! 😊 Anything else I can help with?",
            "sentiment": sentiment,
            "type": "gratitude"
        })
    
    # 4. Check exact FAQ matches
    for keyword, reply in faq_answers.items():
        if keyword in user_lower:
            if sentiment == "negative":
                reply += " (I sense you might be frustrated 😟)"
            return jsonify({
                "reply": reply,
                "sentiment": sentiment,
                "type": "faq"
            })
    
    # 5. Check exact domain knowledge
    for keyword, reply in dsai_knowledge.items():
        if keyword in user_lower:
            return jsonify({
                "reply": reply,
                "sentiment": sentiment,
                "type": "knowledge"
            })
    
    # 6. Try fuzzy matching (typo handling)
    all_knowledge = {**faq_answers, **dsai_knowledge}
    fuzzy_result, score = fuzzy_match(user_lower, all_knowledge)
    
    if fuzzy_result and score > 60:
        return jsonify({
            "reply": f"{fuzzy_result} 🎯",
            "sentiment": sentiment,
            "confidence": f"{int(score)}%",
            "type": "fuzzy_match"
        })
    
    # 7. Context awareness - check if referring to previous message
    if len(history) > 1 and any(word in user_lower for word in ['that', 'it', 'this']):
        previous = history[-2]
        if len(user_message.split()) < 6:  # Short reference
            return jsonify({
                "reply": f"Still talking about '{previous}'? Tell me specifically what you want to know! 💬",
                "sentiment": sentiment,
                "type": "context"
            })
    
    # 8. Smart fallback based on message type
    if is_question:
        fallback = "That's a great question! 🤔 I don't have that specific info yet, but I'm learning every day!"
    elif sentiment == "negative":
        fallback = "I'm sorry if I couldn't help properly 😟 Can you try rephrasing your question?"
    elif sentiment == "positive":
        fallback = "Glad you're in a good mood! 😊 How else can I assist you?"
    else:
        fallback = f"Interesting! You said: '{user_message}' — I'm still learning about this topic. Ask me about Python, ML, Data Science, or Flask! 💬"
    
    return jsonify({
        "reply": fallback,
        "sentiment": sentiment,
        "type": "fallback"
    })

# -------- Clear History Route --------
@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear conversation history for a user"""
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    
    if user_id in conversation_history:
        conversation_history[user_id] = []
    
    return jsonify({"message": "Conversation history cleared! 🧹"})

# -------- Info Route --------
@app.route('/info', methods=['GET'])
def info():
    """Get chatbot stats"""
    return jsonify({
        "bot_name": "Flask-Bot Enhanced 🤖",
        "features": [
            "✅ Typo detection (fuzzy matching)",
            "✅ Sentiment analysis (positive/negative/neutral)",
            "✅ Intent detection (question/greeting/farewell)",
            "✅ Conversation memory (last 5 messages)",
            "✅ Context awareness",
            "✅ 100% Offline - No APIs!"
        ],
        "total_topics": len(faq_answers) + len(dsai_knowledge),
        "status": "online",
        "tech": "Pure Python - No external AI libraries!"
    })

if __name__ == '__main__':
    app.run(debug=True)