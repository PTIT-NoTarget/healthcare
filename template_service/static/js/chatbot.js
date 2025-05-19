document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chatIcon');
    const chatWindow = document.getElementById('chatWindow');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatBody = document.getElementById('chatBody');

    // Toggle chat window
    chatIcon.addEventListener('click', () => {
        chatWindow.style.display = chatWindow.style.display === 'none' || chatWindow.style.display === '' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') {
            chatInput.focus();
        }
    });

    // Close chat window
    closeChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    // Send message function
    function sendMessageToBot() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message
            addMessage(message, 'user-message');
            chatInput.value = '';

            // Simulate bot response (you can replace this with actual API call)
            setTimeout(() => {
                getBasicResponse(message);
            }, 500);
        }
    }

    // Add message to chat
    function addMessage(message, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);
        messageDiv.textContent = message;
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Get bot response
    async function getBotResponse(message) {
        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ message })
            });

            if (response.ok) {
                const data = await response.json();
                addMessage(data.response, 'bot-message');
            } else {
                addMessage("Sorry, I'm having trouble understanding. Please try again.", 'bot-message');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot-message');
        }
    }

    // Send message on button click
    sendMessage.addEventListener('click', sendMessageToBot);

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessageToBot();
        }
    });

    // Basic responses for demo (remove this when implementing actual API)
    const basicResponses = {
        'hello': 'Hi! How can I help you today?',
        'hi': 'Hello! How can I assist you?',
        'how are you': "I'm doing well, thanks for asking! How can I help you?",
        'bye': 'Goodbye! Have a great day!',
        'appointment': 'Would you like to schedule an appointment with a doctor? I can help you with that.',
        'help': 'I can help you with appointments, medical information, and general questions. What would you like to know?'
    };

    // Temporary function to handle responses without API
    function getBasicResponse(message) {
        message = message.toLowerCase();
        for (const [key, response] of Object.entries(basicResponses)) {
            if (message.includes(key)) {
                return response;
            }
        }
        return "I'm here to help! You can ask me about appointments, medical services, or general information.";
    }
});
