import { get, post, del } from '../api.js';
import { renderTable } from '../ui.js';

export async function renderEvaluations(container) {
    container.innerHTML = `
        <h2>Оценки (Evaluations)</h2>
        
        <div class="tabs-container">
            <button class="tab-btn active" data-tab="average">📊 Средние оценки</button>
            <button class="tab-btn" data-tab="all">📋 Все оценки</button>
        </div>
        
        <div id="average-filters" class="filter-box">
            <div class="filter-group-inline">
                <label>С:</label>
                <input type="datetime-local" id="start_date">
            </div>
            <div class="filter-group-inline">
                <label>По:</label>
                <input type="datetime-local" id="end_date">
            </div>
            <button id="load-avg-btn" class="btn-primary">Показать</button>
        </div>
        
        <div id="all-filters" class="filter-box" style="display: none;">
            <div class="filter-group-inline" style="flex: 1; max-width: 500px;">
                <label>🔍 Поиск:</label>
                <input type="text" id="user-search" placeholder="По сотруднику, рецензенту или названию задачи...">
            </div>
            <button id="search-user-btn" class="btn-primary">Найти</button>
            <button id="clear-search-btn" class="btn-secondary" style="display: none;">Сбросить</button>
        </div>
        
        <div id="eval-list" class="mt-4"></div>
    `;

    // 🔥 СОСТОЯНИЕ ПРИЛОЖЕНИЯ (теперь доступно всем внутренним функциям)
    let currentTab = 'average';
    let userMap = new Map();
    let taskMap = new Map();
    let allUsers = [];
    let allEvaluations = [];

    // 🔥 1. ЗАГРУЗКА СПРАВОЧНЫХ ДАННЫХ
    const loadReferenceData = async () => {
        try {
            const [users, tasks] = await Promise.all([
                get('/v1/users/').catch(() => []),
                get('/v1/tasks/').catch(() => [])
            ]);
            users.forEach(u => {
                userMap.set(u.id, u.username);
                allUsers.push(u);
            });
            tasks.forEach(t => taskMap.set(t.id, t.title));
        } catch (e) {
            console.error('Не удалось загрузить справочные данные:', e);
        }
    };

    // 🔥 2. УСТАНОВКА ДАТ ПО УМОЛЧАНИЮ
    const setDefaultDates = () => {
        const today = new Date();
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        const formatDate = (d) => d.toISOString().slice(0, 16);
        
        document.getElementById('start_date').value = formatDate(firstDayOfMonth);
        document.getElementById('end_date').value = formatDate(today);
    };

    // 🔥 3. ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК
    const switchTab = (tabName) => {
        currentTab = tabName;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        document.getElementById('average-filters').style.display = tabName === 'average' ? 'flex' : 'none';
        document.getElementById('all-filters').style.display = tabName === 'all' ? 'flex' : 'none';
        document.getElementById('eval-list').innerHTML = '';
        
        if (tabName === 'average') {
            loadAverageEvaluations();
        } else {
            if (allEvaluations.length === 0) {
                loadAllEvaluations();
            } else {
                renderAllEvaluations(allEvaluations);
            }
        }
    };

    // 🔥 4. ЗАГРУЗКА СРЕДНИХ ОЦЕНОК
    const loadAverageEvaluations = async () => {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const loadBtn = document.getElementById('load-avg-btn');
        const listContainer = document.getElementById('eval-list');

        if (!startDate || !endDate) return alert('Пожалуйста, выберите обе даты');
        if (new Date(startDate) > new Date(endDate)) return alert('Дата начала не может быть позже даты окончания');

        loadBtn.disabled = true;
        loadBtn.textContent = 'Загрузка...';
        listContainer.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem;">Загрузка данных...</p>';

        try {
            const data = await post('/v1/evaluations/average', { start_date: startDate, end_date: endDate });
            listContainer.innerHTML = '';
            
            if (!data || data.length === 0) {
                listContainer.innerHTML = `
                    <div style="text-align: center; color: #64748b; padding: 3rem; background: #f8fafc; border-radius: 8px;">
                        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">📊 Оценок не найдено</p>
                        <p style="font-size: 0.9rem;">За выбранный период сотрудники не получали оценок.</p>
                    </div>
                `;
                return;
            }
            
            renderTable(listContainer, {
                columns: [
                    { key: 'username', label: 'Сотрудник', render: r => `<strong>${escapeHtml(r.username)}</strong> <span style="color: #94a3b8; font-size: 0.85rem;">(ID: ${r.user_id})</span>` },
                    { key: 'avg_score', label: 'Средняя оценка', render: r => renderScoreBadge(parseFloat(r.avg_score)) },
                    { key: 'evaluations_count', label: 'Кол-во оценок', render: r => `<span style="font-weight: 600; color: #475569;">${r.evaluations_count}</span>` }
                ],
                rows: data || []
            });
        } catch (e) {
            listContainer.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`;
        } finally {
            loadBtn.disabled = false;
            loadBtn.textContent = 'Показать';
        }
    };

    // 🔥 5. ЗАГРУЗКА ВСЕХ ОЦЕНОК
    const loadAllEvaluations = async () => {
        const listContainer = document.getElementById('eval-list');
        listContainer.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem;">Загрузка всех оценок...</p>';
        try {
            allEvaluations = await get('/v1/evaluations/') || [];
            renderAllEvaluations(allEvaluations);
        } catch (e) {
            listContainer.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`;
        }
    };

    // 🔥 6. ОТРИСОВКА ВСЕХ ОЦЕНОК (с фильтрацией и удалением)
    const renderAllEvaluations = (evaluations) => {
        const listContainer = document.getElementById('eval-list');
        const searchQuery = document.getElementById('user-search').value.trim().toLowerCase();
        const clearBtn = document.getElementById('clear-search-btn');
        
        let filteredEvaluations = evaluations;
        if (searchQuery) {
            filteredEvaluations = evaluations.filter(e => {
                const employeeName = userMap.get(e.employee_id) || '';
                const reviewerName = userMap.get(e.reviewer_id) || '';
                const taskTitle = taskMap.get(e.task_id) || '';
                
                return employeeName.toLowerCase().includes(searchQuery) || 
                       reviewerName.toLowerCase().includes(searchQuery) ||
                       taskTitle.toLowerCase().includes(searchQuery);
            });
        }
        
        clearBtn.style.display = searchQuery ? 'inline-block' : 'none';
        listContainer.innerHTML = '';
        
        if (filteredEvaluations.length === 0) {
            listContainer.innerHTML = `
                <div style="text-align: center; color: #64748b; padding: 3rem; background: #f8fafc; border-radius: 8px;">
                    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">📋 Оценок не найдено</p>
                    <p style="font-size: 0.9rem;">${searchQuery ? 'По вашему запросу ничего не найдено' : 'В системе пока нет оценок'}</p>
                </div>
            `;
            return;
        }
        
        renderTable(listContainer, {
            columns: [
                { key: 'created_at', label: 'Дата', render: r => r.created_at ? new Date(r.created_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—' },
                { key: 'employee_id', label: 'Кого оценили', render: r => { const name = userMap.get(r.employee_id); return name ? `👤 ${escapeHtml(name)}` : `<span style="color:#94a3b8">ID: ${r.employee_id}</span>`; } },
                { key: 'reviewer_id', label: 'Кто оценил', render: r => { const name = userMap.get(r.reviewer_id); return name ? `👤 ${escapeHtml(name)}` : `<span style="color:#94a3b8">ID: ${r.reviewer_id}</span>`; } },
                { key: 'task_id', label: 'Задача', render: r => { const title = taskMap.get(r.task_id); return title ? escapeHtml(title) : `<span style="color:#94a3b8">ID: ${r.task_id}</span>`; } },
                { key: 'score', label: 'Оценка', render: r => renderScoreBadge(r.score) },
                { key: 'comment', label: 'Комментарий', render: r => {
                    if (!r.comment) return '<span style="color: #cbd5e1;">—</span>';
                    const text = escapeHtml(r.comment);
                    return text.length > 40 ? `<span class="tooltip-text" title="${text}">${text.substring(0, 40)}...</span>` : text;
                }}
            ],
            rows: filteredEvaluations,
            // 🔥 Передаем обработчик удаления
            onDelete: (id) => deleteEvaluation(id, filteredEvaluations, () => {
                allEvaluations = []; // Сброс кэша
                loadAllEvaluations(); // Перезагрузка с сервера
            })
        });
    };

    // 🔥 7. ФУНКЦИЯ УДАЛЕНИЯ (ТЕПЕРЬ ВНУТРИ, ИМЕЕТ ДОСТУП К userMap и allEvaluations)
    const deleteEvaluation = async (id, evaluationsList, reloadCallback) => {
        const evaluation = evaluationsList?.find(e => String(e.id) === String(id));
        
        let description = `оценку ID ${id}`;
        if (evaluation) {
            const employeeName = userMap.get(evaluation.employee_id) || `ID: ${evaluation.employee_id}`;
            const reviewerName = userMap.get(evaluation.reviewer_id) || `ID: ${evaluation.reviewer_id}`;
            const score = evaluation.score || '?';
            description = `оценку сотрудника "${employeeName}" (балл: ${score}, от: ${reviewerName})`;
        }
        
        const confirmed = confirm(`⚠️ Удаление оценки\n\nВы уверены, что хотите удалить ${description}?\n\nЭто действие нельзя отменить.`);
        if (!confirmed) return;
        
        const deleteBtn = document.querySelector(`tr[data-id="${id}"] .delete-btn`);
        if (deleteBtn) {
            deleteBtn.disabled = true;
            deleteBtn.textContent = '...';
        }
        
        try {
            await del(`/v1/evaluations/${id}`);
            showNotification('Оценка успешно удалена', 'success');
            if (typeof reloadCallback === 'function') await reloadCallback();
        } catch (error) {
            console.error('Ошибка при удалении оценки:', error);
            if (deleteBtn) {
                deleteBtn.disabled = false;
                deleteBtn.textContent = '🗑️';
            }
            alert(`❌ Ошибка при удалении:\n\n${error.message || 'Неизвестная ошибка'}`);
        }
    };

    // 🔥 8. ФУНКЦИЯ УВЕДОМЛЕНИЙ (ТОЖЕ ВНУТРИ)
    const showNotification = (message, type = 'info') => {
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
    };

    // 🔥 9. ОБРАБОТЧИКИ СОБЫТИЙ
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });

    document.getElementById('load-avg-btn').onclick = loadAverageEvaluations;

    let searchTimeout;
    document.getElementById('user-search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => renderAllEvaluations(allEvaluations), 300);
    });

    document.getElementById('search-user-btn').onclick = () => renderAllEvaluations(allEvaluations);
    
    document.getElementById('clear-search-btn').onclick = () => {
        document.getElementById('user-search').value = '';
        renderAllEvaluations(allEvaluations);
    };

    // 🔥 10. ИНИЦИАЛИЗАЦИЯ
    setDefaultDates();
    await loadReferenceData();
    switchTab('average');
}

// =====================================================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (вне renderEvaluations, так как не зависят от состояния)
// =====================================================================

function renderScoreBadge(score) {
    if (!score && score !== 0) return '—';
    const numScore = parseFloat(score);
    let colorClass = 'score-neutral';
    if (numScore >= 4.0) colorClass = 'score-high';
    else if (numScore < 3.0) colorClass = 'score-low';
    return `<span class="badge score-badge ${colorClass}">${numScore.toFixed(1)} / 5.0</span>`;
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}