const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");

function addMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add(sender === "bot" ? "bot-message" : "user-message");
  messageDiv.textContent = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  userInput.value = "";
  typingIndicator.classList.remove("hidden");

  try {
    const res = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await res.json();
    typingIndicator.classList.add("hidden");
    addMessage(data.reply, "bot");
  } catch (err) {
    typingIndicator.classList.add("hidden");
    addMessage("⚠️ Server error. Backend nahi chal raha.", "bot");
  }
}

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
