import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

import { getCurrentUserId } from '../auth.js';
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
                    { 
                        key: 'status', 
                        label: 'Статус', 
                        render: r => {
                            const rawStatus = r.status ? String(r.status).trim().toLowerCase() : '';
                            if (!rawStatus || rawStatus === 'undefined' || rawStatus === 'null') {
                                return `<span class="badge status-unknown">Не указан</span>`;
                            }
                            const statusText = rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1).replace('_', ' ');
                            return `<span class="badge status-${rawStatus}">${statusText}</span>`;
                        } 
                    },
                    { 
                        key: 'deadline', 
                        label: 'Дедлайн', 
                        render: r => r.deadline 
                            ? new Date(r.deadline).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) 
                            : '—' 
                    },
                    { 
                        key: 'assignee_id', 
                        label: 'Исполнитель', 
                        render: r => r.assignee_id ? `ID: ${r.assignee_id}` : '—' 
                    }
                ],
                rows: tasks || [],
                onView: (id) => viewTask(id),       // 🔥 НОВОЕ: действие просмотра
                onEdit: (id) => openTaskForm(id),
                onDelete: (id) => deleteTask(id, tasks, loadTasks)
            });
        } catch (e) {
            listContainer.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`;
        }
    };

    window.editItem = openTaskForm;
    window.deleteItem = (id) => deleteTask(id, null, loadTasks);
    document.getElementById('add-task-btn').onclick = () => openTaskForm();

    async function openTaskForm(id = null) {
        const wrap = document.createElement('div');
        let task = {};
        
        if (id) {
            try {
                task = await get(`/v1/tasks/${id}`);
            } catch (e) {
                alert(`Не удалось загрузить данные задачи: ${e.message}`);
                return;
            }
        }
        
        const modalInstance = showModal(id ? 'Редактировать задачу' : 'Новая задача', wrap);
        
        renderForm(wrap, {
            fields: [
                { key: 'title', label: 'Название', required: true, value: task.title || '' },
                { key: 'description', label: 'Описание', value: task.description || '' },
                { key: 'status', label: 'Статус', type: 'select', options: [
                    { value: 'created', label: 'Created (Создана)' },
                    { value: 'open', label: 'Open (Открыта)' }, 
                    { value: 'in_progres', label: 'In Progress (В работе)' }, 
                    { value: 'completed', label: 'Completed (Завершена)' }
                ], value: task.status || 'created' },
                { key: 'deadline', label: 'Дедлайн', type: 'datetime-local', value: task.deadline ? task.deadline.slice(0, 16) : '' },
                { key: 'assignee_id', label: 'ID Исполнителя', type: 'number', value: task.assignee_id || '' },
                { key: 'team_id', label: 'ID Команды', type: 'number', value: task.team_id || '' }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                if (data.assignee_id === '') data.assignee_id = null;
                else data.assignee_id = parseInt(data.assignee_id);
                
                if (data.team_id === '') data.team_id = null;
                else data.team_id = parseInt(data.team_id);

                try {
                    if (id) await patch(`/v1/tasks/${id}`, data);
                    else await post('/v1/tasks/', data);
                    
                    modalInstance.remove();
                    await loadTasks();
                    showNotification(id ? 'Задача обновлена' : 'Задача успешно создана', 'success');
                } catch (e) {
                    alert(`Ошибка сохранения: ${e.message}`);
                }
            }
        });
    }

    await loadTasks();
}
// =====================================================================
// 🔥 ПРОСМОТР ЗАДАЧИ, КОММЕНТАРИИ И ДОБАВЛЕНИЕ НОВЫХ
// =====================================================================
async function viewTask(id) {
    const wrap = document.createElement('div');
    wrap.className = 'task-view-container';
    wrap.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem 0;">Загрузка данных...</p>';
    
    const modalInstance = showModal('Просмотр задачи', wrap);

    try {
        // 🔥 1. ПОЛУЧАЕМ ID ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ЗДЕСЬ
        const currentUserId = getCurrentUserId();

        const [task, allComments] = await Promise.all([
            get(`/v1/tasks/${id}`),
            get('/v1/task_comments/').catch(() => [])
        ]);

        const comments = (allComments || []).filter(c => String(c.task_id) === String(id));
        comments.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

        const rawStatus = task.status ? String(task.status).trim().toLowerCase() : '';
        const statusText = rawStatus ? rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1).replace('_', ' ') : 'Не указан';

        wrap.innerHTML = `
            <div class="task-view-header">
                <h3 style="margin: 0;">${escapeHtml(task.title)}</h3>
                <span class="badge status-${rawStatus || 'unknown'}">${statusText}</span>
            </div>
            
            <div class="task-details-grid">
                <div class="detail-item">
                    <span class="detail-label">Описание:</span>
                    <span class="detail-value">${escapeHtml(task.description) || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Дедлайн:</span>
                    <span class="detail-value">${task.deadline ? new Date(task.deadline).toLocaleString('ru-RU') : '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Исполнитель:</span>
                    <span class="detail-value">${task.assignee_id ? `ID: ${task.assignee_id}` : 'Не назначен'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Команда:</span>
                    <span class="detail-value">${task.team_id ? `ID: ${task.team_id}` : '—'}</span>
                </div>
            </div>

            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 1.5rem 0 1rem 0;">
            
            <h4 style="margin: 0 0 0.75rem 0; color: #334155; font-size: 1rem;">💬 Комментарии (${comments.length})</h4>
            
            <div class="comments-scroll-area" id="comments-list-${id}">
                ${comments.length === 0 
                    ? `<p class="no-comments">Комментариев пока нет. Будьте первым!</p>` 
                    // 🔥 2. ПЕРЕДАЕМ currentUserId в функцию рендеринга
                    : comments.map(c => renderCommentHTML(c, currentUserId)).join('')
                }
            </div>

            <form class="comment-input-area" id="comment-form-${id}">
                <textarea name="content" placeholder="Напишите комментарий..." required rows="2"></textarea>
                <button type="submit" class="btn-primary" style="align-self: flex-end;">Отправить</button>
            </form>
        `;

        const form = document.getElementById(`comment-form-${id}`);
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const textarea = form.querySelector('textarea');
            const content = textarea.value.trim();
            if (!content) return;

            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = '...';

            try {
                // 🔥 3. ТЕПЕРЬ currentUserId ОПРЕДЕЛЕН И ДОСТУПЕН ЗДЕСЬ
                if (!currentUserId) {
                    throw new Error('Не удалось определить пользователя. Перезайдите в систему.');
                }

                await post('/v1/task_comments/', {
                    task_id: parseInt(id),
                    user_id: parseInt(currentUserId), // ✅ Ошибка больше не возникнет
                    content: content
                });

                const newComment = {
                    user_id: currentUserId,
                    content: content,
                    created_at: new Date().toISOString()
                };

                const listContainer = document.getElementById(`comments-list-${id}`);
                const noCommentsMsg = listContainer.querySelector('.no-comments');
                if (noCommentsMsg) noCommentsMsg.remove();

                // 🔥 4. ПЕРЕДАЕМ currentUserId при рендеринге нового комментария
                const newCommentHTML = renderCommentHTML(newComment, currentUserId);
                listContainer.insertAdjacentHTML('afterbegin', newCommentHTML);

                textarea.value = '';
                const header = wrap.querySelector('h4');
                const currentCount = parseInt(header.textContent.match(/\d+/)[0]);
                header.textContent = `💬 Комментарии (${currentCount + 1})`;

            } catch (error) {
                console.error('Ошибка отправки комментария:', error);
                alert(`Не удалось отправить комментарий:\n${error.message}`);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Отправить';
                textarea.focus();
            }
        });

    } catch (e) {
        wrap.innerHTML = `<p style="text-align: center; color: #dc2626; padding: 2rem 0;">Не удалось загрузить данные:<br>${e.message}</p>`;
    }
}
function renderCommentHTML(c, currentUserId) {
    const dateStr = c.created_at 
        ? new Date(c.created_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) 
        : 'Только что';
    
    // 🔥 Проверяем, принадлежит ли комментарий текущему пользователю
    const isMine = String(c.user_id) === String(currentUserId);
    const mineClass = isMine ? 'comment-card-mine' : '';
    
    // Для своих сообщений пишем "Вы", для чужих - ID
    const userName = isMine ? 'Вы' : (c.user_id ? `User ID: ${c.user_id}` : 'Неизвестный');

    return `
        <div class="comment-card ${mineClass}">
            <div class="comment-header">
                <strong>${escapeHtml(userName)}</strong>
                <span class="comment-date">${dateStr}</span>
            </div>
            <div class="comment-body">${escapeHtml(c.content)}</div>
        </div>
    `;
}

// =====================================================================
// УДАЛЕНИЕ ЗАДАЧИ (без изменений, уже было надежным)
// =====================================================================
async function deleteTask(id, tasksList, reloadCallback) {
    const task = tasksList?.find(t => String(t.id) === String(id));
    const taskTitle = task ? task.title : `ID ${id}`;
    
    const confirmed = confirm(`Вы уверены, что хотите удалить задачу "${taskTitle}"?\n\nЭто действие нельзя отменить.`);
    if (!confirmed) return;
    
    const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete-btn`);
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.textContent = '...';
    }
    
    try {
        await del(`/v1/tasks/${id}`);
        showNotification(`Задача "${taskTitle}" успешно удалена`, 'success');
        if (typeof reloadCallback === 'function') await reloadCallback();
    } catch (error) {
        console.error('Ошибка при удалении задачи:', error);
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = '🗑️';
        }
        
        const errMsg = error.message || 'Неизвестная ошибка';
        if (errMsg.includes('403') || errMsg.toLowerCase().includes('forbidden')) {
            alert(`❌ Недостаточно прав для удаления этой задачи.`);
        } else if (errMsg.includes('404') || errMsg.toLowerCase().includes('not found')) {
            alert(`❌ Задача не найдена (возможно, уже удалена).`);
            if (typeof reloadCallback === 'function') await reloadCallback();
        } else if (errMsg.includes('409') || errMsg.toLowerCase().includes('conflict')) {
            alert(`❌ Невозможно удалить задачу "${taskTitle}".\n\nК ней привязаны комментарии или оценки.`);
        } else if (errMsg.includes('Failed to fetch') || errMsg.includes('NetworkError')) {
            alert(`❌ Ошибка сети. Проверьте подключение.`);
        } else {
            alert(`❌ Ошибка при удалении:\n\n${errMsg}`);
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