import { post } from '../api.js';

export async function renderRegister(container) {
    container.innerHTML = `
        <div class="login-box">
            <h2>Регистрация</h2>
            <form id="register-form">
                <div class="form-group"><label>Email</label><input name="email" type="email" required></div>
                <div class="form-group"><label>Username</label><input name="username" required></div>
                <div class="form-group"><label>Full Name</label><input name="full_name" required></div>
                <div class="form-group">
                    <label>Роль</label>
                    <select name="role">
                        <option value="user">User</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <div class="form-group"><label>Пароль</label><input name="password" type="password" required></div>
                <div class="form-group"><label>Повторите пароль</label><input name="repeat_password" type="password" required></div>
                <button type="submit" class="btn-primary">Зарегистрироваться</button>
            </form>
            <p style="margin-top: 1rem; text-align: center;">
                Уже есть аккаунт? <a href="#/login">Войти</a>
            </p>
        </div>
    `;

    document.getElementById('register-form').onsubmit = async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const data = Object.fromEntries(fd.entries());

        try {
            await post('/auth/jwt/register', data);
            alert('Регистрация успешна! Теперь вы можете войти.');
            window.location.hash = '#/login';
        } catch (err) {
            alert(err.message);
        }
    };
}