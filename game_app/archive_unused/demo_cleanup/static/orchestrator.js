/**
 * Enhanced JavaScript for Dynamic Campaign Orchestrator Web UI
 * Provides real-time updates, advanced interactions, and smooth animations
 */

class CampaignOrchestratorUI {
    constructor() {
        this.campaignId = 'orchestrator-campaign';
        this.debugMode = false;
        this.lastUpdate = null;
        this.updateInterval = null;
        this.eventSource = null;
        this.notificationQueue = [];
        this.isProcessing = false;
        
        this.initialize();
    }
    
    initialize() {
        this.setupEventListeners();
        this.loadInitialState();
        this.startAutoRefresh();
        this.setupLocalStorage();
        this.setupKeyboardShortcuts();
    }
    
    setupEventListeners() {
        // Form submissions
        const actionForm = document.getElementById('actionForm');
        const journalForm = document.getElementById('journalForm');
        
        if (actionForm) {
            actionForm.addEventListener('submit', (e) => this.handlePlayerAction(e));
        }
        
        if (journalForm) {
            journalForm.addEventListener('submit', (e) => this.handleJournalEntry(e));
        }
        
        // Buttons
        const debugToggle = document.getElementById('debugToggle');
        const refreshBtn = document.getElementById('refreshBtn');
        
        if (debugToggle) {
            debugToggle.addEventListener('click', () => this.toggleDebugMode());
        }
        
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAll());
        }
        
        // Auto-save on input
        this.setupAutoSave();
        
        // Real-time updates
        this.setupRealTimeUpdates();
    }
    
    setupAutoSave() {
        const actionInput = document.getElementById('playerAction');
        const contextInput = document.getElementById('actionContext');
        const journalTitle = document.getElementById('journalTitle');
        const journalContent = document.getElementById('journalContent');
        
        const inputs = [actionInput, contextInput, journalTitle, journalContent];
        
        inputs.forEach(input => {
            if (input) {
                input.addEventListener('input', () => {
                    this.saveToLocalStorage();
                });
            }
        });
    }
    
    setupRealTimeUpdates() {
        // Check for new orchestration events every 10 seconds
        setInterval(() => {
            this.loadOrchestrationEvents();
        }, 10000);
        
        // Update campaign summary every 30 seconds
        setInterval(() => {
            this.loadCampaignSummary();
        }, 30000);
    }
    
    setupLocalStorage() {
        // Load saved form data
        this.loadFromLocalStorage();
        
        // Save on page unload
        window.addEventListener('beforeunload', () => {
            this.saveToLocalStorage();
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to submit action
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const actionForm = document.getElementById('actionForm');
                if (actionForm && document.activeElement.closest('#actionForm')) {
                    e.preventDefault();
                    actionForm.dispatchEvent(new Event('submit'));
                }
            }
            
            // Ctrl/Cmd + S to save journal
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                const journalForm = document.getElementById('journalForm');
                if (journalForm && document.activeElement.closest('#journalForm')) {
                    e.preventDefault();
                    journalForm.dispatchEvent(new Event('submit'));
                }
            }
            
            // F5 to refresh
            if (e.key === 'F5') {
                e.preventDefault();
                this.refreshAll();
            }
            
            // F12 to toggle debug
            if (e.key === 'F12') {
                e.preventDefault();
                this.toggleDebugMode();
            }
        });
    }
    
    saveToLocalStorage() {
        const data = {
            action: document.getElementById('playerAction')?.value || '',
            context: document.getElementById('actionContext')?.value || '',
            journalTitle: document.getElementById('journalTitle')?.value || '',
            journalContent: document.getElementById('journalContent')?.value || '',
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('orchestrator_ui_draft', JSON.stringify(data));
    }
    
    loadFromLocalStorage() {
        const saved = localStorage.getItem('orchestrator_ui_draft');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                const savedTime = new Date(data.timestamp);
                const now = new Date();
                
                // Only restore if saved within last hour
                if (now - savedTime < 3600000) {
                    if (data.action) document.getElementById('playerAction').value = data.action;
                    if (data.context) document.getElementById('actionContext').value = data.context;
                    if (data.journalTitle) document.getElementById('journalTitle').value = data.journalTitle;
                    if (data.journalContent) document.getElementById('journalContent').value = data.journalContent;
                }
            } catch (e) {
                console.warn('Failed to load saved data:', e);
            }
        }
    }
    
    async handlePlayerAction(e) {
        e.preventDefault();
        
        if (this.isProcessing) {
            this.showNotification('Please wait for the current action to complete', 'info');
            return;
        }
        
        const action = document.getElementById('playerAction').value.trim();
        const context = document.getElementById('actionContext').value.trim();
        
        if (!action) {
            this.showNotification('Please enter an action', 'error');
            return;
        }
        
        this.isProcessing = true;
        this.showLoading(true);
        
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/action', {
                method: 'POST',
                body: JSON.stringify({ action, context })
            });
            
            if (response.success) {
                this.updateCampaignStory(response.narration);
                this.updateOrchestrationEvents(response.orchestration_events);
                this.updateMemoryHighlights(response.recent_memories);
                this.showNotification('Action processed successfully!', 'success');
                
                // Clear form and localStorage
                document.getElementById('playerAction').value = '';
                document.getElementById('actionContext').value = '';
                localStorage.removeItem('orchestrator_ui_draft');
                
                // Add to action history
                this.addToActionHistory(action, response);
                
            } else {
                this.showNotification('Error: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }
    
    async handleJournalEntry(e) {
        e.preventDefault();
        
        const title = document.getElementById('journalTitle').value.trim();
        const content = document.getElementById('journalContent').value.trim();
        
        if (!title || !content) {
            this.showNotification('Please enter both title and content', 'error');
            return;
        }
        
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/journal', {
                method: 'POST',
                body: JSON.stringify({ title, content, entry_type: 'player_written' })
            });
            
            if (response.success) {
                this.showNotification('Journal entry saved!', 'success');
                document.getElementById('journalTitle').value = '';
                document.getElementById('journalContent').value = '';
                localStorage.removeItem('orchestrator_ui_draft');
                this.loadCampaignSummary();
            } else {
                this.showNotification('Error: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        }
    }
    
    async toggleDebugMode() {
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/debug/toggle', {
                method: 'POST'
            });
            
            if (response.success) {
                this.debugMode = response.debug_mode;
                const debugPanel = document.getElementById('debugPanel');
                debugPanel.classList.toggle('hidden', !this.debugMode);
                
                if (this.debugMode) {
                    this.loadDebugInfo();
                    this.showNotification('Debug mode enabled', 'success');
                } else {
                    this.showNotification('Debug mode disabled', 'info');
                }
            }
        } catch (error) {
            this.showNotification('Error toggling debug mode: ' + error.message, 'error');
        }
    }
    
    async loadInitialState() {
        await Promise.all([
            this.loadCampaignSummary(),
            this.loadOrchestrationEvents()
        ]);
    }
    
    async loadCampaignSummary() {
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/summary');
            
            if (!response.error) {
                this.updateCampaignSummary(response.campaign_summary);
                this.updateCharacterArcs(response.character_arcs);
                this.updatePlotThreads(response.plot_threads);
                this.updateMemoryHighlights(response.memory_highlights);
                this.lastUpdate = new Date();
            }
        } catch (error) {
            console.error('Error loading campaign summary:', error);
        }
    }
    
    async loadOrchestrationEvents() {
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/orchestration/events');
            
            if (!response.error) {
                this.updateOrchestrationEvents(response.events);
            }
        } catch (error) {
            console.error('Error loading orchestration events:', error);
        }
    }
    
    async loadDebugInfo() {
        if (!this.debugMode) return;
        
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/debug/info');
            
            if (!response.error) {
                this.updateDebugInfo(response);
            }
        } catch (error) {
            console.error('Error loading debug info:', error);
        }
    }
    
    async executeEvent(eventId) {
        try {
            const response = await this.makeRequest('/api/campaign/' + this.campaignId + '/orchestration/execute/' + eventId, {
                method: 'POST',
                body: JSON.stringify({ notes: 'Executed via web UI' })
            });
            
            if (response.success) {
                this.showNotification('Event executed successfully!', 'success');
                this.loadOrchestrationEvents();
                this.loadCampaignSummary();
            } else {
                this.showNotification('Error executing event: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        }
    }
    
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        const response = await fetch(url, finalOptions);
        return await response.json();
    }
    
    updateCampaignStory(narration) {
        const storyDiv = document.getElementById('campaignStory');
        const timestamp = document.getElementById('storyTimestamp');
        
        if (storyDiv && timestamp) {
            storyDiv.innerHTML = `<p class="text-gray-300 fade-in typewriter">${narration}</p>`;
            timestamp.textContent = new Date().toLocaleTimeString();
        }
    }
    
    updateOrchestrationEvents(events) {
        const eventsDiv = document.getElementById('orchestrationEvents');
        
        if (!eventsDiv) return;
        
        if (!events || events.length === 0) {
            eventsDiv.innerHTML = '<p class="text-gray-400 italic">No orchestration events at the moment...</p>';
            return;
        }
        
        eventsDiv.innerHTML = events.map(event => `
            <div class="bg-gray-700 rounded-lg p-4 fade-in priority-${event.priority >= 8 ? 'critical' : event.priority >= 6 ? 'high' : event.priority >= 4 ? 'medium' : 'low'}">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="font-semibold text-purple-300">${event.event_type}</h3>
                    <span class="text-sm text-gray-400">Priority: ${event.priority}</span>
                </div>
                <p class="text-gray-300 mb-2">${event.description}</p>
                <p class="text-sm text-blue-300 italic">${event.suggested_response}</p>
                <div class="mt-3">
                    <button onclick="ui.executeEvent('${event.id}')" class="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded text-sm transition-colors">
                        Execute Event
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    updateCampaignSummary(summary) {
        const summaryDiv = document.getElementById('campaignSummary');
        
        if (!summaryDiv) return;
        
        if (!summary) {
            summaryDiv.innerHTML = '<p class="text-gray-400 italic">No summary available</p>';
            return;
        }
        
        summaryDiv.innerHTML = `
            <div class="space-y-3">
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-orange-300 mb-1">Campaign Status</h4>
                    <p class="text-sm text-gray-300">${summary.status || 'Active'}</p>
                </div>
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-orange-300 mb-1">Progression</h4>
                    <p class="text-sm text-gray-300">${summary.progression || 'Beginning'}</p>
                </div>
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-orange-300 mb-1">Last Updated</h4>
                    <p class="text-sm text-gray-300">${this.lastUpdate ? this.lastUpdate.toLocaleTimeString() : 'Never'}</p>
                </div>
            </div>
        `;
    }
    
    updateCharacterArcs(arcs) {
        const arcsDiv = document.getElementById('characterArcs');
        
        if (!arcsDiv) return;
        
        if (!arcs || arcs.length === 0) {
            arcsDiv.innerHTML = '<p class="text-gray-400 italic">No active character arcs</p>';
            return;
        }
        
        arcsDiv.innerHTML = arcs.map(arc => `
            <div class="bg-gray-700 rounded p-3">
                <h4 class="font-semibold text-pink-300">${arc.name}</h4>
                <p class="text-sm text-gray-300">${arc.description}</p>
                <div class="mt-2">
                    <span class="text-xs bg-pink-600 px-2 py-1 rounded">${arc.arc_type}</span>
                    <span class="text-xs bg-green-600 px-2 py-1 rounded ml-1">${arc.status}</span>
                </div>
            </div>
        `).join('');
    }
    
    updatePlotThreads(threads) {
        const threadsDiv = document.getElementById('plotThreads');
        
        if (!threadsDiv) return;
        
        if (!threads || threads.length === 0) {
            threadsDiv.innerHTML = '<p class="text-gray-400 italic">No active plot threads</p>';
            return;
        }
        
        threadsDiv.innerHTML = threads.map(thread => `
            <div class="bg-gray-700 rounded p-3">
                <h4 class="font-semibold text-indigo-300">${thread.name}</h4>
                <p class="text-sm text-gray-300">${thread.description}</p>
                <div class="mt-2">
                    <span class="text-xs bg-indigo-600 px-2 py-1 rounded">Priority: ${thread.priority}</span>
                    <span class="text-xs bg-blue-600 px-2 py-1 rounded ml-1">${thread.status}</span>
                </div>
            </div>
        `).join('');
    }
    
    updateMemoryHighlights(memories) {
        const memoriesDiv = document.getElementById('memoryHighlights');
        
        if (!memoriesDiv) return;
        
        if (!memories || memories.length === 0) {
            memoriesDiv.innerHTML = '<p class="text-gray-400 italic">No recent memories</p>';
            return;
        }
        
        memoriesDiv.innerHTML = memories.map(memory => `
            <div class="bg-gray-700 rounded p-3">
                <p class="text-sm text-gray-300">${memory.content}</p>
                <div class="mt-1">
                    <span class="text-xs bg-teal-600 px-2 py-1 rounded emotion-${memory.emotion?.toLowerCase() || 'neutral'}">${memory.emotion || 'Neutral'}</span>
                </div>
            </div>
        `).join('');
    }
    
    updateDebugInfo(debugData) {
        const debugDiv = document.getElementById('debugInfo');
        
        if (!debugDiv) return;
        
        if (debugData.error) {
            debugDiv.innerHTML = `<p class="text-red-400">Error: ${debugData.error}</p>`;
            return;
        }
        
        debugDiv.innerHTML = `
            <div class="space-y-3">
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-red-300 mb-1">Memory Count</h4>
                    <p class="text-sm text-gray-300">${debugData.memory_count || 0}</p>
                </div>
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-red-300 mb-1">Pending Events</h4>
                    <p class="text-sm text-gray-300">${debugData.pending_events ? debugData.pending_events.length : 0}</p>
                </div>
                <div class="bg-gray-700 rounded p-3">
                    <h4 class="font-semibold text-red-300 mb-1">Emotional Memories</h4>
                    <p class="text-sm text-gray-300">${debugData.emotional_memories ? debugData.emotional_memories.length : 0}</p>
                </div>
            </div>
        `;
    }
    
    addToActionHistory(action, response) {
        // This could be expanded to show action history in the UI
        console.log('Action added to history:', { action, response });
    }
    
    startAutoRefresh() {
        // Auto-refresh every 5 minutes
        this.updateInterval = setInterval(() => {
            this.loadCampaignSummary();
        }, 300000);
    }
    
    refreshAll() {
        this.loadCampaignSummary();
        this.loadOrchestrationEvents();
        if (this.debugMode) {
            this.loadDebugInfo();
        }
        this.showNotification('Campaign refreshed', 'info');
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    }
    
    showNotification(message, type = 'success') {
        const toast = document.getElementById('notificationToast');
        const messageSpan = document.getElementById('notificationMessage');
        
        if (!toast || !messageSpan) return;
        
        // Set message and color
        messageSpan.textContent = message;
        
        // Set color based on type
        toast.className = 'fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 z-50';
        if (type === 'success') {
            toast.classList.add('bg-green-600', 'text-white');
        } else if (type === 'error') {
            toast.classList.add('bg-red-600', 'text-white');
        } else if (type === 'info') {
            toast.classList.add('bg-blue-600', 'text-white');
        }
        
        // Show toast
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
        }, 3000);
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// Initialize the UI when the DOM is loaded
let ui;
document.addEventListener('DOMContentLoaded', function() {
    ui = new CampaignOrchestratorUI();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (ui) {
        ui.destroy();
    }
}); 