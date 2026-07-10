// SentinelX AI Assistant Module
async function initAI() {
    if (!requireAdmin()) return;
    updateUserBadge();
    await loadChatHistory();
    document.getElementById('chatForm')?.addEventListener('submit', sendMessage);
}

async function loadChatHistory() {
    try {
        const res = await api.get('/ai/chat/history');
        if (res?.data) renderChatMessages(res.data);
    } catch (err) {
        console.error('Failed to load chat history:', err);
    }
}

function renderChatMessages(messages) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    if (!messages.length) {
        container.innerHTML = `
            <div class="text-center" style="padding:60px;color:var(--text-muted)">
                <p style="font-size:16px;font-weight:600;margin-bottom:8px">SentinelX AI Security Assistant</p>
                <p>Ask me about security events, attack patterns, or system health.</p>
                <div style="margin-top:20px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
                    <button class="btn btn-outline btn-sm" onclick="quickChat('Summarize today\\'s attacks')">Today's attacks</button>
                    <button class="btn btn-outline btn-sm" onclick="quickChat('Most dangerous IP today?')">Dangerous IPs</button>
                    <button class="btn btn-outline btn-sm" onclick="quickChat('Show login activity')">Login activity</button>
                    <button class="btn btn-outline btn-sm" onclick="quickChat('Security recommendations')">Recommendations</button>
                </div>
            </div>`;
        return;
    }
    container.innerHTML = messages.map(m => chatBubble(m.role, m.content, m.timestamp)).join('');
    container.scrollTop = container.scrollHeight;
}

function chatBubble(role, content, timestamp) {
    const isUser = role === 'user';
    return `
        <div class="chat-bubble ${isUser ? 'user' : 'assistant'} animate-fade-in-up" style="
            display:flex;gap:12px;margin-bottom:16px;flex-direction:${isUser ? 'row-reverse' : 'row'};
        ">
            <div style="width:36px;height:36px;border-radius:50%;background:${isUser ? 'var(--accent-blue)' : 'var(--accent-purple)'};display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;color:white;flex-shrink:0">
                ${isUser ? 'U' : 'AI'}
            </div>
            <div style="max-width:70%;padding:14px 18px;border-radius:${isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px'};background:${isUser ? 'rgba(26,115,232,0.1)' : 'var(--bg-card)'};border:1px solid var(--border-color)">
                <div style="font-size:14px;line-height:1.6;color:var(--text-primary)">${isUser ? escapeHtml(content) : formatMarkdown(content)}</div>
                <span style="font-size:10px;color:var(--text-muted);margin-top:6px;display:block">${timeAgo(timestamp)}</span>
            </div>
        </div>
    `;
}

async function sendMessage(e) {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const container = document.getElementById('chatMessages');
    // Remove placeholder if present
    const placeholder = container.querySelector('.text-center');
    if (placeholder) placeholder.remove();

    // Add user message
    container.innerHTML += chatBubble('user', message, new Date().toISOString());
    input.value = '';

    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    container.innerHTML += `<div id="${typingId}" class="chat-bubble assistant animate-fade-in-up" style="display:flex;gap:12px;margin-bottom:16px">
        <div style="width:36px;height:36px;border-radius:50%;background:var(--accent-purple);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;color:white;flex-shrink:0">AI</div>
        <div style="padding:14px 18px;border-radius:16px 16px 16px 4px;background:var(--bg-card);border:1px solid var(--border-color)">
            <div class="loading-spinner" style="width:24px;height:24px;border-width:2px;margin:0"></div>
        </div>
    </div>`;
    container.scrollTop = container.scrollHeight;

    try {
        const res = await api.post('/ai/chat', { message });
        document.getElementById(typingId)?.remove();
        if (res?.data?.reply) {
            container.innerHTML += chatBubble('assistant', res.data.reply, new Date().toISOString());
        }
    } catch (err) {
        document.getElementById(typingId)?.remove();
        container.innerHTML += chatBubble('assistant', 'Sorry, I encountered an error. Please try again.', new Date().toISOString());
    }
    container.scrollTop = container.scrollHeight;
}

function quickChat(message) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = message;
        document.getElementById('chatForm')?.dispatchEvent(new Event('submit'));
    }
}

async function clearChat() {
    if (!confirm('Clear all chat history?')) return;
    try {
        await api.delete('/ai/chat/clear');
        showToast('Chat history cleared', 'success');
        await loadChatHistory();
    } catch (err) {
        showToast('Failed to clear chat', 'error');
    }
}

document.addEventListener('DOMContentLoaded', initAI);
