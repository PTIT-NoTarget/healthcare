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

            // Get bot response from API
            getBotResponse(message);
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
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.textContent = 'Typing...';
        chatBody.appendChild(typingDiv);
        chatBody.scrollTop = chatBody.scrollHeight;

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ message })
            });

            // Remove typing indicator
            chatBody.removeChild(typingDiv);

            if (response.ok) {
                const data = await response.json();
                addMessage(data.response, 'bot-message');
            } else {
                // Handle error responses
                if (response.status === 401) {
                    addMessage("Please log in to use the chatbot.", 'bot-message');
                } else {
                    addMessage("Sorry, I'm having trouble understanding. Please try again.", 'bot-message');
                }
            }
        } catch (error) {
            // Remove typing indicator
            if (typingDiv.parentNode) {
                chatBody.removeChild(typingDiv);
            }
            
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
});
