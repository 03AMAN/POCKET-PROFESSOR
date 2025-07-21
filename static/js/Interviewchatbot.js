document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const jobRole = document.getElementById("job-role");
    const difficulty = document.getElementById("difficulty");

    function appendMessage(text, className) {
        const messageDiv = document.createElement("div");
        messageDiv.className = className;
        messageDiv.innerText = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    window.sendMessage = function() {
        const message = userInput.value;
        if (!message) return;
        
        appendMessage("You: " + message, "user-message");
        userInput.value = "";
        
        fetch("/interview-chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                job_role: jobRole.value,
                difficulty: difficulty.value,
                user_message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("Bot: " + data.reply, "bot-message");
        })
        .catch(error => console.error("Error:", error));
    };

    window.startVoiceRecognition = function() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "en-US";
        recognition.start();

        recognition.onresult = function(event) {
            userInput.value = event.results[0][0].transcript;
            sendMessage();
        };
    };
});
