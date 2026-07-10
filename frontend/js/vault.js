// SentinelX Vault Module
async function initVault() {
    if (!requireAuth()) return;
    updateUserBadge();
    await loadVaultItems();
    document.getElementById('vaultForm')?.addEventListener('submit', addVaultItem);
    
    // Toggle input field type based on selected category
    document.getElementById('vaultCategory')?.addEventListener('change', (e) => {
        const textGroup = document.getElementById('textDataGroup');
        const fileGroup = document.getElementById('fileDataGroup');
        if (e.target.value === 'image') {
            if (textGroup) textGroup.style.display = 'none';
            if (fileGroup) fileGroup.style.display = 'block';
            document.getElementById('vaultData').removeAttribute('required');
            document.getElementById('vaultFile').setAttribute('required', 'true');
        } else {
            if (textGroup) textGroup.style.display = 'block';
            if (fileGroup) fileGroup.style.display = 'none';
            document.getElementById('vaultData').setAttribute('required', 'true');
            document.getElementById('vaultFile').removeAttribute('required');
        }
    });
}

async function loadVaultItems() {
    try {
        const res = await api.get('/vault/');
        if (res?.data) renderVaultItems(res.data);
    } catch (err) {
        showToast('Failed to load vault items', 'error');
    }
}

function renderVaultItems(items) {
    const grid = document.getElementById('vaultGrid');
    if (!grid) return;
    if (!items.length) {
        grid.innerHTML = '<div class="text-center" style="padding:60px;color:var(--text-muted)"><p>No items in your vault yet</p></div>';
        return;
    }
    grid.innerHTML = items.map(item => {
        const isImage = item.category === 'image';
        return `
            <div class="vault-item ${item.category} animate-scale-in">
                <div class="vault-item-header">
                    <span class="vault-item-title">${categoryIcon(item.category)} ${escapeHtml(item.title)}</span>
                    <span class="vault-item-category badge badge-${item.category === 'password' ? 'high' : 'safe'}">${item.category}</span>
                </div>
                <div class="vault-item-data masked" id="vaultData-${item.id}" style="word-break: break-all; max-height: 240px; overflow-y: auto;">
                    ${isImage ? '<div class="image-placeholder" style="text-align:center; padding:12px 0"><span style="font-size: 24px">🖼️</span><br><span style="font-size: 11px; color: var(--text-muted)">Encrypted Image</span></div>' : '••••••••••••'}
                </div>
                <div class="vault-item-actions">
                    <button class="btn btn-outline btn-sm" onclick="toggleVaultItem(${item.id})">View</button>
                    ${isImage ? '' : `<button class="btn btn-outline btn-sm" onclick="copyVaultItem(${item.id})">Copy</button>`}
                    <button class="btn btn-danger btn-sm" onclick="deleteVaultItem(${item.id})">Delete</button>
                </div>
                <div class="vault-item-meta">Created: ${formatDate(item.created_at)}</div>
            </div>
        `;
    }).join('');
}

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

async function addVaultItem(e) {
    e.preventDefault();
    const title = document.getElementById('vaultTitle').value.trim();
    const category = document.getElementById('vaultCategory').value;
    let data = '';

    if (category === 'image') {
        const fileInput = document.getElementById('vaultFile');
        const file = fileInput?.files[0];
        if (!file) {
            showToast('Please select an image file', 'warning');
            return;
        }
        if (file.size > 2 * 1024 * 1024) {
            showToast('Image size must be less than 2MB', 'warning');
            return;
        }
        try {
            data = await readFileAsBase64(file);
        } catch (err) {
            showToast('Failed to read file', 'error');
            return;
        }
    } else {
        data = document.getElementById('vaultData').value.trim();
    }

    if (!title || !data) { showToast('Title and data are required', 'warning'); return; }

    try {
        await api.post('/vault/', { title, category, data });
        showToast('Vault item created', 'success');
        document.getElementById('vaultForm').reset();
        
        // Reset category view state
        const textGroup = document.getElementById('textDataGroup');
        const fileGroup = document.getElementById('fileDataGroup');
        if (textGroup) textGroup.style.display = 'block';
        if (fileGroup) fileGroup.style.display = 'none';
        document.getElementById('vaultData').setAttribute('required', 'true');
        document.getElementById('vaultFile').removeAttribute('required');

        await loadVaultItems();
    } catch (err) {
        showToast(err.message || 'Failed to create item', 'error');
    }
}

async function toggleVaultItem(id) {
    const el = document.getElementById(`vaultData-${id}`);
    if (!el) return;
    if (el.classList.contains('masked')) {
        try {
            const res = await api.get(`/vault/${id}`);
            if (res?.data) {
                const decrypted = res.data.decrypted_data;
                if (res.data.category === 'image' || decrypted.startsWith('data:image/')) {
                    el.innerHTML = `<img src="${decrypted}" class="decrypted-image-preview" style="max-width: 100%; max-height: 200px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); object-fit: contain; margin-top: 8px;">`;
                } else {
                    el.textContent = decrypted;
                }
                el.classList.remove('masked');
            }
        } catch (err) { showToast('Failed to decrypt', 'error'); }
    } else {
        const itemCard = el.closest('.vault-item');
        if (itemCard && itemCard.classList.contains('image')) {
            el.innerHTML = '<div class="image-placeholder" style="text-align:center; padding:12px 0"><span style="font-size: 24px">🖼️</span><br><span style="font-size: 11px; color: var(--text-muted)">Encrypted Image</span></div>';
        } else {
            el.textContent = '••••••••••••';
        }
        el.classList.add('masked');
    }
}

async function copyVaultItem(id) {
    try {
        const res = await api.get(`/vault/${id}`);
        if (res?.data) {
            await navigator.clipboard.writeText(res.data.decrypted_data);
            showToast('Copied to clipboard', 'success');
        }
    } catch (err) { showToast('Failed to copy', 'error'); }
}

async function deleteVaultItem(id) {
    if (!confirm('Delete this vault item?')) return;
    try {
        await api.delete(`/vault/${id}`);
        showToast('Vault item deleted', 'success');
        await loadVaultItems();
    } catch (err) { showToast('Failed to delete', 'error'); }
}

document.addEventListener('DOMContentLoaded', initVault);
