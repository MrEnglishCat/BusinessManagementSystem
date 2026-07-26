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

    // Состояние текущей вкладки
    let currentTab = 'active';

    const loadMeetings = async () => {
        const list = document.getElementById('meetings-list');
        list.innerHTML = '<p>Загрузка...</p>';
        
        try {
            // 🔥 1. Выбираем эндпоинт в зависимости от активной вкладки
            const meetingsUrl = currentTab === 'canceled' 
                ? '/v1/meetings/canceled' 
                : '/v1/meetings/';

            // 🔥 2. Загружаем встречи с нужного эндпоинта + команды для маппинга имен
            const [meetings, teams] = await Promise.all([
                get(meetingsUrl),
                get('/v1/teams/').catch(() => [])
            ]);
            
            const teamMap = new Map();
            (teams || []).forEach(t => teamMap.set(t.id, t.name));
            
            list.innerHTML = '';
            
            // 🔥 3. Проверка на пустой список (бэк уже отфильтровал данные)
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
                            return teamName 
                                ? `<span class="team-badge">${escapeHtml(teamName)}</span>` 
                                : `<span class="no-team">ID ${r.team_id} ⚠️</span>`;
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
                        key: 'id',
                        label: 'Действия',
                        render: r => {
                            const rawStatus = r.status ? String(r.status).trim().toLowerCase() : '';
                            // Кнопка "Отменить" только для активных встреч
                            if (rawStatus === 'planned' || rawStatus === 'in_progress') {
                                return `<button class="btn-sm btn-danger cancel-btn" data-id="${r.id}">Отменить</button>`;
                            }
                            return '<span style="color: #94a3b8; font-size: 0.85rem;">—</span>';
                        }
                    }
                ],
                rows: meetings, // 🔥 4. Передаем массив напрямую, без клиентской фильтрации .filter()
                onEdit: (id) => openMeetingForm(id),
                onDelete: (id) => deleteMeeting(id, meetings, loadMeetings)
            });
            
            // Навешиваем обработчики на кнопки "Отменить"
            list.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.onclick = () => openCancelForm(btn.dataset.id);
            });
        } catch (e) { 
            list.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`; 
        }
    };

    // Обработчики переключения вкладок
    container.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTab = btn.dataset.tab;
            loadMeetings(); // Перезагружает данные с нового URL
        });
    });

    window.editItem = openMeetingForm;
    window.deleteItem = (id) => deleteMeeting(id, null, loadMeetings);
    document.getElementById('add-meeting-btn').onclick = () => openMeetingForm();

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
        
        const teamOptions = [
            { value: '', label: '— Без команды —' },
            ...teams.map(t => ({ value: t.id, label: t.name }))
        ];
        
        const modalInstance = showModal(id ? 'Редактировать встречу' : 'Новая встреча', wrap);
        
        renderForm(wrap, {
            fields: [
                { key: 'title', label: 'Тема', required: true, value: meeting.title || '' },
                { key: 'description', label: 'Описание', value: meeting.description || '' },
                { key: 'location', label: 'Место', value: meeting.location || '' },
                { key: 'start_time', label: 'Начало', type: 'datetime-local', required: true, value: meeting.start_time ? meeting.start_time.slice(0, 16) : '' },
                { key: 'end_time', label: 'Конец', type: 'datetime-local', required: true, value: meeting.end_time ? meeting.end_time.slice(0, 16) : '' },
                { 
                    key: 'status', 
                    label: 'Статус', 
                    type: 'select', 
                    options: [
                        { value: 'planned', label: 'Planned (Запланирована)' }, 
                        { value: 'in_progress', label: 'In Progress (Идет)' }, 
                        { value: 'completed', label: 'Completed (Завершена)' },
                        { value: 'canceled', label: 'Canceled (Отменена)' }
                    ], 
                    value: meeting.status || 'planned' 
                },
                { 
                    key: 'team_id', 
                    label: 'Команда', 
                    type: 'select', 
                    options: teamOptions,
                    value: meeting.team_id || ''
                }
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
                } catch (e) { 
                    alert(`Ошибка сохранения: ${e.message}`); 
                }
            }
        });
    }

    function openCancelForm(id) {
        const wrap = document.createElement('div');
        const modalInstance = showModal('Отмена встречи', wrap);
        
        renderForm(wrap, {
            fields: [
                { key: 'cancellation_reason', label: 'Причина отмены', required: true, type: 'textarea' }
            ],
            submitText: 'Подтвердить отмену',
            onSubmit: async (data) => {
                try {
                    await patch('/v1/meetings/cancel', {
                        id: parseInt(id),
                        cancellation_reason: data.cancellation_reason
                    });
                    
                    modalInstance.remove();
                    showNotification('Встреча успешно отменена', 'success');
                    await loadMeetings(); // Перезагрузит текущую вкладку (встреча исчезнет из "Актуальных")
                } catch (e) { 
                    alert(`Ошибка отмены: ${e.message}`); 
                }
            }
        });
    }

    await loadMeetings();
}

// =====================================================================
// УДАЛЕНИЕ ВСТРЕЧИ
// =====================================================================
async function deleteMeeting(id, meetingsList, reloadCallback) {
    const meeting = meetingsList?.find(m => String(m.id) === String(id));
    const meetingTitle = meeting ? meeting.title : `ID ${id}`;
    
    const confirmed = confirm(`Вы уверены, что хотите удалить встречу "${meetingTitle}"?\n\nЭто действие нельзя отменить.`);
    if (!confirmed) return;
    
    const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete-btn`);
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.textContent = '...';
    }
    
    try {
        await del(`/v1/meetings/${id}`);
        showNotification(`Встреча "${meetingTitle}" успешно удалена`, 'success');
        if (typeof reloadCallback === 'function') await reloadCallback();
    } catch (error) {
        console.error('Ошибка при удалении встречи:', error);
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = '🗑️';
        }
        
        const errMsg = error.message || 'Неизвестная ошибка';
        if (errMsg.includes('403') || errMsg.toLowerCase().includes('forbidden')) {
            alert(`❌ Недостаточно прав.`);
        } else if (errMsg.includes('404')) {
            alert(`❌ Встреча не найдена.`);
            if (typeof reloadCallback === 'function') await reloadCallback();
        } else {
            alert(`❌ Ошибка:\n\n${errMsg}`);
        }
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