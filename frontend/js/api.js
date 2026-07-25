const API_BASE = 'http://127.0.0.1:8000'; // Или ваш порт

async function apiRequest(path, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    
    // Обработка 401 (истекший токен)
    if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.hash = '#/login';
        throw new Error('Сессия истекла. Войдите снова.');
    }

    const json = await res.json().catch(() => ({}));

    // Обработка вашего BaseResponse
    if (json.status === 'error') {
        throw new Error(json.message || JSON.stringify(json.errors));
    }
    if (!res.ok) {
        throw new Error(json.detail || `HTTP Error: ${res.status}`);
    }

    return json.data; // Возвращаем только полезную нагрузку
}

export const get = (path) => apiRequest(path, { method: 'GET' });
export const post = (path, body) => apiRequest(path, { method: 'POST', body: JSON.stringify(body) });
export const patch = (path, body) => apiRequest(path, { method: 'PATCH', body: JSON.stringify(body) });
export const del = (path) => apiRequest(path, { method: 'DELETE' });

// Спец. метод для login (требует form-urlencoded, а не JSON)
export async function login(username, password) {
    const body = new URLSearchParams({ username, password, grant_type: 'password' });
    const res = await fetch(`${API_BASE}/auth/jwt/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Ошибка входа');
    }
    return res.json(); // Вернет { access_token, token_type }
}