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
                // 🔥 ПЕРЕДАЁМ loadUsers как третий аргумент
                onDelete: (id) => deleteUser(id, users, loadUsers)
            });
        } catch (e) { 
            list.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`; 
        }
    };

    window.editItem = openUserForm;
    // 🔥 ПЕРЕДАЁМ loadUsers как третий аргумент
    window.deleteItem = (id) => deleteUser(id, null, loadUsers);
    
    document.getElementById('add-user-btn').onclick = () => openUserForm();

    async function openUserForm(id = null) {
        const wrap = document.createElement('div');
        let user = {};
        
        if (id) {
            try {
                user = await get(`/v1/users/${id}`);
            } catch (e) {
                alert(`Не удалось загрузить данные: ${e.message}`);
                return;
            }
        }
        
        const fields = [
            { key: 'username', label: 'Username', required: true, value: user.username || '' },
            { key: 'email', label: 'Email', type: 'email', required: true, value: user.email || '' },
            { key: 'full_name', label: 'Full Name', required: true, value: user.full_name || '' },
            { 
                key: 'role', 
                label: 'Роль', 
                type: 'select', 
                options: [
                    { value: 'user', label: 'User' }, 
                    { value: 'manager', label: 'Manager' }, 
                    { value: 'admin', label: 'Admin' }
                ], 
                value: user.role || 'user' 
            },
            { 
                key: 'is_active', 
                label: 'Активен', 
                type: 'select', 
                options: [
                    { value: 'true', label: 'Да' }, 
                    { value: 'false', label: 'Нет' }
                ], 
                value: String(user.is_active ?? true) 
            }
        ];

        if (!id) {
            fields.push(
                { key: 'password', label: 'Пароль', type: 'password', required: true },
                { key: 'repeat_password', label: 'Повторите пароль', type: 'password', required: true }
            );
        }
        
        renderForm(wrap, {
            fields,
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                data.is_active = data.is_active === 'true';
                if (data.team_id) data.team_id = parseInt(data.team_id);
                
                if (!id) {
                    if (data.password !== data.repeat_password) {
                        alert('❌ Пароли не совпадают!');
                        return;
                    }
                }

                try {
                    if (id) {
                        await patch(`/v1/users/${id}`, data);
                    } else {
                        await post('/v1/users/', data);
                    }
                    modal.remove();
                    await loadUsers();
                    showNotification(id ? 'Пользователь обновлен' : 'Пользователь успешно создан', 'success');
                } catch (e) { 
                    alert(`Ошибка сохранения: ${e.message}`); 
                }
            }
        });
        const modal = showModal(id ? 'Редактировать пользователя' : 'Новый пользователь', wrap);
    }

    await loadUsers();
}

// =====================================================================
// 🔥 ФУНКЦИЯ УДАЛЕНИЯ: добавлен параметр reloadCallback
// =====================================================================
async function deleteUser(id, usersList, reloadCallback) {
    const user = usersList?.find(u => String(u.id) === String(id));
    const userName = user ? user.username : `ID ${id}`;
    
    const confirmed = confirm(`Вы уверены, что хотите удалить пользователя "${userName}"?\n\nЭто действие нельзя отменить.`);
    if (!confirmed) return;
    
    const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete`) || 
                      document.querySelector(`button[onclick*="deleteItem('${id}')"]`);
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.textContent = '...';
    }
    
    try {
        await del(`/v1/users/${id}`);
        showNotification(`Пользователь "${userName}" успешно удален`, 'success');
        
        // 🔥 Вызываем переданный callback вместо прямой ссылки на loadUsers
        if (typeof reloadCallback === 'function') {
            await reloadCallback();
        }
    } catch (error) {
        console.error('Ошибка при удалении:', error);
        
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = 'Del';
        }
        
        const errMsg = error.message || 'Неизвестная ошибка';
        
        if (errMsg.includes('403') || errMsg.toLowerCase().includes('forbidden')) {
            alert(`❌ Недостаточно прав для удаления этого пользователя.`);
        } else if (errMsg.includes('404') || errMsg.toLowerCase().includes('not found')) {
            alert(`❌ Пользователь не найден (возможно, уже удален).`);
            if (typeof reloadCallback === 'function') await reloadCallback();
        } else if (errMsg.includes('409') || errMsg.toLowerCase().includes('conflict')) {
            alert(`❌ Невозможно удалить "${userName}".\n\nПользователь связан с другими данными.`);
        } else if (errMsg.includes('Failed to fetch') || errMsg.includes('NetworkError')) {
            alert(`❌ Ошибка сети. Проверьте подключение.`);
        } else {
            alert(`❌ Ошибка при удалении:\n\n${errMsg}`);
        }
    }
}

// =====================================================================
// УВЕДОМЛЕНИЯ
// =====================================================================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? '#16a34a' : type === 'error' ? '#dc2626' : '#2563eb';
    
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px;
        padding: 1rem 1.5rem; border-radius: 8px;
        background: ${bgColor}; color: white; font-weight: 500;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.2);
        z-index: 10000; animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}