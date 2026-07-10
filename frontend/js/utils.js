// SentinelX Utility Functions

function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const icons = { success: '✓', error: '✘', warning: '!', info: 'i' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
}

function formatDate(dateStr) {
    if (!dateStr || dateStr === 'None') return '-';
    const d = new Date(dateStr);
    return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function timeAgo(dateStr) {
    if (!dateStr || dateStr === 'None') return '-';
    const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
    if (diff < 60) return `${Math.floor(diff)}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function severityBadge(severity) {
    const cls = { safe: 'badge-safe', medium: 'badge-medium', high: 'badge-high', critical: 'badge-critical' };
    return `<span class="badge ${cls[severity] || 'badge-safe'}">${severity || 'safe'}</span>`;
}

function actionBadge(action) {
    const isBlocked = action === 'blocked';
    return `<span class="badge ${isBlocked ? 'badge-blocked' : 'badge-allowed'}">${isBlocked ? '✘ Blocked' : '✓ Allowed'}</span>`;
}

// Color coding based on Google Cloud theme
function threatScoreColor(score) {
    if (score <= 30) return 'var(--accent-green)';
    if (score <= 60) return 'var(--accent-orange)';
    if (score <= 80) return 'var(--accent-red)';
    return 'var(--accent-red)';
}

function categoryIcon(cat) {
    const icons = { note: '[Note]', password: '[Pass]', api_key: '[Key]', document: '[Doc]', banking: '[Bank]', credential: '[Cred]', image: '[Img]' };
    return icons[cat] || '[Doc]';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function requireAuth() {
    if (!api.getToken()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function isAdmin() {
    const user = api.getUser();
    return user && user.role === 'admin';
}

function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
        window.location.href = 'vault.html';
        return false;
    }
    return true;
}

async function loadComponent(id, file) {
    try {
        const res = await fetch(`components/${file}`);
        const html = await res.text();
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = html;
            // Automatically hide admin navigation links for standard users
            if (file === 'sidebar.html') {
                const user = api.getUser();
                if (user && user.role !== 'admin') {
                    el.querySelectorAll('#nav-dashboard, #nav-attacks, #nav-ai, #nav-reports, #nav-users').forEach(item => {
                        if (item) item.style.display = 'none';
                    });
                }
            }
        }
    } catch (e) {
        console.error(`Failed to load component ${file}:`, e);
    }
}

function updateUserBadge() {
    const user = api.getUser();
    if (!user) return;
    const nameEl = document.querySelector('.user-info .name');
    const roleEl = document.querySelector('.user-info .role');
    const avatarEl = document.querySelector('.user-avatar');
    if (nameEl) nameEl.textContent = user.username;
    if (roleEl) roleEl.textContent = user.role;
    if (avatarEl) avatarEl.textContent = user.username.charAt(0).toUpperCase();
}

// Mobile sidebar toggle with high stability & hardware acceleration
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    let backdrop = document.getElementById('sidebarBackdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'sidebarBackdrop';
        backdrop.className = 'sidebar-backdrop';
        backdrop.addEventListener('click', toggleSidebar);
        document.body.appendChild(backdrop);
    }

    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        backdrop.classList.remove('active');
    } else {
        sidebar.classList.add('open');
        backdrop.classList.add('active');
    }
}

// Client-side markdown-to-HTML parser for structured and colorful AI output
function formatMarkdown(text) {
    if (!text) return "";
    
    // Clean carriage returns first to make multi-line regex matching 100% reliable on Windows
    let html = escapeHtml(text).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    
    // Replace custom priority headers with colored platform badges
    html = html.replace(/^#### High Priority$/gm, '<div class="badge badge-high" style="margin: 14px 0 8px; display: inline-block;">High Priority</div>');
    html = html.replace(/^#### Medium Priority$/gm, '<div class="badge badge-medium" style="margin: 14px 0 8px; display: inline-block;">Medium Priority</div>');
    html = html.replace(/^#### Low Priority$/gm, '<div class="badge badge-safe" style="margin: 14px 0 8px; display: inline-block;">Low Priority</div>');
    
    // Replace standard headers:
    // ##### -> h6
    html = html.replace(/^##### (.*?)$/gm, '<h6 style="margin:12px 0 6px;color:var(--text-muted);font-weight:500;font-size:12px;text-transform:uppercase;">$1</h6>');
    // #### -> h5 (e.g. date)
    html = html.replace(/^#### (.*?)$/gm, '<h5 style="margin:12px 0 6px;color:var(--text-muted);font-weight:500;font-size:13px">$1</h5>');
    // ### -> Banner heading (Executive Summary, Risk Assessment)
    html = html.replace(/^### (.*?)$/gm, '<h3 style="margin: 28px 0 14px; padding: 8px 12px; background: var(--bg-primary); border-left: 4px solid var(--accent-blue); color: var(--text-primary); font-weight: 600; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">$1</h3>');
    // ## -> Secondary heading
    html = html.replace(/^## (.*?)$/gm, '<h4 style="margin:24px 0 12px;color:var(--accent-purple);font-weight:600;font-size:16px;border-bottom:1px solid var(--border-color);padding-bottom:6px;">$1</h4>');
    // # -> Main Document Heading
    html = html.replace(/^# (.*?)$/gm, '<h2 style="margin:20px 0 15px;color:var(--accent-blue);font-weight:700;font-size:20px;text-align:center;padding-bottom:10px;border-bottom:2px solid var(--border-color);">$1</h2>');

    // Replace bold text: **text** -> strong with dark color
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--text-primary);font-weight:600">$1</strong>');
    
    // Replace inline code: `code` -> red badge
    html = html.replace(/`(.*?)`/g, '<code class="mono" style="background:var(--bg-primary);padding:2px 6px;border-radius:4px;font-size:12px;color:var(--accent-red);border:1px solid var(--border-color)">$1</code>');
    
    // Replace list items with clean spacing:
    // Indented sub-lists
    html = html.replace(/^\s*[\+\-\*]\s+(.*?)$/gm, '<li style="margin-left:24px;list-style-type:circle;margin-bottom:6px;color:var(--text-secondary);font-size:13.5px;line-height:1.6">$1</li>');
    // Main lists
    html = html.replace(/^[\+\-\*]\s+(.*?)$/gm, '<li style="margin-left:14px;list-style-type:disc;margin-bottom:8px;color:var(--text-secondary);font-size:13.5px;line-height:1.6">$1</li>');
    
    // Convert newlines to breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
}
