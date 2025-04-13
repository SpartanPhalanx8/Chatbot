const sendButton = document.getElementById("send-button");
const chatDisplay = document.getElementById("chat-display");
const userInputField = document.getElementById("user-input");

sendButton.addEventListener("click", async () => {
    const userInput = userInputField.value.trim();
    console.log("User Input: ", userInput); // Log user input inside the scope

    if (userInput) {
        displayMessage(userInput, "User");
        displayMessage("Processing...", "Bot");

        const botReply = await getBotResponse(userInput);
        console.log("Bot Response: ", botReply); // Log bot reply within scope

        updateLastBotMessage(botReply);
        userInputField.value = "";
    }
});

function updateLastBotMessage(message) {
    const messages = document.querySelectorAll("#chat-display p");
    messages[messages.length - 1].textContent = `Bot: ${message}`;
}

/* Predefined Bot responses */
function getPredefinedBotResponse(input) {
    const predefinedResponses = {
        "hello": "Hi there! How can I assist you today?",
        "how are you": "I'm just a bot, but I'm here to help! How are you?",
        "what is your name": "I'm your friendly AI chatbot, ready to assist!",
        "default": "Sorry, I didn't understand that. Could you try rephrasing?"
    };

    return predefinedResponses[input.toLowerCase()] || predefinedResponses["default"];
}

// Function to display messages in the chat
function displayMessage(message, sender) {
    const messageElement = document.createElement("p");
    messageElement.textContent = `${sender}: ${message}`;
    chatDisplay.appendChild(messageElement);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

async function getBotResponse(userInput) {
    try {
        const response = await fetch("http://127.0.0.1:9999/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });
        const data = await response.json();
        return data.reply; // Ensure the backend returns a valid reply
    } catch (error) {
        console.error("Error fetching bot response:", error);
        displayMessage("Bot: Something went wrong. Please try again.", "Bot"); // Show error message in chat
        return "Something went wrong."; // Return fallback message for debugging
    }
}