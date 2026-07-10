// SentinelX Auth Module
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errEl = document.getElementById('authError');
            const btn = loginForm.querySelector('button[type="submit"]');
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            if (!username || !password) {
                showError(errEl, 'Please fill in all fields');
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner" style="width:20px;height:20px;border-width:2px;margin:0"></span>';

            try {
                const data = await api.post('/auth/login', { username, password });
                api.setToken(data.access_token);
                api.setUser({ username: data.username, role: data.role });
                showToast('Login successful!', 'success');
                const targetPage = data.role === 'admin' ? 'dashboard.html' : 'vault.html';
                setTimeout(() => window.location.href = targetPage, 500);
            } catch (err) {
                showError(errEl, err.message || 'Invalid credentials');
                btn.disabled = false;
                btn.textContent = 'Sign In';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errEl = document.getElementById('authError');
            const btn = registerForm.querySelector('button[type="submit"]');
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirmPassword').value;

            if (!username || !email || !password || !confirm) {
                showError(errEl, 'Please fill in all fields');
                return;
            }
            if (password !== confirm) {
                showError(errEl, 'Passwords do not match');
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner" style="width:20px;height:20px;border-width:2px;margin:0"></span>';

            try {
                await api.post('/auth/register', { username, email, password });
                showToast('Registration successful! Please login.', 'success');
                setTimeout(() => window.location.href = 'login.html', 1000);
            } catch (err) {
                showError(errEl, err.message || 'Registration failed');
                btn.disabled = false;
                btn.textContent = 'Create Account';
            }
        });
    }

    // Password visibility toggle
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = 'Hide';
            } else {
                input.type = 'password';
                btn.textContent = 'Show';
            }
        });
    });
});

function showError(el, msg) {
    if (el) {
        el.textContent = msg;
        el.classList.add('show');
        setTimeout(() => el.classList.remove('show'), 5000);
    }
}

function logout() {
    api.clearAuth();
    showToast('Logged out', 'info');
    window.location.href = 'login.html';
}
