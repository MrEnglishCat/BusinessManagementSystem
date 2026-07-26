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
                        render: r => `<button class="btn-sm btn-secondary manage-members-btn" data-team-id="${r.id}">👥 Управление</button>`
                    }
                ],
                rows: teams || [],
                onEdit: (id) => openTeamForm(id),
                onDelete: (id) => deleteTeam(id, teams, loadTeams)
            });
            
            list.querySelectorAll('.manage-members-btn').forEach(btn => {
                btn.onclick = () => manageTeamMembers(btn.dataset.teamId, loadTeams);
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
                    await post(`/v1/teams/invite_user`, { 
                        username: data.username,
                        invite_code:data.invite_code,

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
// 🔥 УПРАВЛЕНИЕ УЧАСТНИКАМИ КОМАНДЫ (С АВТООБНОВЛЕНИЕМ СПИСКОВ)
// =====================================================================
async function manageTeamMembers(teamId, reloadCallback) {
    const wrap = document.createElement('div');
    wrap.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem 0;">Загрузка данных...</p>';
    const modalInstance = showModal('Управление участниками команды', wrap);

    try {
        // 🔥 1. Используем let, чтобы можно было обновлять эти массивы
        let currentMembers = [];
        let allUsers = [];

        // 🔥 2. Функция для синхронизации данных с бэкендом
        const refreshData = async () => {
            const [members, users] = await Promise.all([
                get(`/v1/teams/${teamId}/members`).catch(() => []),
                get('/v1/users/without_teams').catch(() => [])
            ]);
            currentMembers = members;
            allUsers = users;
        };

        // Первичная загрузка
        await refreshData();

        let searchQuery = '';
        let currentModalTab = 'current';

        // =================================================================
        // Функция ДОБАВЛЕНИЯ
        // =================================================================
        const addMembers = async () => {
            const addBtn = document.getElementById('add-selected-btn');
            const checkboxes = wrap.querySelectorAll('.add-checkbox:checked');
            
            if (checkboxes.length === 0) {
                alert('Выберите хотя бы одного пользователя для добавления');
                return;
            }

            addBtn.disabled = true;
            addBtn.textContent = 'Добавление...';
            const usernamesToAdd = Array.from(checkboxes).map(cb => cb.value);

            try {
                const response = await post(`/v1/teams/${teamId}/members`, { 
                    usernames: usernamesToAdd 
                });
                
                showNotification(response?.message || `Добавлено участников: ${usernamesToAdd.length}`, 'success');
                
                // 🔥 ОБНОВЛЯЕМ данные с бэкенда, чтобы списки были актуальными
                await refreshData();
                
                searchQuery = '';
                currentModalTab = 'current'; // Переключаемся на вкладку "Текущие"
                renderContent();
                if (typeof reloadCallback === 'function') await reloadCallback();
                
            } catch (e) {
                alert(`Ошибка добавления: ${e.message}`);
            } finally {
                const newAddBtn = document.getElementById('add-selected-btn');
                if (newAddBtn) {
                    newAddBtn.disabled = false;
                    newAddBtn.textContent = 'Добавить выбранных';
                }
            }
        };

        // =================================================================
        // Функция МАССОВОГО УДАЛЕНИЯ
        // =================================================================
        const removeMembers = async () => {
            const removeBtn = document.getElementById('remove-selected-btn');
            const checkboxes = wrap.querySelectorAll('.remove-checkbox:checked');
            
            if (checkboxes.length === 0) {
                alert('Выберите хотя бы одного участника для удаления');
                return;
            }

            const usernamesToRemove = Array.from(checkboxes).map(cb => cb.value);
            const confirmed = confirm(`Вы уверены, что хотите удалить ${usernamesToRemove.length} участник(ов) из команды?`);
            if (!confirmed) return;

            removeBtn.disabled = true;
            removeBtn.textContent = 'Удаление...';

            try {
                const response = await del(`/v1/teams/${teamId}/members`, { 
                    usernames: usernamesToRemove
                });
                
                showNotification(response?.message || `Удалено участников: ${usernamesToRemove.length}`, 'success');
                
                // 🔥 ОБНОВЛЯЕМ данные с бэкенда
                await refreshData();
                
                renderContent();
                if (typeof reloadCallback === 'function') await reloadCallback();
            } catch (e) {
                alert(`Ошибка удаления: ${e.message}`);
            } finally {
                const newRemoveBtn = document.getElementById('remove-selected-btn');
                if (newRemoveBtn) {
                    newRemoveBtn.disabled = false;
                    newRemoveBtn.textContent = 'Удалить выбранных';
                }
            }
        };

        // =================================================================
        // Функция единичного УДАЛЕНИЯ
        // =================================================================
        const removeSingleMember = async (username) => {
            const confirmed = confirm(`Удалить пользователя "${username}" из команды?`);
            if (!confirmed) return;

            const removeBtn = wrap.querySelector(`.remove-single-btn[data-username="${CSS.escape(username)}"]`);
            if (removeBtn) {
                removeBtn.disabled = true;
                removeBtn.textContent = '...';
            }

            try {
                await del(`/v1/teams/${teamId}/members`, { 
                    usernames: [username]
                });
                
                showNotification(`Пользователь "${username}" удален из команды`, 'success');
                
                // 🔥 ОБНОВЛЯЕМ данные с бэкенда
                await refreshData();
                
                renderContent();
                if (typeof reloadCallback === 'function') await reloadCallback();
            } catch (e) {
                alert(`Ошибка удаления: ${e.message}`);
                if (removeBtn) {
                    removeBtn.disabled = false;
                    removeBtn.textContent = 'Удалить';
                }
            }
        };

        // =================================================================
        // Вспомогательные функции
        // =================================================================
        const filterUsers = (users, query) => {
            if (!query.trim()) return users;
            const lowerQuery = query.toLowerCase();
            return users.filter(u => 
                u.username.toLowerCase().includes(lowerQuery) ||
                (u.full_name && u.full_name.toLowerCase().includes(lowerQuery)) ||
                (u.email && u.email.toLowerCase().includes(lowerQuery))
            );
        };

        const highlightText = (text, query) => {
            if (!query.trim()) return escapeHtml(text);
            const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
            return escapeHtml(text).replace(regex, '<mark>$1</mark>');
        };

        const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

        // =================================================================
        // Функция отрисовки
        // =================================================================
        const renderContent = () => {
            // Фильтруем: показываем только тех, кого еще нет в этой команде
            const existingUsernames = new Set(currentMembers.map(m => m.username));
            const allAvailableUsers = (allUsers || []).filter(u => !existingUsernames.has(u.username));
            const filteredUsers = filterUsers(allAvailableUsers, searchQuery);

            let html = `
                <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0;">
                    <button class="modal-tab-btn" data-tab="current" style="flex: 1; padding: 0.6rem; border: none; background: transparent; border-bottom: 3px solid ${currentModalTab === 'current' ? '#2563eb' : 'transparent'}; color: ${currentModalTab === 'current' ? '#2563eb' : '#64748b'}; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                        Текущие (${currentMembers.length})
                    </button>
                    <button class="modal-tab-btn" data-tab="add" style="flex: 1; padding: 0.6rem; border: none; background: transparent; border-bottom: 3px solid ${currentModalTab === 'add' ? '#2563eb' : 'transparent'}; color: ${currentModalTab === 'add' ? '#2563eb' : '#64748b'}; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                        Добавить
                    </button>
                </div>
            `;

            if (currentModalTab === 'current') {
                html += `<h4 style="margin: 0 0 0.75rem 0; font-size: 0.95rem;">Список участников</h4>`;
                
                if (currentMembers.length === 0) {
                    html += `<p class="empty-state-small">Пока никого нет</p>`;
                } else {
                    html += `<div class="participants-list">`;
                    currentMembers.forEach(m => {
                        const displayName = m.full_name ? `${m.username} (${m.full_name})` : m.username;
                        html += `
                            <label class="checkbox-item remove-item">
                                <input type="checkbox" class="remove-checkbox" value="${escapeHtml(m.username)}">
                                <span>
                                    👤 ${escapeHtml(displayName)} 
                                    <small style="color: #64748b;">(${m.role || 'user'})</small>
                                </span>
                                <button class="btn-sm btn-danger remove-single-btn" data-username="${escapeHtml(m.username)}">Удалить</button>
                            </label>
                        `;
                    });
                    html += `</div>
                        <button id="remove-selected-btn" class="btn-danger btn-block" style="margin-top: 0.75rem;">
                            Удалить выбранных
                        </button>
                    `;
                }
            } else {
                html += `<h4 style="margin: 0 0 0.75rem 0; font-size: 0.95rem;">Добавить участников</h4>`;

                if (allAvailableUsers.length === 0) {
                    html += `<p class="empty-state-small">Все доступные пользователи уже в команде</p>`;
                } else {
                    html += `
                        <div class="search-container" style="margin-bottom: 0.75rem;">
                            <input 
                                type="text" 
                                id="user-search" 
                                class="search-input" 
                                placeholder="🔍 Поиск по имени, username или email..."
                                value="${escapeHtml(searchQuery)}"
                            >
                            <span class="search-count">${filteredUsers.length} из ${allAvailableUsers.length}</span>
                        </div>
                    `;

                    if (filteredUsers.length === 0) {
                        html += `<p class="empty-state-small">Ничего не найдено</p>`;
                    } else {
                        html += `<div class="available-users-list">`;
                        filteredUsers.forEach(u => {
                            const displayName = u.full_name ? `${u.username} (${u.full_name})` : u.username;
                            html += `
                                <label class="checkbox-item">
                                    <input type="checkbox" class="add-checkbox" value="${escapeHtml(u.username)}">
                                    <span>
                                        👤 ${highlightText(displayName, searchQuery)} 
                                        <small style="color: #64748b;">(${highlightText(u.email || 'Без email', searchQuery)})</small>
                                    </span>
                                </label>
                            `;
                        });
                        html += `</div>
                            <button id="add-selected-btn" class="btn-primary btn-block" style="margin-top: 1rem;">
                                Добавить выбранных
                            </button>
                        `;
                    }
                }
            }

            wrap.innerHTML = html;

            // Обработчики вкладок
            wrap.querySelectorAll('.modal-tab-btn').forEach(btn => {
                btn.onclick = () => {
                    currentModalTab = btn.dataset.tab;
                    renderContent();
                };
            });

            // Логика блокировки единичных кнопок удаления
            if (currentModalTab === 'current') {
                const updateSingleDeleteButtons = () => {
                    const checkedCount = wrap.querySelectorAll('.remove-checkbox:checked').length;
                    const isMultipleSelected = checkedCount > 0;

                    wrap.querySelectorAll('.remove-single-btn').forEach(btn => {
                        btn.disabled = isMultipleSelected;
                        btn.style.opacity = isMultipleSelected ? '0.5' : '1';
                        btn.style.cursor = isMultipleSelected ? 'not-allowed' : 'pointer';
                        btn.title = isMultipleSelected ? "Сначала снимите выделение" : "Удалить этого участника";
                    });
                };

                wrap.querySelectorAll('.remove-checkbox').forEach(checkbox => {
                    checkbox.addEventListener('change', updateSingleDeleteButtons);
                });
                updateSingleDeleteButtons();
            }

            // Обработчик поиска
            if (currentModalTab === 'add') {
                const searchInput = document.getElementById('user-search');
                if (searchInput) {
                    let debounceTimer;
                    searchInput.addEventListener('input', (e) => {
                        clearTimeout(debounceTimer);
                        debounceTimer = setTimeout(() => {
                            searchQuery = e.target.value;
                            renderContent();
                            const newSearchInput = document.getElementById('user-search');
                            if (newSearchInput) {
                                newSearchInput.focus();
                                newSearchInput.setSelectionRange(newSearchInput.value.length, newSearchInput.value.length);
                            }
                        }, 300);
                    });
                }
            }

            // Обработчики кнопок действий
            const addBtn = document.getElementById('add-selected-btn');
            if (addBtn) addBtn.onclick = addMembers;

            const removeBtn = document.getElementById('remove-selected-btn');
            if (removeBtn) removeBtn.onclick = removeMembers;

            wrap.querySelectorAll('.remove-single-btn').forEach(btn => {
                btn.onclick = async (e) => {
                    e.preventDefault();
                    await removeSingleMember(btn.dataset.username);
                };
            });
        };

        // Первичная отрисовка
        renderContent();

    } catch (e) {
        wrap.innerHTML = `<p style="text-align: center; color: #dc2626; padding: 2rem 0;">Не удалось загрузить данные:<br>${e.message}</p>`;
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