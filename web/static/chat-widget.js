class SupportChatWidget {
    constructor(config = {}) {
        this.config = {
            serverUrl: config.serverUrl || 'http://localhost:8000',
            title: config.title || 'Support Chat',
            placeholder: config.placeholder || 'Type your message...',
            position: config.position || 'right',
            theme: config.theme || 'light',
            ...config
        };
        
        this.isOpen = false;
        this.isMinimized = false;
        this.messageHistory = [];
        this.setupWidget();
    }

    setupWidget() {
        // Create and inject styles
        this.injectStyles();
        
        // Create chat button
        this.createChatButton();
        
        // Create chat widget container
        this.createWidgetContainer();

        // Setup event listeners
        this.setupEventListeners();
    }

    injectStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${this.config.serverUrl}/static/chat-widget.css`;
        document.head.appendChild(link);
    }

    createChatButton() {
        this.chatButton = document.createElement('button');
        this.chatButton.className = 'support-chat-button';
        this.chatButton.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
            Chat with Support
        `;
        document.body.appendChild(this.chatButton);
    }

    createWidgetContainer() {
        this.container = document.createElement('div');
        this.container.className = 'support-chat-widget';
        this.container.style.display = 'none';
        
        this.container.innerHTML = `
            <div class="support-chat-header">
                <div class="support-chat-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                    </svg>
                    ${this.config.title}
                </div>
                <div class="support-chat-controls">
                    <button class="minimize-btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
                        </svg>
                    </button>
                    <button class="close-btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="support-chat-messages"></div>
            <div class="support-chat-input">
                <input type="text" placeholder="${this.config.placeholder}">
                <button type="submit">Send</button>
            </div>
        `;
        
        document.body.appendChild(this.container);
        
        this.messagesContainer = this.container.querySelector('.support-chat-messages');
        this.input = this.container.querySelector('input');
        this.sendButton = this.container.querySelector('button[type="submit"]');
    }

    setupEventListeners() {
        // Chat button click
        this.chatButton.addEventListener('click', () => this.toggleWidget());
        
        // Close button
        this.container.querySelector('.close-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeWidget();
        });
        
        // Minimize button
        this.container.querySelector('.minimize-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMinimize();
        });
        
        // Send message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Header click for minimized state
        this.container.querySelector('.support-chat-header').addEventListener('click', () => {
            if (this.isMinimized) this.toggleMinimize();
        });
    }

    toggleWidget() {
        this.isOpen = !this.isOpen;
        this.container.style.display = this.isOpen ? 'flex' : 'none';
        this.chatButton.style.display = this.isOpen ? 'none' : 'flex';
        if (this.isOpen) this.input.focus();
    }

    closeWidget() {
        this.isOpen = false;
        this.isMinimized = false;
        this.container.style.display = 'none';
        this.chatButton.style.display = 'flex';
        this.container.classList.remove('minimized');
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        this.container.classList.toggle('minimized');
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;
        
        // Clear input
        this.input.value = '';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Disable input and button while waiting
        this.input.disabled = true;
        this.sendButton.disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to server
            const response = await fetch(`${this.config.serverUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.messageHistory
                }),
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add assistant's response
            this.addMessage(data.response, 'assistant');
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage('Sorry, there was an error processing your message.', 'assistant');
        }
        
        // Re-enable input and button
        this.input.disabled = false;
        this.sendButton.disabled = false;
        this.input.focus();
    }

    addMessage(text, sender) {
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${sender}-message`;
        messageEl.textContent = text;
        
        this.messagesContainer.appendChild(messageEl);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        
        // Store in history
        this.messageHistory.push({
            role: sender,
            content: text
        });
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        this.messagesContainer.appendChild(indicator);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const indicator = this.messagesContainer.querySelector('.typing-indicator');
        if (indicator) indicator.remove();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupportChatWidget;
}