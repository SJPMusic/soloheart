// DnD 5E AI-Powered Game - Enhanced Frontend JavaScript
// ====================================================

class EnhancedDnDGameApp {
    constructor() {
        this.isTyping = false;
        this.messageHistory = [];
        this.isProcessing = false;
        this.savedSessions = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.autoResizeTextarea();
        this.updateCharCount();
        this.loadGameStatus();
        this.focusInput();
    }

    bindEvents() {
        // Message input events
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateCharCount();
            this.updateSendButton();
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        messageInput.addEventListener('paste', () => {
            // Auto-resize after paste
            setTimeout(() => {
                this.autoResizeTextarea();
                this.updateCharCount();
            }, 0);
        });

        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Header button events
        document.getElementById('new-campaign-btn').addEventListener('click', () => {
            this.showNewCampaignModal();
        });

        document.getElementById('save-campaign-btn').addEventListener('click', () => {
            this.showSaveCampaignModal();
        });

        document.getElementById('load-campaign-btn').addEventListener('click', () => {
            this.showLoadCampaignModal();
        });

        document.getElementById('start-session-btn').addEventListener('click', () => {
            this.startSession();
        });

        document.getElementById('end-session-btn').addEventListener('click', () => {
            this.endSession();
        });

        // Modal events
        document.getElementById('close-modal').addEventListener('click', () => {
            this.hideModal('new-campaign-modal');
        });

        document.getElementById('close-save-modal').addEventListener('click', () => {
            this.hideModal('save-campaign-modal');
        });

        document.getElementById('close-load-modal').addEventListener('click', () => {
            this.hideModal('load-campaign-modal');
        });

        document.getElementById('cancel-campaign').addEventListener('click', () => {
            this.hideModal('new-campaign-modal');
        });

        document.getElementById('cancel-save').addEventListener('click', () => {
            this.hideModal('save-campaign-modal');
        });

        document.getElementById('cancel-load').addEventListener('click', () => {
            this.hideModal('load-campaign-modal');
        });

        document.getElementById('create-campaign').addEventListener('click', () => {
            this.createNewCampaign();
        });

        document.getElementById('confirm-save').addEventListener('click', () => {
            this.saveCampaign();
        });

        // Close modals when clicking outside
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal')) {
                    this.hideModal(modal.id);
                }
            });
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });

        // Focus on input when clicking in chat area
        document.querySelector('.chat-container').addEventListener('click', () => {
            this.focusInput();
        });
    }

    focusInput() {
        const messageInput = document.getElementById('message-input');
        messageInput.focus();
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('message-input');
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 8 * 24); // 8rem max height
        textarea.style.height = newHeight + 'px';
    }

    updateCharCount() {
        const textarea = document.getElementById('message-input');
        const charCount = document.getElementById('char-count');
        const count = textarea.value.length;
        charCount.textContent = `${count}/4000`;
        
        // Change color when approaching limit
        if (count > 3600) {
            charCount.style.color = '#ef4444';
        } else if (count > 3000) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#9ca3af';
        }
    }

    updateSendButton() {
        const textarea = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const hasText = textarea.value.trim().length > 0;
        
        sendButton.disabled = !hasText || this.isTyping || this.isProcessing;
    }

    async sendMessage() {
        const textarea = document.getElementById('message-input');
        const message = textarea.value.trim();
        
        if (!message || this.isTyping || this.isProcessing) return;

        this.isProcessing = true;
        this.updateSendButton();

        // Store the message before clearing
        const userMessage = message;

        // Clear input immediately (ChatGPT behavior)
        textarea.value = '';
        this.autoResizeTextarea();
        this.updateCharCount();

        // Add user message to chat
        this.addMessage(userMessage, 'user');

        // Show typing indicator with a small delay (ChatGPT behavior)
        setTimeout(() => {
            this.showTypingIndicator();
        }, 300);

        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage })
            });

            const data = await response.json();

            if (response.ok) {
                // Hide typing indicator and add AI response
                this.hideTypingIndicator();
                this.addMessage(data.response, 'ai');
            } else {
                throw new Error(data.error || 'Failed to send message');
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage(`Sorry, I encountered an error: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
            this.focusInput();
        }
    }

    addMessage(content, type = 'ai') {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const timestamp = this.formatTimestamp(new Date());

        let avatarIcon = 'fas fa-user';
        if (type === 'ai') {
            avatarIcon = 'fas fa-dragon';
        } else if (type === 'error') {
            avatarIcon = 'fas fa-exclamation-triangle';
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">
                    ${this.formatMessageContent(content)}
                </div>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Store in history
        this.messageHistory.push({
            content,
            type,
            timestamp: new Date()
        });
    }

    formatMessageContent(content) {
        // Convert line breaks to paragraphs
        const paragraphs = content.split('\n').filter(p => p.trim());
        if (paragraphs.length === 0) {
            return '<p>' + this.escapeHtml(content) + '</p>';
        }
        return paragraphs.map(p => `<p>${this.escapeHtml(p)}</p>`).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTimestamp(date) {
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.updateSendButton();
        document.getElementById('typing-indicator').style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.updateSendButton();
        document.getElementById('typing-indicator').style.display = 'none';
    }

    scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        // Smooth scroll to bottom
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('show');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
        this.focusInput();
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
        this.focusInput();
    }

    showNewCampaignModal() {
        this.showModal('new-campaign-modal');
        document.getElementById('campaign-name').focus();
    }

    showSaveCampaignModal() {
        this.showModal('save-campaign-modal');
        document.getElementById('save-name').focus();
    }

    async showLoadCampaignModal() {
        this.showModal('load-campaign-modal');
        await this.loadSavedSessions();
    }

    async loadSavedSessions() {
        const sessionsList = document.getElementById('saved-sessions-list');
        sessionsList.innerHTML = '<p>Loading saved sessions...</p>';

        try {
            const response = await fetch('/api/saved-sessions');
            const data = await response.json();

            if (response.ok) {
                this.savedSessions = data.saved_sessions;
                this.renderSavedSessions();
            } else {
                throw new Error(data.error || 'Failed to load saved sessions');
            }
        } catch (error) {
            console.error('Error loading saved sessions:', error);
            sessionsList.innerHTML = `<p class="error">Error loading saved sessions: ${error.message}</p>`;
        }
    }

    renderSavedSessions() {
        const sessionsList = document.getElementById('saved-sessions-list');
        
        if (this.savedSessions.length === 0) {
            sessionsList.innerHTML = '<p>No saved sessions found.</p>';
            return;
        }

        const sessionsHtml = this.savedSessions.map(session => {
            const date = new Date(session.started_at).toLocaleString();
            return `
                <div class="saved-session-item">
                    <div class="session-info">
                        <h4>${session.name || 'Unnamed Save'}</h4>
                        <p class="session-meta">
                            <span class="session-date">${date}</span>
                            <span class="session-messages">${session.message_count} messages</span>
                        </p>
                        ${session.current_location ? `<p class="session-location">Location: ${session.current_location}</p>` : ''}
                    </div>
                    <button class="btn btn-primary load-session-btn" data-session-id="${session.session_id}">
                        <i class="fas fa-play"></i> Load
                    </button>
                </div>
            `;
        }).join('');

        sessionsList.innerHTML = sessionsHtml;

        // Add event listeners to load buttons
        document.querySelectorAll('.load-session-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sessionId = e.target.dataset.sessionId;
                this.loadCampaign(sessionId);
            });
        });
    }

    async createNewCampaign() {
        const campaignName = document.getElementById('campaign-name').value.trim();
        
        if (!campaignName) {
            alert('Please enter a campaign name');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/new-campaign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ campaign_name: campaignName })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('new-campaign-modal');
                this.addMessage(`New campaign "${campaignName}" created successfully! You can now start your adventure.`, 'ai');
                this.loadGameStatus();
            } else {
                throw new Error(data.error || 'Failed to create campaign');
            }

        } catch (error) {
            console.error('Error creating campaign:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async saveCampaign() {
        const saveName = document.getElementById('save-name').value.trim();
        
        this.showLoading();

        try {
            const response = await fetch('/api/save-campaign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ save_name: saveName || null })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('save-campaign-modal');
                this.addMessage(`Campaign saved successfully as "${data.save_data.save_name}"!`, 'ai');
                document.getElementById('save-name').value = '';
            } else {
                throw new Error(data.error || 'Failed to save campaign');
            }

        } catch (error) {
            console.error('Error saving campaign:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadCampaign(sessionId) {
        this.showLoading();

        try {
            const response = await fetch('/api/load-campaign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('load-campaign-modal');
                this.addMessage(`Campaign loaded successfully! Your adventure continues...`, 'ai');
                this.loadGameStatus();
                
                // Clear chat and reload messages (you might want to implement this)
                // this.clearChat();
                // this.loadChatHistory();
            } else {
                throw new Error(data.error || 'Failed to load campaign');
            }

        } catch (error) {
            console.error('Error loading campaign:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async startSession() {
        this.showLoading();

        try {
            const response = await fetch('/api/start-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.addMessage('Session started! Your adventure begins now. Describe what you want to do or create your character.', 'ai');
                this.loadGameStatus();
            } else {
                throw new Error(data.error || 'Failed to start session');
            }

        } catch (error) {
            console.error('Error starting session:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async endSession() {
        this.showLoading();

        try {
            const response = await fetch('/api/end-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.addMessage('Session ended. Your progress has been saved and you can continue your adventure later.', 'ai');
                this.loadGameStatus();
            } else {
                throw new Error(data.error || 'Failed to end session');
            }

        } catch (error) {
            console.error('Error ending session:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadGameStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (response.ok) {
                this.updateHeaderButtons(data.session_active);
            }
        } catch (error) {
            console.error('Error loading game status:', error);
        }
    }

    updateHeaderButtons(sessionActive) {
        const startBtn = document.getElementById('start-session-btn');
        const endBtn = document.getElementById('end-session-btn');

        if (sessionActive) {
            startBtn.disabled = true;
            endBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            endBtn.disabled = true;
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dndApp = new EnhancedDnDGameApp();
}); 