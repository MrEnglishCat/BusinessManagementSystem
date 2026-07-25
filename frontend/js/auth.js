import { login } from './api.js';

export function isLoggedIn() {
    return !!localStorage.getItem('token');
}

export async function handleLogin(container) {
    container.innerHTML = `
        <div class="login-box">
            <h2>Вход в BMS</h2>
            <form id="login-form">
                <div class="form-group"><label>Email / Username</label><input name="username" required></div>
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