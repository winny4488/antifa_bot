class KomunaChat {
    constructor() {
        this.chatArea = document.getElementById('chatArea');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        this.initEventListeners();
        this.loadChatHistory();
    }

    initEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.messageInput.addEventListener('input', () => this.updateCharCount());

        document.getElementById('clearBtn').addEventListener('click', () => this.clearChat());
        document.getElementById('refineBtn').addEventListener('click', () => this.refineResponse());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportChat());
        document.getElementById('importBtn').addEventListener('click', () => this.importChat());
        document.getElementById('importFile').addEventListener('change', (e) => this.handleFileImport(e));
        document.getElementById('themeToggle').addEventListener('change', (e) => this.toggleTheme(e));
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.messageInput.value = '';
        this.updateCharCount();
        this.showLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });
            
            const data = await response.json();
            this.addMessage('Komuna', data.response);
        } catch (error) {
            this.addMessage('System', 'Error: Could not connect to Komuna. Please try again.');
        }
        
        this.showLoading(false);
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role === 'user' ? 'user-message' : 'bot-message'}`;
        
        if (role !== 'user') {
            messageDiv.innerHTML = `<strong>${role}:</strong> ${content}`;
        } else {
            messageDiv.textContent = content;
        }
        
        this.chatArea.appendChild(messageDiv);
        this.chatArea.scrollTop = this.chatArea.scrollHeight;
        this.saveChatHistory();
    }

    async clearChat() {
        try {
            await fetch('/api/clear', { method: 'POST' });
            //this.chatArea.innerHTML = '<div class="message bot-message"><strong>Komuna:</strong> Chat cleared. How can I help you?</div>';
            this.chatArea.innerHTML = '';
            this.addMessage('Komuna', 'Chat cleared. How can I help you?');
            this.saveChatHistory();
        } catch (error) {
            this.addMessage('System', 'Error clearing chat.');
        }
    }

    async refineResponse() {
        this.showLoading(true);
        try {
            const response = await fetch('/api/refine', { method: 'POST' });
            const data = await response.json();
            this.addMessage('Komuna', data.response);
        } catch (error) {
            this.addMessage('System', 'Error refining response.');
        }
        this.showLoading(false);
    }

    async exportChat() {
        try {
            const response = await fetch('/api/export');
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `komuna_chat_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            this.addMessage('System', 'Error exporting chat.');
        }
    }

    importChat() {
        document.getElementById('importFile').click();
    }

    async handleFileImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            const response = await fetch('/api/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                //location.reload();
                const result = await response.json();
                this.chatArea.innerHTML = ''; // clear old UI

                // Loop through conversation and display messages
                result.conversation.forEach(msg => {
                    this.addMessage(msg.role, msg.content);
                });

                this.saveChatHistory();
            }
        } catch (error) {
            this.addMessage('System', 'Error importing chat file.');
        }
    }

    toggleTheme(event) {
        document.body.className = event.target.checked ? 'dark-theme' : 'light-theme';
        localStorage.setItem('theme', event.target.checked ? 'dark' : 'light');
    }

    updateCharCount() {
        this.charCount.textContent = this.messageInput.value.length;
    }

    showLoading(show) {
        this.loadingIndicator.style.display = show ? 'block' : 'none';
    }

    saveChatHistory() {
        const messages = Array.from(this.chatArea.children).map(msg => ({
            role: msg.className.includes('user-message') ? 'user' : 'bot',
            content: msg.textContent
        }));
        localStorage.setItem('chatHistory', JSON.stringify(messages));
    }

    loadChatHistory() {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            const messages = JSON.parse(saved);
            this.chatArea.innerHTML = '';
            messages.forEach(msg => this.addMessage(msg.role, msg.content));
        }

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.getElementById('themeToggle').checked = false;
            document.body.className = 'light-theme';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new KomunaChat();
});
