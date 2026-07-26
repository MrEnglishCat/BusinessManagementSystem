import { get, post } from '../api.js';
import { renderTable } from '../ui.js';

export async function renderEvaluations(container) {
    container.innerHTML = `
        <h2>Оценки (Evaluations)</h2>
        
        <!-- 🔥 НАВИГАЦИЯ ПО ВКЛАДКАМ -->
        <div class="tabs-container">
            <button class="tab-btn active" data-tab="average">📊 Средние оценки</button>
            <button class="tab-btn" data-tab="all">📋 Все оценки</button>
        </div>
        
        <!-- 🔥 ФИЛЬТР ДЛЯ ВКЛАДКИ "СРЕДНИЕ ОЦЕНКИ" -->
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
        
        <!-- 🔥 ПОИСК ДЛЯ ВКЛАДКИ "ВСЕ ОЦЕНКИ" -->
        <div id="all-filters" class="filter-box" style="display: none;">
            <div class="filter-group-inline" style="flex: 1; max-width: 400px;">
                <label>🔍 Поиск по сотруднику:</label>
                <input type="text" id="user-search" placeholder="Введите username или имя...">
            </div>
            <button id="search-user-btn" class="btn-primary">Найти</button>
            <button id="clear-search-btn" class="btn-secondary" style="display: none;">Сбросить</button>
        </div>
        
        <div id="eval-list" class="mt-4"></div>
    `;

    // 🔥 СОСТОЯНИЕ ПРИЛОЖЕНИЯ
    let currentTab = 'average';
    let userMap = new Map();
    let taskMap = new Map();
    let allUsers = [];
    let allEvaluations = []; // Кэш всех оценок для быстрого поиска

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
        
        // Обновляем активную кнопку
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Показываем/скрываем фильтры
        document.getElementById('average-filters').style.display = tabName === 'average' ? 'flex' : 'none';
        document.getElementById('all-filters').style.display = tabName === 'all' ? 'flex' : 'none';
        
        // Очищаем результаты
        document.getElementById('eval-list').innerHTML = '';
        
        // Загружаем данные для вкладки
        if (tabName === 'average') {
            loadAverageEvaluations();
        } else {
            // Для вкладки "Все оценки" загружаем все данные при первом открытии
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
            const data = await post('/v1/evaluations/average', { 
                start_date: startDate, 
                end_date: endDate 
            });
            
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
                    { 
                        key: 'username', 
                        label: 'Сотрудник', 
                        render: r => `<strong>${escapeHtml(r.username)}</strong> <span style="color: #94a3b8; font-size: 0.85rem;">(ID: ${r.user_id})</span>` 
                    },
                    { 
                        key: 'avg_score', 
                        label: 'Средняя оценка', 
                        render: r => renderScoreBadge(parseFloat(r.avg_score))
                    },
                    { 
                        key: 'evaluations_count', 
                        label: 'Кол-во оценок', 
                        render: r => `<span style="font-weight: 600; color: #475569;">${r.evaluations_count}</span>` 
                    }
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

    // 🔥 5. ЗАГРУЗКА ВСЕХ ОЦЕНОК (с кэшированием)
    const loadAllEvaluations = async () => {
        const listContainer = document.getElementById('eval-list');
        listContainer.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem;">Загрузка всех оценок...</p>';

        try {
            // Загружаем все оценки (проверьте эндпоинт в вашем OpenAPI)
            allEvaluations = await get('/v1/evaluations/') || [];
            renderAllEvaluations(allEvaluations);
        } catch (e) {
            listContainer.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`;
        }
    };

    // 🔥 6. ОТРИСОВКА ВСЕХ ОЦЕНОК (с фильтрацией)
    const renderAllEvaluations = (evaluations) => {
        const listContainer = document.getElementById('eval-list');
        const searchQuery = document.getElementById('user-search').value.trim().toLowerCase();
        const clearBtn = document.getElementById('clear-search-btn');
        
        // Фильтрация по поисковому запросу
        let filteredEvaluations = evaluations;
        if (searchQuery) {
            filteredEvaluations = evaluations.filter(e => {
                const assesseeName = userMap.get(e.assessee_id) || '';
                const assessorName = userMap.get(e.assessor_id) || '';
                return assesseeName.toLowerCase().includes(searchQuery) || 
                       assessorName.toLowerCase().includes(searchQuery);
            });
        }
        
        // Показываем/скрываем кнопку "Сбросить"
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
                { 
                    key: 'created_at', 
                    label: 'Дата', 
                    render: r => r.created_at ? new Date(r.created_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'
                },
                { 
                    key: 'assessee_id', 
                    label: 'Кого оценили', 
                    render: r => {
                        const name = userMap.get(r.assessee_id);
                        return name ? `👤 ${escapeHtml(name)}` : `<span style="color:#94a3b8">ID: ${r.assessee_id}</span>`;
                    }
                },
                { 
                    key: 'assessor_id', 
                    label: 'Кто оценил', 
                    render: r => {
                        const name = userMap.get(r.assessor_id);
                        return name ? `👤 ${escapeHtml(name)}` : `<span style="color:#94a3b8">ID: ${r.assessor_id}</span>`;
                    }
                },
                { 
                    key: 'task_id', 
                    label: 'Задача', 
                    render: r => {
                        const title = taskMap.get(r.task_id);
                        return title ? escapeHtml(title) : `<span style="color:#94a3b8">ID: ${r.task_id}</span>`;
                    }
                },
                { 
                    key: 'score', 
                    label: 'Оценка', 
                    render: r => renderScoreBadge(r.score)
                },
                { 
                    key: 'comment', 
                    label: 'Комментарий', 
                    render: r => {
                        if (!r.comment) return '<span style="color: #cbd5e1;">—</span>';
                        const text = escapeHtml(r.comment);
                        return text.length > 40 ? `<span class="tooltip-text" title="${text}">${text.substring(0, 40)}...</span>` : text;
                    }
                }
            ],
            rows: filteredEvaluations
        });
    };

    // 🔥 7. ОБРАБОТЧИКИ СОБЫТИЙ
    
    // Переключение вкладок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });

    // Кнопка "Показать" для средних оценок
    document.getElementById('load-avg-btn').onclick = loadAverageEvaluations;

    // Поиск по пользователю (с debounce)
    let searchTimeout;
    document.getElementById('user-search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            renderAllEvaluations(allEvaluations);
        }, 300); // Debounce 300ms
    });

    // Кнопка "Найти"
    document.getElementById('search-user-btn').onclick = () => {
        renderAllEvaluations(allEvaluations);
    };

    // Кнопка "Сбросить"
    document.getElementById('clear-search-btn').onclick = () => {
        document.getElementById('user-search').value = '';
        renderAllEvaluations(allEvaluations);
    };

    // 🔥 8. ИНИЦИАЛИЗАЦИЯ
    setDefaultDates();
    await loadReferenceData();
    switchTab('average'); // Загружаем первую вкладку по умолчанию
}

// =====================================================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
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