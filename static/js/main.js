/**
 * LLM Shield Main JavaScript
 * Handles chat interactions and system status
 */

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const statusDot = document.querySelector('.status-dot');
const statusText = document.getElementById('status-text');
const systemStatus = document.getElementById('system-status');

// State
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check system health on load
    checkSystemHealth();
    
    // Set up event listeners
    if (sendButton && userInput) {
        sendButton.addEventListener('click', handleSendMessage);
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }
});

/**
 * Handle sending a message to the AI
 */
function handleSendMessage() {
    // Don't process empty messages or if already processing
    if (isProcessing || !userInput.value.trim()) {
        return;
    }
    
    const userMessage = userInput.value.trim();
    
    // Add user message to chat
    addMessageToChat('user', userMessage);
    
    // Clear input
    userInput.value = '';
    
    // Set processing state
    setProcessingState(true);
    
    // Send to backend
    sendMessageToBackend(userMessage)
        .then(response => {
            // Handle successful response
            if (response.success) {
                addMessageToChat('ai', response.response);
            } else {
                // Handle error from backend
                addMessageToChat('error', response.error || 'An error occurred processing your request.');
            }
        })
        .catch(error => {
            // Handle network or other errors
            addMessageToChat('error', 'Unable to reach the server. Please try again later.');
            console.error('Error:', error);
        })
        .finally(() => {
            // Reset processing state
            setProcessingState(false);
        });
}

/**
 * Send message to the backend API
 * @param {string} message - User message
 * @returns {Promise} - Response promise
 */
async function sendMessageToBackend(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: message })
        });
        
        return await response.json();
    } catch (error) {
        throw error;
    }
}

/**
 * Add a message to the chat display
 * @param {string} type - Message type ('user', 'ai', 'system', 'error')
 * @param {string} content - Message content
 */
function addMessageToChat(type, content) {
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    
    // For AI messages, use marked for markdown if available
    if (type === 'ai' && window.marked) {
        messageDiv.innerHTML = marked.parse(content);
    } else {
        // Basic formatting for code blocks
        const formattedContent = content.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
        messageDiv.innerHTML = formattedContent;
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Set the UI processing state
 * @param {boolean} isProcessing - Whether the system is processing
 */
function setProcessingState(processing) {
    isProcessing = processing;
    
    if (sendButton) {
        sendButton.disabled = processing;
    }
    
    if (statusDot && statusText) {
        if (processing) {
            statusDot.classList.add('loading');
            statusText.textContent = 'Processing...';
        } else {
            statusDot.classList.remove('loading');
            statusText.textContent = 'Ready';
        }
    }
}

/**
 * Check the system health status
 */
async function checkSystemHealth() {
    if (!systemStatus) return;
    
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        systemStatus.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        systemStatus.className = data.status;
        
        // If degraded, show why
        if (data.status === 'degraded') {
            let reason = '';
            if (data.llm_service === 'unavailable') {
                reason += 'LLM service unavailable. ';
            }
            if (data.logging === 'not writable') {
                reason += 'Logging system issues.';
            }
            systemStatus.setAttribute('title', reason.trim());
        }
    } catch (error) {
        systemStatus.textContent = 'Unhealthy';
        systemStatus.className = 'unhealthy';
        console.error('Health check error:', error);
    }
}