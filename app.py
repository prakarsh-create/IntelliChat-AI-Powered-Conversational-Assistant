from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app)

# -------- Load Real AI Model (First time takes 5-10 min) --------
print("🤖 Loading DialoGPT AI model... Please wait...")
print("⏳ First time download: ~350MB (happens only once)")

try:
    model_name = "microsoft/DialoGPT-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Set pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print("✅ AI Model loaded successfully!")
    print(f"✅ Model: {model_name}")
    print("✅ Ready to chat with real AI!\n")
    AI_ENABLED = True
except Exception as e:
    print(f"❌ AI Model loading failed: {e}")
    print("⚠️ Falling back to keyword-based responses")
    AI_ENABLED = False

# -------- Knowledge Base (Backup) --------
faq_answers = {
    "hello": "Hello! 👋 How can I assist you today?",
    "hi": "Hi 👋! What's up?",
    "who are you": "I'm IntelliChat, your AI assistant powered by DialoGPT! 🤖",
    "your name": "I'm IntelliChat — running completely offline with real AI! 😎",
    "bye": "Goodbye! 👋 Keep learning & keep building!",
    "help": "I'm here to chat naturally with you! Ask me anything! 💬",
    "how are you": "I'm doing great! Thanks for asking 😊",
    "thank you": "You're welcome! Happy to help! 😊",
    "thanks": "No problem! Anytime! 👍"
}

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

# -------- Conversation History --------
chat_history_ids = {}
conversation_memory = {}

# -------- Helper Functions --------

def check_knowledge_base(user_input):
    """Check for exact domain knowledge matches"""
    user_lower = user_input.lower()
    
    # Check FAQ
    for keyword, answer in faq_answers.items():
        if keyword in user_lower:
            return answer, "faq"
    
    # Check domain knowledge for direct questions
    if any(word in user_lower for word in ['what is', 'tell me about', 'explain']):
        for keyword, answer in dsai_knowledge.items():
            if keyword in user_lower:
                return answer, "knowledge"
    
    return None, None

def generate_ai_response(user_input, user_id):
    """Generate response using DialoGPT AI model"""
    
    try:
        # Encode user input
        new_input_ids = tokenizer.encode(
            user_input + tokenizer.eos_token, 
            return_tensors='pt',
            padding=True
        )
        
        # Get or create conversation history
        if user_id not in chat_history_ids:
            chat_history_ids[user_id] = new_input_ids
        else:
            # Append to existing conversation
            chat_history_ids[user_id] = torch.cat([
                chat_history_ids[user_id], 
                new_input_ids
            ], dim=-1)
        
        # Limit history to prevent memory issues (last 1000 tokens)
        if chat_history_ids[user_id].shape[-1] > 1000:
            chat_history_ids[user_id] = chat_history_ids[user_id][:, -1000:]
        
        # Generate AI response
        with torch.no_grad():
            output_ids = model.generate(
                chat_history_ids[user_id],
                max_length=chat_history_ids[user_id].shape[-1] + 100,
                pad_token_id=tokenizer.pad_token_id,
                temperature=0.8,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                no_repeat_ngram_size=3
            )
        
        # Update conversation history
        chat_history_ids[user_id] = output_ids
        
        # Decode only the new response
        response = tokenizer.decode(
            output_ids[:, chat_history_ids[user_id].shape[-1]:][0],
            skip_special_tokens=True
        )
        
        # Fallback if response is empty or too short
        if not response or len(response.strip()) < 2:
            response = "I'm processing that. Could you tell me more?"
        
        return response.strip()
    
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return "I'm having trouble generating a response. Could you rephrase that?"

def simple_sentiment(text):
    """Basic sentiment analysis"""
    positive_words = ['good', 'great', 'awesome', 'love', 'excellent', 'happy', 'nice', 'wonderful', 'amazing', 'best']
    negative_words = ['bad', 'hate', 'terrible', 'awful', 'worst', 'horrible', 'annoying', 'sad', 'angry']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"

# -------- Main Chat Route --------

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    user_id = data.get("user_id", "default_user")
    
    if not user_message:
        return jsonify({"reply": "Please say something! 😊"})
    
    # Analyze sentiment
    sentiment = simple_sentiment(user_message)
    
    # First check knowledge base for specific topics
    kb_answer, kb_type = check_knowledge_base(user_message)
    
    if kb_answer:
        return jsonify({
            "reply": kb_answer,
            "sentiment": sentiment,
            "type": kb_type,
            "model": "Knowledge Base"
        })
    
    # Use AI model if enabled
    if AI_ENABLED:
        try:
            ai_response = generate_ai_response(user_message, user_id)
            
            return jsonify({
                "reply": ai_response,
                "sentiment": sentiment,
                "type": "ai_generated",
                "model": "DialoGPT-small"
            })
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({
                "reply": "I'm having a moment. Can you try again? 😅",
                "sentiment": sentiment,
                "type": "error"
            })
    else:
        # Fallback response
        return jsonify({
            "reply": f"Interesting! You said: '{user_message}'. I'm still learning about this topic! 💬",
            "sentiment": sentiment,
            "type": "fallback"
        })

# -------- Reset Conversation --------

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Clear conversation history"""
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    
    if user_id in chat_history_ids:
        del chat_history_ids[user_id]
    
    if user_id in conversation_memory:
        del conversation_memory[user_id]
    
    return jsonify({
        "message": "Conversation reset! Starting fresh 🆕",
        "status": "success"
    })

# -------- Clear All History --------

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear all conversation data"""
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    
    if user_id in chat_history_ids:
        del chat_history_ids[user_id]
    
    return jsonify({
        "message": "Conversation history cleared! 🧹"
    })

# -------- Bot Info --------

@app.route('/info', methods=['GET'])
def info():
    """Get chatbot information"""
    return jsonify({
        "bot_name": "IntelliChat AI 🤖",
        "model": "Microsoft DialoGPT-small" if AI_ENABLED else "Keyword-based",
        "ai_enabled": AI_ENABLED,
        "features": [
            "✅ Real conversational AI" if AI_ENABLED else "⚠️ Keyword-based responses",
            "✅ Context-aware responses",
            "✅ Natural language understanding",
            "✅ 100% Offline - No API costs",
            "✅ Memory across conversation",
            "✅ Sentiment analysis"
        ],
        "total_topics": len(faq_answers) + len(dsai_knowledge),
        "status": "online",
        "type": "Real AI Model" if AI_ENABLED else "Fallback Mode"
    })

# -------- Health Check --------

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ai_model": "loaded" if AI_ENABLED else "not loaded",
        "server": "running"
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 IntelliChat AI Server Starting...")
    print("="*50)
    print(f"📡 Server: http://127.0.0.1:5000")
    print(f"🤖 AI Model: {'DialoGPT ✅' if AI_ENABLED else 'Fallback Mode ⚠️'}")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)