// DnD 5E AI-Powered Game - Enhanced Frontend JavaScript with Memory Integration
// ===========================================================================

class EnhancedDnDGameApp {
    constructor() {
        this.isTyping = false;
        this.messageHistory = [];
        this.isProcessing = false;
        this.savedSessions = [];
        this.memoryStats = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.autoResizeTextarea();
        this.updateCharCount();
        this.loadGameStatus();
        this.loadMemoryStats();
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

        // Memory management buttons
        const memoryStatsBtn = document.getElementById('memory-stats-btn');
        if (memoryStatsBtn) {
            memoryStatsBtn.addEventListener('click', () => {
                this.showMemoryStats();
            });
        }

        const recallMemoriesBtn = document.getElementById('recall-memories-btn');
        if (recallMemoriesBtn) {
            recallMemoriesBtn.addEventListener('click', () => {
                this.showRecallMemoriesModal();
            });
        }

        const saveMemoryBtn = document.getElementById('save-memory-btn');
        if (saveMemoryBtn) {
            saveMemoryBtn.addEventListener('click', () => {
                this.saveMemoryState();
            });
        }

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

        document.getElementById('close-memory-modal').addEventListener('click', () => {
            this.hideModal('memory-stats-modal');
        });

        document.getElementById('close-recall-modal').addEventListener('click', () => {
            this.hideModal('recall-memories-modal');
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

        document.getElementById('cancel-recall').addEventListener('click', () => {
            this.hideModal('recall-memories-modal');
        });

        document.getElementById('create-campaign').addEventListener('click', () => {
            this.createNewCampaign();
        });

        document.getElementById('confirm-save').addEventListener('click', () => {
            this.saveCampaign();
        });

        document.getElementById('confirm-recall').addEventListener('click', () => {
            this.recallMemories();
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

    async loadMemoryStats() {
        try {
            const response = await fetch('/api/memory/stats');
            if (response.ok) {
                const data = await response.json();
                this.memoryStats = data.memory_stats;
                this.updateMemoryDisplay();
            }
        } catch (error) {
            console.error('Error loading memory stats:', error);
        }
    }

    updateMemoryDisplay() {
        if (!this.memoryStats) return;

        // Update memory stats in header if element exists
        const memoryStatsElement = document.getElementById('memory-stats-display');
        if (memoryStatsElement) {
            const stats = this.memoryStats;
            memoryStatsElement.innerHTML = `
                <div class="memory-stats">
                    <span class="stat">ST: ${stats.short_term || 0}</span>
                    <span class="stat">MT: ${stats.mid_term || 0}</span>
                    <span class="stat">LT: ${stats.long_term || 0}</span>
                    <span class="stat">Total: ${stats.created || 0}</span>
                </div>
            `;
        }
    }

    showMemoryStats() {
        if (!this.memoryStats) {
            this.loadMemoryStats();
            return;
        }

        const modal = document.getElementById('memory-stats-modal');
        const content = document.getElementById('memory-stats-content');
        
        const stats = this.memoryStats;
        content.innerHTML = `
            <div class="memory-stats-grid">
                <div class="stat-card">
                    <h3>Memory Layers</h3>
                    <div class="stat-item">
                        <span>Short-term:</span>
                        <span>${stats.short_term || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span>Mid-term:</span>
                        <span>${stats.mid_term || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span>Long-term:</span>
                        <span>${stats.long_term || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>Memory Operations</h3>
                    <div class="stat-item">
                        <span>Created:</span>
                        <span>${stats.created || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span>Forgotten:</span>
                        <span>${stats.forgotten || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span>Reinforced:</span>
                        <span>${stats.reinforced || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>System Info</h3>
                    <div class="stat-item">
                        <span>Users:</span>
                        <span>${stats.users || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span>Forgotten:</span>
                        <span>${stats.forgotten || 0}</span>
                    </div>
                </div>
            </div>
        `;
        
        this.showModal('memory-stats-modal');
    }

    showRecallMemoriesModal() {
        this.showModal('recall-memories-modal');
    }

    async recallMemories() {
        const query = document.getElementById('memory-query').value.trim();
        const memoryType = document.getElementById('memory-type').value;
        const layer = document.getElementById('memory-layer').value;

        try {
            const response = await fetch('/api/memory/recall', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    memory_type: memoryType || null,
                    layer: layer || null
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayRecalledMemories(data.memories);
            } else {
                this.showError(`Error recalling memories: ${data.error}`);
            }
        } catch (error) {
            console.error('Error recalling memories:', error);
            this.showError('Failed to recall memories');
        }
    }

    displayRecalledMemories(memories) {
        const resultsContainer = document.getElementById('memory-results');
        
        if (memories.length === 0) {
            resultsContainer.innerHTML = '<p class="no-memories">No memories found matching your criteria.</p>';
            return;
        }

        const memoriesHtml = memories.map(memory => `
            <div class="memory-item">
                <div class="memory-header">
                    <span class="memory-type">${memory.type}</span>
                    <span class="memory-layer">${memory.layer}</span>
                    <span class="memory-significance">Significance: ${memory.significance.toFixed(2)}</span>
                </div>
                <div class="memory-content">
                    <strong>Content:</strong> ${this.escapeHtml(JSON.stringify(memory.content, null, 2))}
                </div>
                <div class="memory-meta">
                    <span class="memory-tags">Tags: ${memory.thematic_tags.join(', ') || 'None'}</span>
                    <span class="memory-emotions">Emotions: ${memory.emotional_context.join(', ') || 'None'}</span>
                    <span class="memory-time">${new Date(memory.timestamp).toLocaleString()}</span>
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = memoriesHtml;
    }

    async saveMemoryState() {
        try {
            const response = await fetch('/api/memory/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(`Memory state saved as ${data.filename}`);
                this.loadMemoryStats(); // Refresh stats
            } else {
                this.showError(`Error saving memory: ${data.error}`);
            }
        } catch (error) {
            console.error('Error saving memory state:', error);
            this.showError('Failed to save memory state');
        }
    }

    showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    showError(message) {
        // Create a temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dndApp = new EnhancedDnDGameApp();
});

// Character Creation Functions
let characterCreationActive = false;
let currentCharacter = null;

function showCampaignSelection() {
    document.getElementById('campaignSelectionModal').style.display = 'block';
}

function closeCampaignSelection() {
    document.getElementById('campaignSelectionModal').style.display = 'none';
}

function startNewCampaign() {
    closeCampaignSelection();
    startCharacterCreation();
}

function loadExistingCampaign() {
    closeCampaignSelection();
    // Load existing campaign logic here
    addMessage('system', 'Loading existing campaign...');
    // For now, just start character creation
    startCharacterCreation();
}

function startCharacterCreation() {
    characterCreationActive = true;
    
    fetch('/api/character/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showCharacterCreationStep(data);
        } else {
            console.error('Failed to start character creation:', data.error);
        }
    })
    .catch(error => {
        console.error('Error starting character creation:', error);
    });
}

function showCharacterCreationStep(data) {
    const modal = document.getElementById('characterCreationModal');
    const instructions = document.getElementById('stepInstructions');
    const options = document.getElementById('stepOptions');
    const summary = document.getElementById('characterSummary');
    
    // Show instructions
    instructions.innerHTML = `<p>${data.instructions}</p>`;
    
    // Show options
    options.innerHTML = '';
    if (data.options) {
        Object.keys(data.options).forEach(key => {
            const optionList = data.options[key];
            optionList.forEach(option => {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'option-item';
                optionDiv.onclick = () => {
                    document.getElementById('characterChoice').value = option.name;
                };
                optionDiv.innerHTML = `
                    <h4>${option.name}</h4>
                    <p>${option.description}</p>
                `;
                options.appendChild(optionDiv);
            });
        });
    }
    
    // Show character summary
    if (data.summary && data.summary.status !== 'No character data yet') {
        summary.innerHTML = `
            <h4>Character Summary</h4>
            <ul>
                <li><strong>Race:</strong> ${data.summary.race}</li>
                <li><strong>Class:</strong> ${data.summary.class}</li>
                <li><strong>Background:</strong> ${data.summary.background}</li>
                <li><strong>Equipment:</strong> ${data.summary.equipment} items</li>
                <li><strong>Backstory:</strong> ${data.summary.backstory}</li>
            </ul>
        `;
    } else {
        summary.innerHTML = '';
    }
    
    modal.style.display = 'block';
}

function makeCharacterChoice() {
    const choice = document.getElementById('characterChoice').value.trim();
    if (!choice) {
        alert('Please enter a choice');
        return;
    }
    
    fetch('/api/character/choice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            choice: choice,
            details: {}
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Add response to chat
            addMessage('ai', data.response);
            
            if (data.complete) {
                // Character creation complete
                closeCharacterCreation();
                showCharacterNameModal();
            } else {
                // Show next step
                showCharacterCreationStep(data);
            }
        } else {
            console.error('Failed to make choice:', data.error);
        }
    })
    .catch(error => {
        console.error('Error making character choice:', error);
    });
}

function closeCharacterCreation() {
    document.getElementById('characterCreationModal').style.display = 'none';
    document.getElementById('characterChoice').value = '';
}

function showCharacterNameModal() {
    document.getElementById('characterNameModal').style.display = 'block';
}

function closeCharacterNameModal() {
    document.getElementById('characterNameModal').style.display = 'none';
    document.getElementById('characterName').value = '';
}

function saveCharacter() {
    const characterName = document.getElementById('characterName').value.trim();
    if (!characterName) {
        alert('Please enter a character name');
        return;
    }
    
    fetch('/api/character/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: characterName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeCharacterNameModal();
            currentCharacter = data.character;
            
            // Add character creation complete message
            addMessage('ai', `Excellent! Your character ${characterName} has been created and saved. You are now ready to begin your adventure!`);
            
            // Start the campaign intro
            startCampaignIntro(characterName, data.character);
        } else {
            console.error('Failed to save character:', data.error);
        }
    })
    .catch(error => {
        console.error('Error saving character:', error);
    });
}

function startCampaignIntro(characterName, characterData) {
    const race = characterData.race.name;
    const charClass = characterData.class.name;
    const background = characterData.background.name;
    
    const introMessage = `Welcome to your adventure, ${characterName}! 

You are a ${race} ${charClass.toLowerCase()} with a ${background.toLowerCase()} background. Your journey begins in the bustling town of Neverwinter, where rumors of ancient treasures and dark forces have drawn adventurers from across the Sword Coast.

As you step into the local tavern, The Sleeping Giant, you notice several other travelers gathered around a notice board. A weathered parchment catches your eye - it speaks of a mysterious dungeon discovered in the nearby Neverwinter Wood, said to contain both great treasures and ancient secrets.

What would you like to do? You could:
- Approach the notice board to read the details
- Talk to the other adventurers in the tavern
- Speak with the tavern keeper for local gossip
- Head directly to the dungeon entrance
- Or something else entirely?

The choice is yours, brave adventurer!`;
    
    addMessage('ai', introMessage);
}

// Enhanced message handling for character creation
function addMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // If it's an AI message and character creation is active, don't show typing indicator
    if (sender === 'ai' && !characterCreationActive) {
        showTypingIndicator();
        setTimeout(() => {
            hideTypingIndicator();
        }, 1000);
    }
}

// Initialize the game flow
document.addEventListener('DOMContentLoaded', function() {
    // Show welcome screen initially
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-screen';
    welcomeDiv.innerHTML = `
        <h1>🎲 DnD 5E Solo Adventure</h1>
        <p>Embark on an epic journey with AI-powered storytelling</p>
        <button onclick="showCampaignSelection()">Begin Your Adventure</button>
    `;
    
    // Insert welcome screen before the chat interface
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.parentNode.insertBefore(welcomeDiv, chatContainer);
    
    // Hide chat interface initially
    chatContainer.style.display = 'none';
    
    // Show chat interface after character creation
    window.showChatInterface = function() {
        document.querySelector('.welcome-screen').style.display = 'none';
        chatContainer.style.display = 'block';
    };
}); 