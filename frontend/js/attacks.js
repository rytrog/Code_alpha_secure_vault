// SentinelX Attacks Module
let attacksRefreshInterval;

async function initAttacks() {
    if (!requireAdmin()) return;
    updateUserBadge();
    await loadAttackLogs();
    document.getElementById('attackSearch')?.addEventListener('input', debounce(searchAttacks));
    document.getElementById('severityFilter')?.addEventListener('change', filterAttacks);
    
    // Auto-refresh the logs table every 3 seconds for instant log visibility
    attacksRefreshInterval = setInterval(loadAttackLogs, 3000);
}

async function loadAttackLogs() {
    // If the user is currently searching or filtering, skip auto-refresh to prevent UI disruption
    const searchVal = document.getElementById('attackSearch')?.value.trim();
    const filterVal = document.getElementById('severityFilter')?.value;
    if (searchVal || (filterVal && filterVal !== 'all')) return;

    try {
        const res = await api.get('/attacks/?limit=100');
        if (res?.data) renderAttackTable(res.data);
    } catch (err) {
        showToast('Failed to load attack logs', 'error');
    }
}

function renderAttackTable(logs) {
    const tbody = document.getElementById('attackTableBody');
    if (!tbody) return;
    if (!logs.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center" style="padding:40px;color:var(--text-muted)">No attack logs found</td></tr>';
        return;
    }
    tbody.innerHTML = logs.map(log => `
        <tr class="animate-fade-in-up">
            <td class="mono" style="font-size:11px">${timeAgo(log.timestamp)}</td>
            <td class="mono">${escapeHtml(log.ip_address)}</td>
            <td>${escapeHtml(log.endpoint)}</td>
            <td><span class="mono" style="font-size:12px;color:${threatScoreColor(log.threat_score)}">${log.threat_score}</span></td>
            <td>${escapeHtml(log.attack_type || '-')}</td>
            <td>${severityBadge(log.severity)}</td>
            <td>${actionBadge(log.action)}</td>
            <td>
                <button class="btn btn-outline btn-sm" onclick="explainAttack(${log.id})" title="AI Explain">Explain</button>
            </td>
        </tr>
    `).join('');
}

async function searchAttacks() {
    const query = document.getElementById('attackSearch')?.value.trim();
    const severity = document.getElementById('severityFilter')?.value;
    if (!query && !severity) return loadAttackLogs();

    const params = new URLSearchParams();
    if (query) params.set('ip', query);
    if (severity) params.set('severity', severity);

    try {
        const res = await api.get(`/attacks/search?${params.toString()}`);
        if (res?.data) renderAttackTable(res.data);
    } catch (err) {
        showToast('Search failed', 'error');
    }
}

function filterAttacks() { searchAttacks(); }

async function explainAttack(logId) {
    const modal = document.getElementById('aiModal');
    const content = document.getElementById('aiModalContent');
    if (!modal || !content) return;

    modal.classList.add('active');
    content.innerHTML = '<div class="loading-spinner"></div><p class="text-center" style="color:var(--text-muted);margin-top:12px">AI is analyzing this attack...</p>';

    try {
        const res = await api.post('/ai/explain', { attack_log_id: logId });
        if (res?.data) {
            const d = res.data;
            content.innerHTML = `
                <div class="animate-fade-in-up">
                    <h4 style="color:var(--accent-blue);margin-bottom:16px">${escapeHtml(d.attack_name || 'SQL Injection Analysis')}</h4>
                    <div class="form-group"><label class="form-label">Description</label><div style="color:var(--text-secondary);font-size:14px;line-height:1.6">${formatMarkdown(d.description || d.explanation || '')}</div></div>
                    <div class="form-group"><label class="form-label">Risk Level</label><p>${severityBadge((d.risk_level || '').toLowerCase())}</p></div>
                    <div class="form-group"><label class="form-label">Potential Impact</label><div style="color:var(--accent-orange);font-size:14px;line-height:1.6">${formatMarkdown(d.potential_impact || '')}</div></div>
                    <div class="form-group"><label class="form-label">Recommendation</label><div style="color:var(--accent-green);font-size:14px;line-height:1.6">${formatMarkdown(d.recommendation || '')}</div></div>
                    ${d.technical_details ? `<div class="form-group"><label class="form-label">Technical Details</label><div class="mono" style="font-size:12px;color:var(--text-muted);background:var(--bg-input);padding:12px;border-radius:8px;line-height:1.6">${formatMarkdown(d.technical_details)}</div></div>` : ''}
                </div>
            `;
        }
    } catch (err) {
        content.innerHTML = `<p style="color:var(--accent-red)">Failed to generate AI analysis: ${escapeHtml(err.message)}</p>`;
    }
}

function closeAiModal() {
    document.getElementById('aiModal')?.classList.remove('active');
}

document.addEventListener('DOMContentLoaded', initAttacks);
