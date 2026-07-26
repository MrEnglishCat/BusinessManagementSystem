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
            // 🔥 ПАРАЛЛЕЛЬНАЯ загрузка пользователей и команд
            const [users, teams] = await Promise.all([
                get('/v1/users/'),
                get('/v1/teams/').catch(() => []) // Если команды не загрузились — не ломаем страницу
            ]);
            
            // 🔥 Создаём Map для быстрого O(1) доступа: teamId -> teamName
            const teamMap = new Map();
            (teams || []).forEach(t => teamMap.set(t.id, t.name));
            
            list.innerHTML = '';
            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'username', label: 'Username' },
                    { key: 'email', label: 'Email' },
                    { 
                        key: 'role', 
                        label: 'Роль', 
                        render: r => `<span class="badge status-${r.role}">${r.role}</span>` 
                    },
                    // 🔥 НОВАЯ КОЛОНКА: Команда
                    { 
                        key: 'team_id', 
                        label: 'Команда', 
                        render: r => {
                            if (!r.team_id) {
                                return '<span class="no-team">— не в команде —</span>';
                            }
                            const teamName = teamMap.get(r.team_id);
                            if (!teamName) {
                                return `<span class="no-team" title="Команда ID ${r.team_id} не найдена">ID ${r.team_id} ⚠️</span>`;
                            }
                            return `<span class="team-badge">${escapeHtml(teamName)}</span>`;
                        }
                    },
                    { 
                        key: 'is_active', 
                        label: 'Активен', 
                        render: r => r.is_active ? '✅' : '❌' 
                    }
                ],
                rows: users || [],
                onEdit: (id) => openUserForm(id),
                onDelete: (id) => deleteUser(id, users, loadUsers)
            });
        } catch (e) { 
            list.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`; 
        }
    };

    window.editItem = openUserForm;
    window.deleteItem = (id) => deleteUser(id, null, loadUsers);
    
    document.getElementById('add-user-btn').onclick = () => openUserForm();

    async function openUserForm(id = null) {
        const wrap = document.createElement('div');
        let user = {};
        
        // 🔥 Параллельно загружаем пользователя и команды (для выпадающего списка)
        const [userData, teams] = await Promise.all([
            id ? get(`/v1/users/${id}`).catch(e => { 
                alert(`Не удалось загрузить данные: ${e.message}`); 
                return null; 
            }) : Promise.resolve({}),
            get('/v1/teams/').catch(() => [])
        ]);
        
        if (id && !userData) return;
        user = userData;
        
        // Создаём опции для выбора команды
        const teamOptions = [
            { value: '', label: '— Не в команде —' },
            ...(teams || []).map(t => ({ value: t.id, label: t.name }))
        ];
        
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
            // 🔥 НОВОЕ ПОЛЕ: выбор команды
            { 
                key: 'team_id', 
                label: 'Команда', 
                type: 'select', 
                options: teamOptions,
                value: user.team_id || ''
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
                // Преобразуем team_id: пустая строка -> null, иначе число
                data.team_id = data.team_id ? parseInt(data.team_id) : null;
                
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
// ФУНКЦИЯ УДАЛЕНИЯ
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
        if (typeof reloadCallback === 'function') await reloadCallback();
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

// =====================================================================
// 🔥 УТИЛИТА: защита от XSS при отображении названий команд
// =====================================================================
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}