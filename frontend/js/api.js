const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : `${window.location.origin}/api`;

const api = {
    getToken() {
        return localStorage.getItem('sentinelx_token');
    },

    setToken(token) {
        localStorage.setItem('sentinelx_token', token);
    },

    setUser(user) {
        localStorage.setItem('sentinelx_user', JSON.stringify(user));
    },

    getUser() {
        try { return JSON.parse(localStorage.getItem('sentinelx_user')); }
        catch { return null; }
    },

    clearAuth() {
        localStorage.removeItem('sentinelx_token');
        localStorage.removeItem('sentinelx_user');
    },

    headers() {
        const h = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) h['Authorization'] = `Bearer ${token}`;
        return h;
    },

    async request(method, endpoint, body = null) {
        const opts = { method, headers: this.headers() };
        if (body && method !== 'GET') opts.body = JSON.stringify(body);

        try {
            const res = await fetch(`${API_BASE}${endpoint}`, opts);
            const data = await res.json();

            if (res.status === 401) {
                this.clearAuth();
                window.location.href = 'login.html';
                return null;
            }

            if (res.status === 429) {
                showToast('Rate limit exceeded. Please wait.', 'warning');
                return null;
            }

            if (!res.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (err) {
            console.error(`API ${method} ${endpoint}:`, err);
            throw err;
        }
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, body) { return this.request('POST', endpoint, body); },
    put(endpoint, body) { return this.request('PUT', endpoint, body); },
    patch(endpoint, body) { return this.request('PATCH', endpoint, body); },
    delete(endpoint) { return this.request('DELETE', endpoint); },
};
