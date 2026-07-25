import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderMeetings(container) {
    container.innerHTML = `
        <h2>Встречи (Meetings)</h2>
        <button id="add-meeting-btn" class="btn-primary">+ Запланировать встречу</button>
        <div id="meetings-list" class="mt-4"></div>
    `;

    const loadMeetings = async () => {
        const list = document.getElementById('meetings-list');
        list.innerHTML = '<p>Загрузка...</p>';
        try {
            const meetings = await get('/v1/meetings/');
            list.innerHTML = '';
            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'title', label: 'Тема' },
                    { key: 'start_time', label: 'Начало' },
                    { key: 'status', label: 'Статус', render: r => `<span class="badge status-${r.status}">${r.status}</span>` }
                ],
                rows: meetings || [],
                onEdit: (id) => openMeetingForm(id),
                onDelete: async (id) => {
                    if (confirm('Удалить встречу?')) {
                        await del(`/v1/meetings/${id}`);
                        loadMeetings();
                    }
                }
            });
            
            // Добавляем кнопку "Отменить" вручную в строки, т.к. это спец. действие
            document.querySelectorAll('#meetings-list tr').forEach(tr => {
                if (tr.dataset.id) {
                    const id = tr.dataset.id;
                    const status = tr.querySelector('.badge')?.textContent;
                    if (status === 'planned' || status === 'in_progress') {
                        const btn = document.createElement('button');
                        btn.className = 'btn-sm btn-danger';
                        btn.textContent = 'Отменить';
                        btn.onclick = () => openCancelForm(id);
                        tr.querySelector('.actions').appendChild(btn);
                    }
                }
            });
        } catch (e) { list.innerHTML = `<p class="error">${e.message}</p>`; }
    };

    window.editItem = openMeetingForm;
    window.deleteItem = async (id) => { await del(`/v1/meetings/${id}`); loadMeetings(); };
    document.getElementById('add-meeting-btn').onclick = () => openMeetingForm();

    async function openMeetingForm(id = null) {
        const wrap = document.createElement('div');
        const meeting = id ? (await get(`/v1/meetings/${id}`)) : {};
        
        renderForm(wrap, {
            fields: [
                { key: 'title', label: 'Тема', required: true, value: meeting.title },
                { key: 'description', label: 'Описание', value: meeting.description },
                { key: 'location', label: 'Место', value: meeting.location },
                { key: 'start_time', label: 'Начало', type: 'datetime-local', value: meeting.start_time ? meeting.start_time.slice(0, 16) : '' },
                { key: 'end_time', label: 'Конец', type: 'datetime-local', value: meeting.end_time ? meeting.end_time.slice(0, 16) : '' },
                { key: 'status', label: 'Статус', type: 'select', options: [
                    { value: 'planned', label: 'Planned' }, { value: 'in_progress', label: 'In Progress' }, { value: 'completed', label: 'Completed' }
                ], value: meeting.status || 'planned' },
                { key: 'team_id', label: 'ID Команды', type: 'number', value: meeting.team_id }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                try {
                    if (id) await patch(`/v1/meetings/${id}`, data);
                    else await post('/v1/meetings/', data);
                    modal.remove();
                    loadMeetings();
                } catch (e) { alert(e.message); }
            }
        });
        const modal = showModal(id ? 'Редактировать встречу' : 'Новая встреча', wrap);
    }

    function openCancelForm(id) {
        const wrap = document.createElement('div');
        renderForm(wrap, {
            fields: [
                { key: 'id', label: 'ID Встречи', type: 'number', value: id, readonly: true },
                { key: 'cancellation_reason', label: 'Причина отмены', required: true }
            ],
            submitText: 'Подтвердить отмену',
            onSubmit: async (data) => {
                try {
                    // Специфичный эндпоинт из OpenAPI
                    await patch('/v1/meetings/cancel', data);
                    alert('Встреча отменена');
                    modal.remove();
                    loadMeetings();
                } catch (e) { alert(e.message); }
            }
        });
        showModal('Отмена встречи', wrap);
    }

    await loadMeetings();
}