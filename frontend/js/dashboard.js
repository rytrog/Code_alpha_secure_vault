// SentinelX Dashboard Module
let dashboardRefreshInterval;
let attackCounter = 0;

async function initDashboard() {
    if (!requireAdmin()) return;
    updateUserBadge();
    await loadDashboardData();
    startAutoRefresh();
    startLiveCounter();
}

function startAutoRefresh() {
    dashboardRefreshInterval = setInterval(loadDashboardData, 3000);
}

function startLiveCounter() {
    const counterEl = document.getElementById('liveAttackCounter');
    if (counterEl) {
        setInterval(async () => {
            try {
                const res = await api.get('/dashboard/stats');
                if (res?.data) {
                    const newCount = res.data.blocked_requests;
                    if (newCount > attackCounter) {
                        counterEl.classList.add('animate-bounce-in');
                        setTimeout(() => counterEl.classList.remove('animate-bounce-in'), 600);
                    }
                    attackCounter = newCount;
                    counterEl.textContent = attackCounter;
                }
            } catch (e) {}
        }, 3000);
    }
}

async function loadDashboardData() {
    try {
        const [statsRes, chartsRes, recentRes] = await Promise.all([
            api.get('/dashboard/stats'),
            api.get('/dashboard/charts'),
            api.get('/dashboard/recent'),
        ]);

        if (statsRes?.data) renderStats(statsRes.data);
        if (chartsRes?.data) renderCharts(chartsRes.data);
        if (recentRes?.data) renderRecentActivity(recentRes.data);
    } catch (err) {
        console.error('Dashboard load error:', err);
        showToast('Failed to load dashboard data', 'error');
    }
}

function renderStats(stats) {
    const items = {
        'totalUsers': stats.total_users,
        'encryptedRecords': stats.encrypted_records,
        'todayRequests': stats.today_requests,
        'blockedRequests': stats.blocked_requests,
        'successfulLogins': stats.successful_logins,
        'failedLogins': stats.failed_logins,
        'threatLevel': stats.threat_level,
        'securityScore': stats.security_score,
    };

    for (const [id, value] of Object.entries(items)) {
        const el = document.getElementById(id);
        if (el) {
            // Animate number change
            const oldVal = el.textContent;
            el.textContent = value;
            if (oldVal !== '-' && oldVal !== String(value)) {
                el.classList.add('animate-bounce-in');
                setTimeout(() => el.classList.remove('animate-bounce-in'), 500);
            }
        }
    }

    // Update live counter
    const counterEl = document.getElementById('liveAttackCounter');
    if (counterEl) counterEl.textContent = stats.blocked_requests;

    // Update security gauge
    const gauge = document.getElementById('gaugeValue');
    if (gauge) gauge.textContent = stats.security_score;

    const gaugeEl = document.getElementById('securityGauge');
    if (gaugeEl) {
        const deg = (stats.security_score / 100) * 360;
        let color;
        if (stats.security_score >= 80) color = 'var(--accent-green)';
        else if (stats.security_score >= 60) color = 'var(--accent-orange)';
        else if (stats.security_score >= 40) color = 'var(--accent-red)';
        else color = 'var(--accent-pink)';
        gaugeEl.style.background = `conic-gradient(${color} ${deg}deg, var(--bg-input) ${deg}deg)`;
    }

    // Update threat level indicator
    const threatDot = document.getElementById('threatDot');
    const threatText = document.getElementById('threatText');
    if (threatDot) {
        threatDot.className = `threat-dot ${stats.threat_level.toLowerCase()}`;
    }
    if (threatText) {
        threatText.textContent = stats.threat_level;
        const colors = { 'Low': 'var(--accent-green)', 'Medium': 'var(--accent-orange)', 'High': 'var(--accent-red)', 'Critical': 'var(--accent-pink)' };
        threatText.style.color = colors[stats.threat_level] || 'var(--text-primary)';
    }

    // Update threat bar
    const threatBar = document.getElementById('threatBarFill');
    if (threatBar) {
        threatBar.className = `threat-bar-fill ${stats.threat_level.toLowerCase()}`;
    }
}

function renderRecentActivity(data) {
    const attackFeed = document.getElementById('attackFeed');
    if (attackFeed && data.recent_attacks) {
        if (data.recent_attacks.length === 0) {
            attackFeed.innerHTML = '<div class="text-center" style="padding:40px;color:var(--text-muted)"><p>No recent attacks detected</p></div>';
            return;
        }
        attackFeed.innerHTML = data.recent_attacks.map((a, i) => `
            <div class="attack-feed-item animate-fade-in-left" style="animation-delay:${i * 0.05}s">
                <div class="feed-icon stat-icon ${a.action === 'blocked' ? 'red' : 'green'}" style="font-size:10px;font-weight:bold;width:auto;padding:2px 6px">
                    ${a.action === 'blocked' ? '✘ Blocked' : '✓ Allowed'}
                </div>
                <div class="feed-info">
                    <div class="title">${escapeHtml(a.attack_type || 'Request')} - ${escapeHtml(a.endpoint)}</div>
                    <div class="meta">${escapeHtml(a.ip_address)} &bull; ${timeAgo(a.timestamp)}</div>
                </div>
                <div class="feed-score" style="color:${threatScoreColor(a.threat_score)};font-family:'JetBrains Mono',monospace;font-weight:700">${a.threat_score}</div>
            </div>
        `).join('');
    }

    const loginFeed = document.getElementById('loginFeed');
    if (loginFeed && data.recent_logins) {
        if (data.recent_logins.length === 0) {
            loginFeed.innerHTML = '<div class="text-center" style="padding:40px;color:var(--text-muted)"><p>No recent login activity</p></div>';
            return;
        }
        loginFeed.innerHTML = data.recent_logins.map((l, i) => `
            <div class="attack-feed-item" style="animation-delay:${i * 0.05}s">
                <div class="feed-icon stat-icon ${l.success ? 'green' : 'red'}" style="font-size:10px;font-weight:bold;width:auto;padding:2px 6px">
                    ${l.success ? '✓ Success' : '✘ Failed'}
                </div>
                <div class="feed-info">
                    <div class="title">${escapeHtml(l.username)}</div>
                    <div class="meta">${escapeHtml(l.ip_address)} &bull; ${timeAgo(l.timestamp)}</div>
                </div>
                ${actionBadge(l.success ? 'allowed' : 'blocked')}
            </div>
        `).join('');
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardRefreshInterval) clearInterval(dashboardRefreshInterval);
});

document.addEventListener('DOMContentLoaded', initDashboard);
