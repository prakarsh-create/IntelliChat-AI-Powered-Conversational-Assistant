const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function appendMessage(sender, message) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender.toLowerCase());
  msgDiv.textContent = message;
  chatBox.appendChild(msgDiv);

  // auto-scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const message = userInput.value.trim();
  if (message === "") return;

  appendMessage("You", message);
  userInput.value = "";

  fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      appendMessage("Bot", data.reply);
    })
    .catch(err => {
      console.error("Error:", err);
      appendMessage("Bot", "⚠️ Connection error!");
    });
}
