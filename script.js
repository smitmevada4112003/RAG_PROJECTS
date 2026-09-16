async function sendQuestion() {
    const inputElement = document.getElementById("question");
    const question = inputElement.value.trim();

    if (!question) return;

    const chat = document.getElementById("chatBox");

    // Append User Message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user";
    userMessageDiv.textContent = question;
    chat.appendChild(userMessageDiv);

    // Clear Input
    inputElement.value = "";

    // Append Loading Indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot loading";
    loadingDiv.id = "loading-" + Date.now();
    loadingDiv.innerHTML = '<span class="spinner"></span> Thinking...';
    chat.appendChild(loadingDiv);

    chat.scrollTop = chat.scrollHeight;

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Remove loading state
        loadingDiv.remove();

        // Append Bot Answer
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "message bot";
        botMessageDiv.textContent = data.answer || "No response received.";
        chat.appendChild(botMessageDiv);

    } catch (error) {
        console.error("API Error:", error);
        loadingDiv.classList.remove("loading");
        loadingDiv.classList.add("error");
        loadingDiv.textContent = "❌ Unable to connect to API backend. Make sure uvicorn is running on port 8000.";
    }

    chat.scrollTop = chat.scrollHeight;
}

// Allow sending message with Enter key
document.addEventListener("DOMContentLoaded", () => {
    const inputElement = document.getElementById("question");
    if (inputElement) {
        inputElement.addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                sendQuestion();
            }
        });
    }
});
