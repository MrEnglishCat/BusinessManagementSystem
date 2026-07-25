import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderUsers(container) {
    container.innerHTML = `
        <h2>Пользователи</h2>
        <button id="add-user-btn" class="btn-primary">+ Добавить пользователя</button>
        <div id="users-list" class="mt-4"></div>
    `;

    const loadUsers = async () => {
        const list = document.getElementById('users-list');
        list.innerHTML = '<p>Загрузка...</p>';
        try {
            const users = await get('/v1/users/');
            list.innerHTML = '';
            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'username', label: 'Username' },
                    { key: 'email', label: 'Email' },
                    { key: 'role', label: 'Роль', render: r => `<span class="badge status-${r.role}">${r.role}</span>` },
                    { key: 'is_active', label: 'Активен', render: r => r.is_active ? '✅' : '❌' }
                ],
                rows: users || [],
                onEdit: (id) => openUserForm(id),
                onDelete: async (id) => {
                    if (confirm('Удалить пользователя?')) {
                        await del(`/v1/users/${id}`);
                        loadUsers();
                    }
                }
            });
        } catch (e) { list.innerHTML = `<p class="error">${e.message}</p>`; }
    };

    window.editItem = openUserForm;
    window.deleteItem = async (id) => { await del(`/v1/users/${id}`); loadUsers(); };
    document.getElementById('add-user-btn').onclick = () => openUserForm();

    async function openUserForm(id = null) {
        const wrap = document.createElement('div');
        const user = id ? (await get(`/v1/users/${id}`)) : {};
        
        renderForm(wrap, {
            fields: [
                { key: 'username', label: 'Username', required: true, value: user.username },
                { key: 'email', label: 'Email', type: 'email', required: true, value: user.email },
                { key: 'full_name', label: 'Full Name', required: true, value: user.full_name },
                { key: 'role', label: 'Роль', type: 'select', options: [
                    { value: 'user', label: 'User' }, { value: 'manager', label: 'Manager' }, { value: 'admin', label: 'Admin' }
                ], value: user.role || 'user' },
                { key: 'is_active', label: 'Активен', type: 'select', options: [
                    { value: 'true', label: 'Да' }, { value: 'false', label: 'Нет' }
                ], value: user.is_active ? 'true' : 'false' }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                data.is_active = data.is_active === 'true';
                try {
                    if (id) await patch(`/v1/users/${id}`, data);
                    else await post('/v1/users/', data); // Примечание: для создания может потребоваться пароль, добавьте поля при необходимости
                    modal.remove();
                    loadUsers();
                } catch (e) { alert(e.message); }
            }
        });
        const modal = showModal(id ? 'Редактировать пользователя' : 'Новый пользователь', wrap);
    }

    await loadUsers();
}