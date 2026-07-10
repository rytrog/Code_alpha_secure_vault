// SentinelX Charts Module (Chart.js)
function renderCharts(data) {
    if (data.attack_types && data.attack_types.length) renderAttackTypesChart(data.attack_types);
    if (data.daily_attacks && data.daily_attacks.length) renderDailyAttacksChart(data.daily_attacks);
    if (data.severity_distribution && data.severity_distribution.length) renderSeverityChart(data.severity_distribution);
    if (data.login_activity && data.login_activity.length) renderLoginChart(data.login_activity);
}

function renderAttackTypesChart(types) {
    const ctx = document.getElementById('attackTypesChart');
    if (!ctx) return;
    if (ctx._chart) ctx._chart.destroy();
    ctx._chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: types.map(t => t.type || 'Unknown'),
            datasets: [{
                data: types.map(t => t.count),
                backgroundColor: ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#64748b'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 12 } } },
            cutout: '65%',
        }
    });
}

function renderDailyAttacksChart(daily) {
    const ctx = document.getElementById('dailyAttacksChart');
    if (!ctx) return;
    if (ctx._chart) ctx._chart.destroy();
    ctx._chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: daily.map(d => d.date),
            datasets: [{
                label: 'Attacks',
                data: daily.map(d => d.count),
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(59,130,246,0.05)' }, beginAtZero: true }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function renderSeverityChart(severity) {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;
    if (ctx._chart) ctx._chart.destroy();
    const colors = { safe: '#10b981', medium: '#f59e0b', high: '#ef4444', critical: '#ec4899' };
    ctx._chart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: severity.map(s => s.severity),
            datasets: [{
                data: severity.map(s => s.count),
                backgroundColor: severity.map(s => colors[s.severity] || '#64748b'),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } } },
            scales: { r: { ticks: { display: false }, grid: { color: 'rgba(59,130,246,0.1)' } } }
        }
    });
}

function renderLoginChart(logins) {
    const ctx = document.getElementById('loginChart');
    if (!ctx) return;
    if (ctx._chart) ctx._chart.destroy();
    const success = logins.filter(l => l.success);
    const failed = logins.filter(l => !l.success);
    ctx._chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...new Set(logins.map(l => l.date))],
            datasets: [
                { label: 'Successful', data: success.map(l => l.count), borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, fill: true },
                { label: 'Failed', data: failed.map(l => l.count), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', tension: 0.4, fill: true },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(59,130,246,0.05)' }, beginAtZero: true }
            },
            plugins: { legend: { labels: { color: '#94a3b8' } } }
        }
    });
}
