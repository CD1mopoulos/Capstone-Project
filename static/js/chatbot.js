document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chatbot-input");
    const sendBtn = document.getElementById("chatbot-send");
    const chatbox = document.getElementById("chatbot-messages");
    const container = document.getElementById("chatbot-container");
    const header = document.getElementById("chatbot-header");
    const toggle = document.getElementById("chatbot-toggle");
    const body = document.getElementById("chatbot-body");
    const icon = document.getElementById("chatbot-icon");

    const language = "en";
    let isMinimized = true;
    let hasGreeted = false; // ✅ NEW: prevent multiple greetings

    // ========== START MINIMIZED ==========
    body.style.display = "none";
    header.style.display = "none";
    container.style.height = "50px";
    container.style.width = "50px";
    container.style.borderRadius = "50%";
    container.style.bottom = "20px";
    container.style.right = "20px";
    container.style.left = "unset";
    container.style.top = "unset";
    icon.style.display = "flex";
    icon.style.visibility = "visible";

    // ========== SEND MESSAGE ==========
    function sendMessage() {
        const message = inputField.value.trim();
        if (message === "") return;

        chatbox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

        fetch("/chatbot/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                lang: language
            })
        })
        .then(response => response.json())
        .then(data => {
            chatbox.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        });

        inputField.value = "";
    }

    sendBtn.addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // ========== TOGGLE ==========
    toggle.addEventListener("click", () => {
        if (isMinimized) {
            body.style.display = "flex";
            header.style.display = "block";
            container.style.height = "400px";
            container.style.width = "300px";
            container.style.borderRadius = "10px";
            toggle.innerHTML = "▲";
            icon.style.display = "none";
            icon.style.visibility = "hidden";

            // 🟢 Only greet once
            if (!hasGreeted) {
                chatbox.innerHTML += `<div><strong>Bot:</strong> Hi there! 👋 How can I assist you today?</div>`;
                chatbox.scrollTop = chatbox.scrollHeight;
                hasGreeted = true;
            }
        } else {
            body.style.display = "none";
            header.style.display = "none";
            container.style.height = "50px";
            container.style.width = "50px";
            container.style.borderRadius = "50%";
            icon.style.display = "flex";
            icon.style.visibility = "visible";
        }
        isMinimized = !isMinimized;
    });

    // ========== ICON CLICK ==========
    icon.addEventListener("click", () => {
        body.style.display = "flex";
        header.style.display = "block";
        container.style.height = "400px";
        container.style.width = "300px";
        container.style.borderRadius = "10px";
        container.style.bottom = "20px";
        container.style.right = "20px";
        container.style.left = "unset";
        container.style.top = "unset";
        toggle.innerHTML = "▲";
        icon.style.display = "none";
        icon.style.visibility = "hidden";
        isMinimized = false;

        // 🟢 Only greet once
        if (!hasGreeted) {
            chatbox.innerHTML += `<div><strong>Bot:</strong> Hi there! 👋 How can I assist you today?</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
            hasGreeted = true;
        }
    });

    // ========== REVEAL CONTAINER ==========
    container.style.visibility = "visible";
});
