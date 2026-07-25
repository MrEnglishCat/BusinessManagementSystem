import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderTasks(container) {
    container.innerHTML = `
        <h2>Задачи (Tasks)</h2>
        <button id="add-task-btn" class="btn-primary">+ Новая задача</button>
        <div id="tasks-list" class="mt-4"></div>
    `;

    const loadTasks = async () => {
        const listContainer = document.getElementById('tasks-list');
        listContainer.innerHTML = '<p>Загрузка...</p>';
        try {
            const tasks = await get('/v1/tasks/');
            listContainer.innerHTML = '';
            
            renderTable(listContainer, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'title', label: 'Название' },
                    { key: 'status', label: 'Статус', render: r => `<span class="badge status-${r.status}">${r.status}</span>` },
                    { key: 'deadline', label: 'Дедлайн' }
                ],
                rows: tasks || [],
                onEdit: (id) => openTaskForm(id),
                onDelete: async (id) => {
                    if (confirm('Удалить задачу?')) {
                        await del(`/v1/tasks/${id}`);
                        loadTasks();
                    }
                }
            });
        } catch (e) {
            listContainer.innerHTML = `<p class="error">${e.message}</p>`;
        }
    };

    // Глобальные функции для onclick в таблице
    window.editItem = openTaskForm;
    window.deleteItem = async (id) => { /* вызовется из таблицы */ };

    document.getElementById('add-task-btn').onclick = () => openTaskForm();

    async function openTaskForm(id = null) {
        const wrap = document.createElement('div');
        const task = id ? (await get(`/v1/tasks/${id}`)) : {};
        
        renderForm(wrap, {
            fields: [
                { key: 'title', label: 'Название', required: true, value: task.title },
                { key: 'description', label: 'Описание', value: task.description },
                { key: 'status', label: 'Статус', type: 'select', options: [
                    { value: 'open', label: 'Open' }, { value: 'in_progres', label: 'In Progress' }, { value: 'completed', label: 'Completed' }, { value: 'created', label: 'Created' }
                ], value: task.status || 'open' },
                { key: 'deadline', label: 'Дедлайн', type: 'datetime-local', value: task.deadline ? task.deadline.slice(0, 16) : '' },
                { key: 'assignee_id', label: 'ID Исполнителя', type: 'number', value: task.assignee_id },
                { key: 'team_id', label: 'ID Команды', type: 'number', value: task.team_id }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                try {
                    if (id) await patch(`/v1/tasks/${id}`, data);
                    else await post('/v1/tasks/', data);
                    modal.remove();
                    loadTasks();
                } catch (e) {
                    alert(e.message);
                }
            }
        });
        const modal = showModal(id ? 'Редактировать задачу' : 'Новая задача', wrap);
    }

    await loadTasks();
}