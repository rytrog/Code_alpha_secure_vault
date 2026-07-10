// SentinelX Reports Module
async function initReports() {
    if (!requireAdmin()) return;
    updateUserBadge();
    await loadReports();
}

async function loadReports() {
    try {
        const res = await api.get('/reports/');
        if (res?.data) renderReports(res.data);
    } catch (err) {
        showToast('Failed to load reports', 'error');
    }
}

function renderReports(reports) {
    const container = document.getElementById('reportsList');
    if (!container) return;
    if (!reports.length) {
        container.innerHTML = '<div class="text-center" style="padding:60px;color:var(--text-muted)"><p>No reports generated yet</p></div>';
        return;
    }
    container.innerHTML = reports.map(r => `
        <div class="card animate-fade-in-up" style="margin-bottom:16px;cursor:pointer" onclick="viewReport(${r.id})">
            <div class="flex-between">
                <div>
                    <h4 style="font-size:15px;font-weight:600">${r.report_type.charAt(0).toUpperCase() + r.report_type.slice(1)} Security Report</h4>
                    <p style="font-size:12px;color:var(--text-muted);margin-top:4px">Generated ${formatDate(r.generated_at)} by ${escapeHtml(r.generated_by)}</p>
                </div>
                <span class="badge badge-safe">${r.report_type}</span>
            </div>
        </div>
    `).join('');
}

async function generateReport() {
    const btn = document.getElementById('generateReportBtn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="loading-spinner" style="width:18px;height:18px;border-width:2px;margin:0"></span> Generating...'; }
    try {
        const res = await api.post('/ai/report');
        showToast('AI Report generated!', 'success');
        await loadReports();
    } catch (err) {
        showToast('Failed to generate report: ' + err.message, 'error');
    }
    if (btn) { btn.disabled = false; btn.innerHTML = 'Generate AI Report'; }
}

async function viewReport(id) {
    try {
        const res = await api.get(`/reports/${id}`);
        if (res?.data) {
            const modal = document.getElementById('reportModal');
            const content = document.getElementById('reportModalContent');
            if (modal && content) {
                content.innerHTML = `<div style="font-size:14px;line-height:1.8;color:var(--text-secondary)">${formatMarkdown(res.data.content)}</div>`;
                modal.classList.add('active');
            }
        }
    } catch (err) { showToast('Failed to load report', 'error'); }
}

function closeReportModal() {
    document.getElementById('reportModal')?.classList.remove('active');
}

function exportReport() {
    const content = document.getElementById('reportModalContent')?.textContent;
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `sentinelx-report-${Date.now()}.txt`;
    a.click();
    showToast('Report exported', 'success');
}

document.addEventListener('DOMContentLoaded', initReports);
