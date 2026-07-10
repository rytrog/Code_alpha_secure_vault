// SentinelX User Management Page Controller
let usersRefreshInterval;

async function initUsersPage() {
    if (!requireAdmin()) return;
    updateUserBadge();
    await loadUsersDatabase();
    
    // Auto-refresh the user database every 3 seconds for instant management sync
    usersRefreshInterval = setInterval(loadUsersDatabase, 3000);
}

async function loadUsersDatabase() {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;

    try {
        const res = await api.get('/users/');
        if (res?.data) {
            renderUserTable(res.data);
        } else {
            showNoUsers(tbody);
        }
    } catch (err) {
        showToast('Failed to load user registry', 'error');
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--accent-red);padding:24px;">Failed to load user database. ${err.message}</td></tr>`;
    }
}

function renderUserTable(users) {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;

    const currentUser = api.getUser();

    if (!users.length) {
        showNoUsers(tbody);
        return;
    }

    tbody.innerHTML = users.map(u => {
        const isSelf = currentUser && currentUser.username === u.username;
        const statusBadge = u.is_active 
            ? '<span class="badge badge-safe">✓ Active</span>' 
            : '<span class="badge badge-blocked">✘ Disabled</span>';
            
        const roleBadge = u.role === 'admin'
            ? '<span class="badge badge-high" style="text-transform:uppercase;font-weight:600">Admin</span>'
            : '<span class="badge badge-allowed" style="text-transform:uppercase;font-weight:500">User</span>';

        return `
            <tr class="stagger-item">
                <td class="mono" style="font-size:12px;color:var(--text-muted)">#${u.id}</td>
                <td style="font-weight:600;color:var(--text-primary)">${escapeHtml(u.username)} ${isSelf ? '<span style="font-size:11px;color:var(--accent-blue);font-weight:normal">(You)</span>' : ''}</td>
                <td style="color:var(--text-secondary)">${escapeHtml(u.email)}</td>
                <td>${roleBadge}</td>
                <td>${statusBadge}</td>
                <td style="color:var(--text-muted);font-size:13px">${formatDate(u.created_at)}</td>
                <td style="text-align:right">
                    <div class="action-btn-group" style="justify-content:flex-end">
                        ${!isSelf ? `
                            <button class="action-btn btn-primary" onclick="changeUserRole(${u.id}, '${u.role}')" title="Change Permissions">
                                ${u.role === 'admin' ? 'Demote to User' : 'Make Admin'}
                            </button>
                            <button class="action-btn" onclick="toggleUserStatus(${u.id})" title="Toggle Access Status">
                                ${u.is_active ? 'Disable' : 'Enable'}
                            </button>
                        ` : ''}
                        <button class="action-btn" onclick="resetUserPassword(${u.id})" title="Reset to default password">
                            Reset Password
                        </button>
                        ${!isSelf ? `
                            <button class="action-btn btn-danger" onclick="deleteUserAccount(${u.id})" title="Permanently Delete Account">
                                Delete
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function showNoUsers(tbody) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);padding:24px;">No registered users found in database.</td></tr>`;
}

// Administrative Actions:

async function changeUserRole(userId, currentRole) {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    const actionText = newRole === 'admin' ? 'promote this user to Admin' : 'demote this user to Standard User';
    
    if (!confirm(`Are you sure you want to ${actionText}?`)) return;

    try {
        await api.patch(`/users/${userId}/role?new_role=${newRole}`);
        showToast('User role updated successfully', 'success');
        await loadUsersDatabase();
    } catch (err) {
        showToast(err.message || 'Failed to update user role', 'error');
    }
}

async function toggleUserStatus(userId) {
    try {
        await api.patch(`/users/${userId}/toggle`);
        showToast('User status updated', 'success');
        await loadUsersDatabase();
    } catch (err) {
        showToast(err.message || 'Failed to toggle status', 'error');
    }
}

async function resetUserPassword(userId) {
    if (!confirm("Are you sure you want to reset this user's password to the default ('Reset@2026!')?")) return;

    try {
        await api.patch(`/users/${userId}/reset-password`);
        showToast('Password reset to default (Reset@2026!) successfully', 'success');
    } catch (err) {
        showToast(err.message || 'Failed to reset password', 'error');
    }
}

async function deleteUserAccount(userId) {
    if (!confirm('WARNING: Are you sure you want to permanently delete this user account? All their vault secrets will be lost.')) return;

    try {
        await api.delete(`/users/${userId}`);
        showToast('User account deleted successfully', 'success');
        await loadUsersDatabase();
    } catch (err) {
        showToast(err.message || 'Failed to delete user', 'error');
    }
}
