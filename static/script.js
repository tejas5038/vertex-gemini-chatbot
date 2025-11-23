// Generate or retrieve session ID
function getSessionId() {
    let sessionId = localStorage.getItem('chatbot_session_id');
    if (!sessionId) {
        sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatbot_session_id', sessionId);
    }
    return sessionId;
}

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const resetButton = document.getElementById('resetButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const sessionIdDisplay = document.getElementById('sessionId');

// Initialize
const sessionId = getSessionId();
sessionIdDisplay.textContent = sessionId;

// Add message to chat
function addMessage(role, content, toolCalls = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    // Add tool call information if present
    if (toolCalls && toolCalls.length > 0) {
        toolCalls.forEach(call => {
            const toolDiv = document.createElement('div');
            toolDiv.className = 'tool-call';
            toolDiv.innerHTML = `
                <strong>🔧 Tool Used:</strong> ${call.tool}<br>
                <strong>Result:</strong> ${call.result.success ? '✅ Success' : '❌ Failed'}
                ${call.result.error ? `<br><em>${call.result.error}</em>` : ''}
            `;
            messageContent.appendChild(toolDiv);
        });
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show/hide loading indicator
function setLoading(isLoading) {
    if (isLoading) {
        loadingIndicator.classList.add('active');
        sendButton.disabled = true;
        userInput.disabled = true;
    } else {
        loadingIndicator.classList.remove('active');
        sendButton.disabled = false;
        userInput.disabled = false;
    }
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Add user message to chat
    addMessage('user', message);
    userInput.value = '';
    
    setLoading(true);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                user_message: message
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            addMessage('assistant', `Sorry, an error occurred: ${data.message}`);
        } else {
            addMessage('assistant', data.assistant_message, data.tool_calls);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('assistant', 'Sorry, I encountered an error processing your request. Please try again.');
    } finally {
        setLoading(false);
        userInput.focus();
    }
}

// Reset conversation
async function resetConversation() {
    if (!confirm('Are you sure you want to clear the conversation history?')) {
        return;
    }
    
    setLoading(true);
    
    try {
        const response = await fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (!data.error) {
            // Clear chat messages (keep system message)
            const systemMessage = chatMessages.querySelector('.system-message');
            chatMessages.innerHTML = '';
            if (systemMessage) {
                chatMessages.appendChild(systemMessage);
            }
            
            addMessage('assistant', 'Conversation history has been cleared. How can I help you?');
        } else {
            alert('Failed to reset conversation: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to reset conversation. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
resetButton.addEventListener('click', resetConversation);

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Focus input on load
userInput.focus();
