import { login } from './api.js';

export function isLoggedIn() {
    return !!localStorage.getItem('token');
}
// 🔥 ЭКСПОРТ ФУНКЦИИ ПОЛУЧЕНИЯ ID ПОЛЬЗОВАТЕЛЯ
export function getCurrentUserId() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
        // JWT состоит из 3 частей, разделенных точкой. Нас интересует вторая (payload)
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join('')
        );
        
        const payload = JSON.parse(jsonPayload);
        
        // fastapi-users обычно кладет ID в поле 'sub' (как строку) или 'user_id'
        const rawId = payload.sub || payload.user_id;
        
        return rawId ? parseInt(rawId) : null;
    } catch (e) {
        console.error("Не удалось распарсить JWT токен:", e);
        return null;
    }
}
export async function handleLogin(container) {
    container.innerHTML = `
        <div class="login-box">
            <h2>Вход в BMS</h2>
            <form id="login-form">
                <div class="form-group"><label>Email</label><input name="username" required></div>
                <div class="form-group"><label>Пароль</label><input name="password" type="password" required></div>
                <button type="submit" class="btn-primary">Войти</button>
            </form>
        </div>
    `;
    document.getElementById('login-form').onsubmit = async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        try {
            const res = await login(fd.get('username'), fd.get('password'));
            localStorage.setItem('token', res.access_token);
            window.location.hash = '#/tasks';
        } catch (err) {
            alert(err.message);
        }
    };
}

export function logout() {
    localStorage.removeItem('token');
    window.location.hash = '#/login';
}


