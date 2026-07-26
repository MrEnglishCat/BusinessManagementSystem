import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderMeetings(container) {
    container.innerHTML = `
        <h2>Встречи (Meetings)</h2>
        
        <div class="tabs-container">
            <button class="tab-btn active" data-tab="active">Актуальные</button>
            <button class="tab-btn" data-tab="canceled">Отмененные</button>
        </div>
        
        <button id="add-meeting-btn" class="btn-primary" style="margin-top: 1rem;">+ Запланировать встречу</button>
        <div id="meetings-list" class="mt-4"></div>
    `;

    let currentTab = 'active';

    const loadMeetings = async () => {
        const list = document.getElementById('meetings-list');
        list.innerHTML = '<p>Загрузка...</p>';
        
        try {
            const meetingsUrl = currentTab === 'canceled' ? '/v1/meetings/canceled' : '/v1/meetings/';

            const [meetings, teams] = await Promise.all([
                get(meetingsUrl),
                get('/v1/teams/').catch(() => [])
            ]);
            
            const teamMap = new Map();
            (teams || []).forEach(t => teamMap.set(t.id, t.name));
            
            list.innerHTML = '';
            
            if (!meetings || meetings.length === 0) {
                list.innerHTML = `<p style="text-align: center; color: #64748b; padding: 2rem;">
                    ${currentTab === 'active' ? 'Нет актуальных встреч' : 'Нет отмененных встреч'}
                </p>`;
                return;
            }

            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'title', label: 'Тема' },
                    { 
                        key: 'start_time', 
                        label: 'Начало', 
                        render: r => r.start_time 
                            ? new Date(r.start_time).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) 
                            : '—' 
                    },
                    { 
                        key: 'team_id', 
                        label: 'Команда', 
                        render: r => {
                            if (!r.team_id) return '<span class="no-team">— без команды —</span>';
                            const teamName = teamMap.get(r.team_id);
                            return teamName ? `<span class="team-badge">${escapeHtml(teamName)}</span>` : `<span class="no-team">ID ${r.team_id} ⚠️</span>`;
                        }
                    },
                    { 
                        key: 'status', 
                        label: 'Статус', 
                        render: r => {
                            const rawStatus = r.status ? String(r.status).trim().toLowerCase() : '';
                            if (!rawStatus) return '<span class="badge status-unknown">Не указан</span>';
                            const statusText = rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1).replace('_', ' ');
                            return `<span class="badge status-${rawStatus}">${statusText}</span>`;
                        } 
                    },
                    {
                        key: 'participants',
                        label: 'Участники',
                        render: r => {
                            const count = r.participants ? r.participants.length : 0;
                            return `<button class="btn-sm btn-secondary manage-participants-btn" data-id="${r.id}">👥 ${count}</button>`;
                        }
                    }
                    // 🔥 Мы убрали отсюда кастомную колонку 'Действия', чтобы ui.js создал её стандартно
                ],
                rows: meetings,
                onView: null,
                onEdit: (id) => openMeetingForm(id),
                onDelete: (id) => deleteMeeting(id, meetings, loadMeetings)
            });
            
            // 🔥 ДОБАВЛЯЕМ КНОПКУ "ОТМЕНИТЬ" В СУЩЕСТВУЮЩУЮ ЯЧЕЙКУ .actions
            list.querySelectorAll('tbody tr').forEach(tr => {
                const id = tr.dataset.id;
                const meeting = meetings.find(m => String(m.id) === String(id));
                if (!meeting) return;

                const rawStatus = meeting.status ? String(meeting.status).trim().toLowerCase() : '';
                // Показываем кнопку только для запланированных или идущих встреч
                if (rawStatus === 'planned' || rawStatus === 'in_progress') {
                    const actionsCell = tr.querySelector('.actions');
                    if (actionsCell) {
                        const cancelBtn = document.createElement('button');
                        cancelBtn.className = 'btn-sm btn-warning cancel-btn';
                        cancelBtn.textContent = 'Отменить';
                        cancelBtn.dataset.id = id;
                        cancelBtn.title = 'Отменить встречу';
                        actionsCell.appendChild(cancelBtn); // Добавляем в конец ячейки (после ✏️ и 🗑️)
                    }
                }
            });

            // Обработчик для кнопки "Отменить"
            list.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.onclick = () => openCancelForm(btn.dataset.id);
            });
            
            // Обработчики для кнопок "Участники" (они уже были, оставляем)
            list.querySelectorAll('.manage-participants-btn').forEach(btn => {
                btn.onclick = () => manageParticipants(btn.dataset.id);
            });
            
            // Обработчики для кнопок "Отменить"
            list.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.onclick = () => openCancelForm(btn.dataset.id);
            });

            // 🔥 Обработчики для кнопок "Участники"
            list.querySelectorAll('.manage-participants-btn').forEach(btn => {
                btn.onclick = () => manageParticipants(btn.dataset.id);
            });

        } catch (e) { 
            list.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`; 
        }
    };

    container.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTab = btn.dataset.tab;
            loadMeetings();
        });
    });

    window.editItem = openMeetingForm;
    window.deleteItem = (id) => deleteMeeting(id, null, loadMeetings);
    document.getElementById('add-meeting-btn').onclick = () => openMeetingForm();

    // ... (функции openMeetingForm и openCancelForm остаются без изменений, как в вашем коде) ...
    async function openMeetingForm(id = null) {
        const wrap = document.createElement('div');
        let meeting = {};
        let teams = [];
        try {
            const results = await Promise.all([
                id ? get(`/v1/meetings/${id}`) : Promise.resolve({}),
                get('/v1/teams/').catch(() => [])
            ]);
            meeting = results[0];
            teams = results[1] || [];
        } catch (e) {
            alert(`Не удалось загрузить данные: ${e.message}`);
            return;
        }
        const teamOptions = [{ value: '', label: '— Без команды —' }, ...teams.map(t => ({ value: t.id, label: t.name }))];
        const modalInstance = showModal(id ? 'Редактировать встречу' : 'Новая встреча', wrap);
        renderForm(wrap, {
            fields: [
                { key: 'title', label: 'Тема', required: true, value: meeting.title || '' },
                { key: 'description', label: 'Описание', value: meeting.description || '' },
                { key: 'location', label: 'Место', value: meeting.location || '' },
                { key: 'start_time', label: 'Начало', type: 'datetime-local', required: true, value: meeting.start_time ? meeting.start_time.slice(0, 16) : '' },
                { key: 'end_time', label: 'Конец', type: 'datetime-local', required: true, value: meeting.end_time ? meeting.end_time.slice(0, 16) : '' },
                { key: 'status', label: 'Статус', type: 'select', options: [{ value: 'planned', label: 'Planned' }, { value: 'in_progress', label: 'In Progress' }, { value: 'completed', label: 'Completed' }, { value: 'canceled', label: 'Canceled' }], value: meeting.status || 'planned' },
                { key: 'team_id', label: 'Команда', type: 'select', options: teamOptions, value: meeting.team_id || '' }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                data.team_id = data.team_id ? parseInt(data.team_id) : null;
                try {
                    if (id) await patch(`/v1/meetings/${id}`, data);
                    else await post('/v1/meetings/', data);
                    modalInstance.remove();
                    await loadMeetings();
                    showNotification(id ? 'Встреча обновлена' : 'Встреча успешно создана', 'success');
                } catch (e) { alert(`Ошибка сохранения: ${e.message}`); }
            }
        });
    }

    function openCancelForm(id) {
        const wrap = document.createElement('div');
        const modalInstance = showModal('Отмена встречи', wrap);
        renderForm(wrap, {
            fields: [{ key: 'cancellation_reason', label: 'Причина отмены', required: true, type: 'textarea' }],
            submitText: 'Подтвердить отмену',
            onSubmit: async (data) => {
                try {
                    await patch('/v1/meetings/cancel', { id: parseInt(id), cancellation_reason: data.cancellation_reason });
                    modalInstance.remove();
                    showNotification('Встреча успешно отменена', 'success');
                    await loadMeetings();
                } catch (e) { alert(`Ошибка отмены: ${e.message}`); }
            }
        });
    }

    await loadMeetings();
}

// =====================================================================
// 🔥 ИСПРАВЛЕННАЯ ФУНКЦИЯ: УПРАВЛЕНИЕ УЧАСТНИКАМИ (С ОБНОВЛЕНИЕМ МОДАЛКИ)
// =====================================================================
async function manageParticipants(meetingId) {
    const wrap = document.createElement('div');
    wrap.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem 0;">Загрузка данных...</p>';
    const modalInstance = showModal('Управление участниками', wrap);

    try {
        const [meeting, allUsers] = await Promise.all([
            get(`/v1/meetings/${meetingId}`),
            get('/v1/users/').catch(() => [])
        ]);

        let currentParticipants = meeting.participants || [];
        let searchQuery = '';

        // 🔥 1. Функция ДОБАВЛЕНИЯ нескольких участников
        const addParticipants = async () => {
            const addBtn = document.getElementById('add-selected-btn');
            const checkboxes = wrap.querySelectorAll('.user-checkbox:checked');
            
            if (checkboxes.length === 0) {
                alert('Выберите хотя бы одного пользователя');
                return;
            }

            addBtn.disabled = true;
            addBtn.textContent = 'Добавление...';

            const usersToAdd = Array.from(checkboxes).map(cb => ({ username: cb.value }));

            try {
                await post(`/v1/meetings/${meetingId}/add_participants`, {
                    participants: usersToAdd
                });
                
                showNotification(`Успешно добавлено участников: ${usersToAdd.length}`, 'success');
                
                // 🔥 ОБНОВЛЯЕМ локальное состояние
                currentParticipants = [...currentParticipants, ...usersToAdd];
                searchQuery = '';
                
                // 🔥 ПЕРЕРИСОВЫВАЕМ модалку с новыми данными
                renderContent();
                
                // Обновляем счетчик в главной таблице
                await loadMeetings();
                
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

        // 🔥 2. Функция УДАЛЕНИЯ участника
        const removeParticipant = async (username) => {
            // 🔥 СРАЗУ обновляем локальное состояние
            currentParticipants = currentParticipants.filter(p => p.username !== username);
            
            await saveParticipants();
        };

        // 🔥 3. Функция сохранения (для удаления)
        const saveParticipants = async () => {
            try {
                await patch(`/v1/meetings/${meetingId}`, {
                    participants: currentParticipants
                });
                showNotification('Участник успешно удален', 'success');
                
                // 🔥 ПЕРЕРИСОВЫВАЕМ модалку с обновленными данными
                renderContent();
                
                await loadMeetings();
            } catch (e) {
                alert(`Ошибка сохранения: ${e.message}`);
            }
        };

        // 🔥 4. Функция фильтрации пользователей
        const filterUsers = (users, query) => {
            if (!query.trim()) return users;
            const lowerQuery = query.toLowerCase();
            return users.filter(u => 
                u.username.toLowerCase().includes(lowerQuery) ||
                (u.full_name && u.full_name.toLowerCase().includes(lowerQuery))
            );
        };

        // 🔥 5. Функция подсветки совпадений
        const highlightText = (text, query) => {
            if (!query.trim()) return escapeHtml(text);
            const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
            return escapeHtml(text).replace(regex, '<mark>$1</mark>');
        };

        const escapeRegExp = (string) => {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        };

        // 🔥 6. Функция отрисовки содержимого модалки
        const renderContent = () => {
            const existingUsernames = new Set(currentParticipants.map(p => p.username));
            const allAvailableUsers = (allUsers || []).filter(u => !existingUsernames.has(u.username));
            const filteredUsers = filterUsers(allAvailableUsers, searchQuery);

            let html = `
                <h4 style="margin: 0 0 0.75rem 0; font-size: 0.95rem;">Текущие участники (${currentParticipants.length})</h4>
                <div class="participants-list">
                    ${currentParticipants.length === 0 
                        ? '<p class="empty-state-small">Пока никого нет</p>' 
                        : currentParticipants.map(p => `
                            <div class="participant-item">
                                <span>👤 ${escapeHtml(p.username)}</span>
                                <button class="btn-sm btn-danger remove-participant-btn" data-username="${escapeHtml(p.username)}">Удалить</button>
                            </div>
                          `).join('')
                    }
                </div>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;">
                <h4 style="margin: 0 0 0.75rem 0; font-size: 0.95rem;">Добавить участников</h4>
            `;

            if (allAvailableUsers.length === 0) {
                html += `<p class="empty-state-small">Все пользователи системы уже добавлены</p>`;
            } else {
                html += `
                    <div class="search-container">
                        <input 
                            type="text" 
                            id="user-search" 
                            class="search-input" 
                            placeholder="🔍 Поиск по имени или username..."
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
                        html += `
                            <label class="checkbox-item">
                                <input type="checkbox" class="user-checkbox" value="${escapeHtml(u.username)}">
                                <span>
                                    ${highlightText(u.username, searchQuery)} 
                                    <small style="color: #64748b;">(${highlightText(u.full_name || 'Без имени', searchQuery)})</small>
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

            wrap.innerHTML = html;

            // 🔥 Обработчик поиска
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

            // 🔥 Обработчики кнопок удаления
            wrap.querySelectorAll('.remove-participant-btn').forEach(btn => {
                btn.onclick = async () => await removeParticipant(btn.dataset.username);
            });

            // 🔥 Обработчик кнопки добавления
            const addBtn = document.getElementById('add-selected-btn');
            if (addBtn) {
                addBtn.onclick = addParticipants;
            }
        };

        // Первичная отрисовка
        renderContent();

    } catch (e) {
        wrap.innerHTML = `<p style="text-align: center; color: #dc2626; padding: 2rem 0;">Не удалось загрузить данные:<br>${e.message}</p>`;
    }
}

// =====================================================================
// УДАЛЕНИЕ ВСТРЕЧИ (без изменений)
// =====================================================================
async function deleteMeeting(id, meetingsList, reloadCallback) {
    const meeting = meetingsList?.find(m => String(m.id) === String(id));
    const meetingTitle = meeting ? meeting.title : `ID ${id}`;
    const confirmed = confirm(`Вы уверены, что хотите удалить встречу "${meetingTitle}"?\n\nЭто действие нельзя отменить.`);
    if (!confirmed) return;
    const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete-btn`);
    if (deleteBtn) { deleteBtn.disabled = true; deleteBtn.textContent = '...'; }
    try {
        await del(`/v1/meetings/${id}`);
        showNotification(`Встреча "${meetingTitle}" успешно удалена`, 'success');
        if (typeof reloadCallback === 'function') await reloadCallback();
    } catch (error) {
        if (deleteBtn) { deleteBtn.disabled = false; deleteBtn.textContent = '🗑️'; }
        alert(`❌ Ошибка:\n\n${error.message || 'Неизвестная ошибка'}`);
    }
}

// =====================================================================
// УВЕДОМЛЕНИЯ И УТИЛИТЫ
// =====================================================================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? '#16a34a' : type === 'error' ? '#dc2626' : '#2563eb';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; border-radius: 8px;
        background: ${bgColor}; color: white; font-weight: 500;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.2); z-index: 10000; animation: slideIn 0.3s ease-out;
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