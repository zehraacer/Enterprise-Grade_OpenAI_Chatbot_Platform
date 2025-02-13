// Constant definitions
const chatForm = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const typingIndicator = document.getElementById('typing-indicator');

// Create user ID
const userId = 'user_' + Math.random().toString(36).substr(2, 9);

// WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/chat`);
let useWebSocket = true;

// Define cleanup function once (with the latest version)
function cleanup() {
    // Close WebSocket connection
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    
    // Clear interval
    if (window.timeUpdateInterval) {
        clearInterval(window.timeUpdateInterval);
    }

    // Clear conversation history
    conversationHistory = [];
}

// Call cleanup when the page is closed
window.addEventListener('unload', cleanup);

// Helper functions
function formatBotMessage(text) {
    // Special formatting for date and user info
    if (text.includes("Current Date and Time") || text.includes("Current User's Login")) {
        return text.split('\n').map(line => `<div class="info-line">${line}</div>`).join('');
    }
    
    // Format list items
    text = text.replace(/(\d+\.|-)(.+)/g, '<div class="list-item">$1$2</div>');
    
    // Format paragraphs
    text = text.split('\n').map(para => {
        if (para.trim()) {
            return `<div class="paragraph">${para}</div>`;
        }
        return '';
    }).join('');
    
    return text;
}

// Array to hold conversation history
let conversationHistory = [];

// Update message append function
function appendMessage(text, sender) {
    // Add message to history
    conversationHistory.push({
        text: text,
        sender: sender,
        timestamp: getCurrentTime()
    });

    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-msg`;
    
    if (sender === 'bot') {
        messageDiv.innerHTML = formatBotMessage(text);
    } else {
        messageDiv.textContent = text;
    }
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.innerHTML = `
        <i class="fas fa-clock"></i>
        <span>${getCurrentTime()}</span>
    `;
    
    messageDiv.appendChild(timestamp);
    chatBox.insertBefore(messageDiv, typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Update conversation history helper functions
function getLastUserMessage() {
    for (let i = conversationHistory.length - 1; i >= 0; i--) {
        if (conversationHistory[i].sender === 'user') {
            return conversationHistory[i].text;
        }
    }
    return null;
}

function getNthUserMessage(n) {
    // Find the nth user message (starting from 1)
    let count = 0;
    for (let i = 0; i < conversationHistory.length; i++) {
        if (conversationHistory[i].sender === 'user') {
            count++;
            if (count === n) {
                return conversationHistory[i].text;
            }
        }
    }
    return null;
}

// Update sendMessage function
async function sendMessage(message) {
    try {
        // Add user message to history and display
        appendMessage(message, 'user');
        showTypingIndicator();

        // Check for special commands
        if (message.toLowerCase() === 'what was my first question?' || message.toLowerCase() === 'what did I ask you first?') {
            const firstMessage = getNthUserMessage(1);
            hideTypingIndicator();
            appendMessage(
                firstMessage ? 
                `Your first question was "${firstMessage}".` : 
                'You have not asked a question yet.', 
                'bot'
            );
            return;
        }

        // Debug to check conversation history
        console.log('Conversation History:', conversationHistory);

        // Normal message sending process
        if (useWebSocket && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ 
                text: message,
                user_id: userId
            }));
        } else {
            // Send via HTTP
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: message,
                    user_id: userId
                })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.error) {
                console.error('Error:', data.error);
                appendMessage('Sorry, an error occurred: ' + data.error, 'bot');
            } else {
                appendMessage(data.response, 'bot');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        appendMessage('Sorry, an error occurred. Please try again.', 'bot');
    }
}

function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

// WebSocket event handlers
ws.onmessage = function(event) {
    hideTypingIndicator();
    const data = JSON.parse(event.data);
    // Add bot message to history and display
    appendMessage(data.response, 'bot');
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
    appendMessage('Connection error. Using HTTP.', 'bot');
    useWebSocket = false;
};

// Form submit event listener
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        messageInput.value = '';
        messageInput.focus();
        sendMessage(message);
    }
});

// Time update function
function updateTime() {
    const now = new Date();
    const formattedTime = now.toISOString().replace('T', ' ').substr(0, 19) + ' UTC';
    document.getElementById('current-time').textContent = formattedTime;
}

// Update every second
setInterval(updateTime, 1000);
updateTime(); // For initial load

// Theme change function
function changeTheme(theme) {
    // First remove all theme classes
    document.body.classList.remove('theme-holographic', 'theme-terminal', 'theme-comic', 'theme-cyberpunk', 'theme-default');
    
    // Add new theme
    if (theme !== 'default') {
        document.body.classList.add(`theme-${theme}`);
    }
    
    // Save theme preference
    localStorage.setItem('preferred-theme', theme);
    
    // Log to console for debugging
    console.log('Theme changed to:', theme);
}

// Load saved theme when the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('preferred-theme');
    if (savedTheme) {
        changeTheme(savedTheme);
        document.getElementById('themeSelect').value = savedTheme;
    }
    console.log('Saved theme loaded:', savedTheme);
});
