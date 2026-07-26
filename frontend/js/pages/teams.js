import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderTeams(container) {
    container.innerHTML = `
        <h2>Команды</h2>
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
            <button id="add-team-btn" class="btn-primary">+ Создать команду</button>
            <button id="join-team-btn" class="btn-secondary">Вступить по коду</button>
        </div>
        <div id="teams-list" class="mt-4"></div>
    `;

    const loadTeams = async () => {
        const list = document.getElementById('teams-list');
        list.innerHTML = '<p>Загрузка...</p>';
        try {
            const teams = await get('/v1/teams/');
            list.innerHTML = '';
            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'name', label: 'Название' },
                    { key: 'description', label: 'Описание' },
                    { 
                        key: 'invite_code', 
                        label: 'Код приглашения', 
                        render: r => `<code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace;">${r.invite_code}</code>` 
                    },
                    {
                        key: 'id',
                        label: 'Участники',
                        render: r => `<button class="btn-sm btn-secondary view-members" data-team-id="${r.id}">👥 Показать</button>`
                    }
                ],
                rows: teams || [],
                onEdit: (id) => openTeamForm(id),
                onDelete: (id) => deleteTeam(id, teams, loadTeams)
            });
            
            list.querySelectorAll('.view-members').forEach(btn => {
                btn.onclick = () => showTeamMembers(btn.dataset.teamId);
            });
        } catch (e) { 
            list.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`; 
        }
    };

    window.editItem = openTeamForm;
    window.deleteItem = (id) => deleteTeam(id, null, loadTeams);
    
    document.getElementById('add-team-btn').onclick = () => openTeamForm();
    document.getElementById('join-team-btn').onclick = openJoinForm;

    async function openTeamForm(id = null) {
        const wrap = document.createElement('div');
        let team = {};
        
        if (id) {
            try {
                team = await get(`/v1/teams/${id}`);
            } catch (e) {
                alert(`Не удалось загрузить данные: ${e.message}`);
                return;
            }
        }
        
        // 🔥 1. Сначала создаём модалку и получаем на неё ПРЯМУЮ ссылку
        const modalInstance = showModal(id ? 'Редактировать команду' : 'Новая команда', wrap);
        
        renderForm(wrap, {
            fields: [
                { key: 'name', label: 'Название', required: true, value: team.name || '' },
                { key: 'description', label: 'Описание', value: team.description || '' },
                { key: 'invite_code', label: 'Код приглашения', required: true, value: team.invite_code || '' }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                try {
                    if (id) await patch(`/v1/teams/${id}`, data);
                    else await post('/v1/teams/', data);
                    
                    // 🔥 2. Закрываем модалку по прямой ссылке (гарантированно работает)
                    modalInstance.remove();
                    
                    await loadTeams();
                    showNotification(id ? 'Команда обновлена' : 'Команда успешно создана', 'success');
                } catch (e) { 
                    alert(`Ошибка сохранения: ${e.message}`); 
                }
            }
        });
    }

    function openJoinForm() {
        const wrap = document.createElement('div');
        
        // 🔥 1. Сначала создаём модалку и получаем на неё ПРЯМУЮ ссылку
        const modalInstance = showModal('Вступление в команду', wrap);
        
        renderForm(wrap, {
            fields: [
                { key: 'username', label: 'Ваш Username', required: true },
                { key: 'invite_code', label: 'Код команды', required: true }
            ],
            submitText: 'Вступить',
            onSubmit: async (data) => {
                try {
                    await post(`/v1/teams/${encodeURIComponent(data.invite_code)}`, { 
                        username: data.username 
                    });
                    
                    // 🔥 2. Закрываем модалку по прямой ссылке
                    modalInstance.remove();
                    
                    showNotification(`Вы успешно присоединились к команде!`, 'success');
                    await loadTeams();
                } catch (e) { 
                    alert(`Ошибка присоединения:\n${e.message}`); 
                }
            }
        });
    }

    await loadTeams();
}


// =====================================================================
// 🔥 ПРОСМОТР УЧАСТНИКОВ КОМАНДЫ (в виде таблицы)
// =====================================================================
async function showTeamMembers(teamId) {
    const wrap = document.createElement('div');
    wrap.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem 0;">Загрузка участников...</p>';
    
    const modalInstance = showModal(`Участники команды`, wrap);
    
    try {
        const members = await get(`/v1/teams/${teamId}/members`);
        
        // 1. Нейтральное сообщение, если участников нет (без слова "Ошибка")
        if (!members || members.length === 0) {
            wrap.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem 0;">В этой команде пока нет участников</p>';
            return;
        }
        
        // 2. Отображение в виде красивой таблицы
        const tableHtml = `
            <table class="members-table">
                <thead>
                    <tr>
                        <th>Пользователь</th>
                        <th>Email</th>
                        <th>Роль</th>
                    </tr>
                </thead>
                <tbody>
                    ${members.map(m => `
                        <tr>
                            <td><strong>${escapeHtml(m.username || m.full_name || 'Без имени')}</strong></td>
                            <td>${escapeHtml(m.email || '—')}</td>
                            <td><span class="badge status-${m.role || 'user'}">${m.role || 'user'}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        wrap.innerHTML = tableHtml;
        
    } catch (e) {
        // 3. Мягкое сообщение при реальной ошибке сети/сервера
        wrap.innerHTML = `<p style="text-align: center; color: #dc2626; padding: 2rem 0;">Не удалось загрузить список участников:<br>${e.message}</p>`;
    }
}



// =====================================================================
// УДАЛЕНИЕ КОМАНДЫ С ОБРАБОТКОЙ ОШИБОК
// =====================================================================
async function deleteTeam(id, teamsList, reloadCallback) {
    const team = teamsList?.find(t => String(t.id) === String(id));
    const teamName = team ? team.name : `ID ${id}`;
    
    const confirmed = confirm(`Вы уверены, что хотите удалить команду "${teamName}"?\n\nВсе пользователи этой команды потеряют к ней доступ.`);
    if (!confirmed) return;
    
    const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete`);
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.textContent = '...';
    }
    
    try {
        await del(`/v1/teams/${id}`);
        showNotification(`Команда "${teamName}" успешно удалена`, 'success');
        if (typeof reloadCallback === 'function') await reloadCallback();
    } catch (error) {
        console.error('Ошибка при удалении:', error);
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = 'Del';
        }
        
        const errMsg = error.message || 'Неизвестная ошибка';
        if (errMsg.includes('403') || errMsg.toLowerCase().includes('forbidden')) {
            alert(`❌ Недостаточно прав для удаления этой команды.`);
        } else if (errMsg.includes('404') || errMsg.toLowerCase().includes('not found')) {
            alert(`❌ Команда не найдена (возможно, уже удалена).`);
            if (typeof reloadCallback === 'function') await reloadCallback();
        } else if (errMsg.includes('409') || errMsg.toLowerCase().includes('conflict')) {
            alert(`❌ Невозможно удалить команду "${teamName}".\n\nК ней привязаны пользователи, задачи или встречи.`);
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

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}