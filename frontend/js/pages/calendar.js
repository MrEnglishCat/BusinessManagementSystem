import { get, post } from '../api.js';
import { showModal, renderForm } from '../ui.js';

const MONTHS_RU = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const WEEKDAYS_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

let currentDate = new Date();
let eventsByDate = {};
let filter = 'all'; // 'all' | 'tasks' | 'meetings'

export async function renderCalendar(container) {
    container.innerHTML = `
        <h2>📅 Календарь</h2>
        <div class="calendar-toolbar">
            <button id="prev-month" class="btn-secondary">←</button>
            <h3 id="current-month" class="month-title"></h3>
            <button id="next-month" class="btn-secondary">→</button>
            <button id="today-btn" class="btn-primary">Сегодня</button>
            
            <div class="filter-group">
                <button data-filter="all" class="filter-btn active">Все</button>
                <button data-filter="tasks" class="filter-btn filter-tasks">Задачи</button>
                <button data-filter="meetings" class="filter-btn filter-meetings">Встречи</button>
            </div>
        </div>
        
        <div class="calendar-grid">
            <div class="calendar-header">
                ${WEEKDAYS_RU.map(d => `<div class="weekday">${d}</div>`).join('')}
            </div>
            <div id="calendar-body" class="calendar-body"></div>
        </div>
    `;

    document.getElementById('prev-month').onclick = () => changeMonth(-1);
    document.getElementById('next-month').onclick = () => changeMonth(1);
    document.getElementById('today-btn').onclick = () => {
        currentDate = new Date();
        loadAndRender();
    };
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.onclick = () => {
            filter = btn.dataset.filter;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderGrid();
        };
    });

    await loadAndRender();
}

async function loadAndRender() {
    const body = document.getElementById('calendar-body');
    body.innerHTML = '<div class="loading">Загрузка событий...</div>';
    
    try {
        const [tasks, meetings] = await Promise.all([
            get('/v1/tasks/').catch(() => []),
            get('/v1/meetings/').catch(() => [])
        ]);
        
        eventsByDate = groupEventsByDate(tasks || [], meetings || []);
        document.getElementById('current-month').textContent = 
            `${MONTHS_RU[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        
        renderGrid();
    } catch (e) {
        body.innerHTML = `<p class="error">Ошибка загрузки: ${e.message}</p>`;
    }
}

function groupEventsByDate(tasks, meetings) {
    const grouped = {};
    
    const addToDate = (dateStr, event, type) => {
        if (!dateStr) return;
        const key = dateStr.slice(0, 10); // YYYY-MM-DD
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push({ ...event, _type: type });
    };
    
    tasks.forEach(t => addToDate(t.deadline, t, 'task'));
    meetings.forEach(m => addToDate(m.start_time, m, 'meeting'));
    
    Object.values(grouped).forEach(arr => {
        arr.sort((a, b) => {
            if (a._type !== b._type) return a._type === 'meeting' ? -1 : 1;
            const timeA = (a.start_time || a.deadline || '').slice(11, 16);
            const timeB = (b.start_time || b.deadline || '').slice(11, 16);
            return timeA.localeCompare(timeB);
        });
    });
    
    return grouped;
}

function renderGrid() {
    const body = document.getElementById('calendar-body');
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    let startOffset = firstDay.getDay() - 1;
    if (startOffset < 0) startOffset = 6;
    
    const totalDays = lastDay.getDate();
    const today = new Date();
    const todayKey = formatDateKey(today);
    
    let html = '';
    let dayCounter = 1;
    const totalCells = Math.ceil((startOffset + totalDays) / 7) * 7;
    
    for (let i = 0; i < totalCells; i++) {
        if (i < startOffset || dayCounter > totalDays) {
            html += `<div class="calendar-cell other-month"></div>`;
            if (i >= startOffset) dayCounter++;
        } else {
            const dateKey = formatDateKey(new Date(year, month, dayCounter));
            const isToday = dateKey === todayKey;
            const events = getFilteredEvents(eventsByDate[dateKey] || []);
            
            html += `
                <div class="calendar-cell ${isToday ? 'today' : ''}" data-date="${dateKey}">
                    <div class="cell-date">${dayCounter}</div>
                    <div class="cell-events">
                        ${events.slice(0, 3).map(renderEventChip).join('')}
                        ${events.length > 3 ? `<div class="more-events">+${events.length - 3}</div>` : ''}
                    </div>
                </div>
            `;
            dayCounter++;
        }
    }
    
    body.innerHTML = html;
    
    // Обработчики клика по дням
    body.querySelectorAll('.calendar-cell[data-date]').forEach(cell => {
        cell.onclick = () => openDayDetails(cell.dataset.date);
    });
}

function getFilteredEvents(events) {
    if (filter === 'all') return events;
    return events.filter(e => e._type === filter.slice(0, -1)); // 'tasks' -> 'task'
}

function renderEventChip(event) {
    const time = (event.start_time || event.deadline || '').slice(11, 16);
    const title = event.title || event.name || 'Без названия';
    const statusClass = event.status ? `status-${event.status}` : '';
    
    return `
        <div class="event-chip event-${event._type} ${statusClass}" title="${title}">
            ${time ? `<span class="event-time">${time}</span>` : ''}
            <span class="event-title">${escapeHtml(title)}</span>
        </div>
    `;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function changeMonth(delta) {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + delta, 1);
    loadAndRender();
}

function formatDateKey(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

async function openDayDetails(dateKey) {
    const events = eventsByDate[dateKey] || [];
    const wrap = document.createElement('div');
    
    const [y, m, d] = dateKey.split('-');
    const dateObj = new Date(+y, +m - 1, +d);
    const dateStr = dateObj.toLocaleDateString('ru-RU', { 
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' 
    });
    
    // 🔥 Создаем футер ОТДЕЛЬНО от body
    const footerWrap = document.createElement('div');
    footerWrap.className = 'footer-actions';
    footerWrap.innerHTML = `
        <button class="btn-primary" id="quick-task">+ Задача</button>
        <button class="btn-secondary" id="quick-meeting">+ Встреча</button>
    `;
    
    if (events.length === 0) {
        wrap.innerHTML = `<p style="color: #64748b; text-align: center; padding: 1rem 0;">Нет событий на эту дату</p>`;
        showModal(`📅 ${dateStr}`, wrap, null, footerWrap);
        
        document.getElementById('quick-task').onclick = () => createQuick('task', dateKey);
        document.getElementById('quick-meeting').onclick = () => createQuick('meeting', dateKey);
        return;
    }
    
    const tasks = events.filter(e => e._type === 'task');
    const meetings = events.filter(e => e._type === 'meeting');
    
    wrap.innerHTML = `
        ${meetings.length ? `
            <h4>🤝 Встречи (${meetings.length})</h4>
            <div class="events-list">
                ${meetings.map(m => `
                    <div class="event-item meeting">
                        <div class="event-time-block">${(m.start_time || '').slice(11, 16) || '—'}</div>
                        <div class="event-info">
                            <strong>${escapeHtml(m.title)}</strong>
                            <div class="event-meta">
                                <span class="badge status-${m.status}">${m.status}</span>
                                ${m.location ? `<span>📍 ${escapeHtml(m.location)}</span>` : ''}
                            </div>
                            ${m.description ? `<div class="event-desc">${escapeHtml(m.description)}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
        
        ${tasks.length ? `
            <h4>✅ Задачи (${tasks.length})</h4>
            <div class="events-list">
                ${tasks.map(t => `
                    <div class="event-item task">
                        <div class="event-time-block">${(t.deadline || '').slice(11, 16) || '—'}</div>
                        <div class="event-info">
                            <strong>${escapeHtml(t.title)}</strong>
                            <div class="event-meta">
                                <span class="badge status-${t.status}">${t.status}</span>
                            </div>
                            ${t.description ? `<div class="event-desc">${escapeHtml(t.description)}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
    
    // 🔥 Передаем footerWrap как 4-й параметр
    showModal(`📅 ${dateStr}`, wrap, null, footerWrap);
    
    document.getElementById('quick-task').onclick = () => createQuick('task', dateKey);
    document.getElementById('quick-meeting').onclick = () => createQuick('meeting', dateKey);
}

async function createQuick(type, dateKey) {
    const wrap = document.createElement('div');
    const defaultTime = dateKey + 'T09:00';
    
    // 1. Загружаем команды для встреч
    let teamOptions = [];
    if (type === 'meeting') {
        try {
            const teams = await get('/v1/teams/');
            teamOptions = (teams || []).map(t => ({
                value: t.id,
                label: t.name
            }));
        } catch (e) {
            console.error('Не удалось загрузить команды:', e);
        }
    }
    
    // 2. Определяем поля формы
    const fields = type === 'task' ? [
        { key: 'title', label: 'Название', required: true },
        { key: 'description', label: 'Описание' },
        { key: 'deadline', label: 'Дедлайн', type: 'datetime-local', value: defaultTime, required: true }
    ] : [
        { key: 'title', label: 'Тема', required: true },
        { key: 'description', label: 'Описание' },
        { key: 'location', label: 'Место' },
        { key: 'start_time', label: 'Начало', type: 'datetime-local', value: defaultTime, required: true },
        { key: 'end_time', label: 'Конец', type: 'datetime-local', value: defaultTime, required: true },
        { 
            key: 'team_id', 
            label: 'Команда', 
            type: 'select', 
            required: true,
            options: teamOptions.length 
                ? teamOptions 
                : [{ value: '', label: '— Нет доступных команд —' }]
        }
    ];

    // 3. Рендерим форму
    renderForm(wrap, {
        fields,
        submitText: type === 'task' ? 'Добавить задачу' : 'Добавить встречу',
        onSubmit: async (data) => {
            console.log("🔥 1. onSubmit сработал! Сырые данные:", data);

            if (type === 'meeting') {
                // 1. Жесткая JS-валидация
                if (!data.title || !data.start_time || !data.end_time) {
                    alert("Заполните тему, начало и конец встречи");
                    return;
                }
                if (!data.team_id || data.team_id === "") {
                    alert("Выберите команду из выпадающего списка");
                    return;
                }

                // 2. Подготовка данных под требования вашего OpenAPI
                data.team_id = parseInt(data.team_id);
                data.status = "planned"; // 🔥 ОБЯЗАТЕЛЬНОЕ ПОЛЕ
                
                // Пытаемся получить ID, если функции нет - ставим заглушку 1 (замените на реальный импорт)
                const userId = typeof getCurrentUserId === 'function' ? getCurrentUserId() : 1;
                data.created_by = userId ? parseInt(userId) : 1; // 🔥 ОБЯЗАТЕЛЬНОЕ ПОЛЕ
                
                console.log("🔥 2. Данные после подготовки для бэка:", data);
            } else {
                if (!data.title || !data.deadline) {
                    alert("Заполните название и дедлайн");
                    return;
                }
            }

            // 3. БЕЗОПАСНАЯ блокировка кнопки (защита от null)
            const submitBtn = wrap.querySelector('button[type="submit"]') || wrap.querySelector('button');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Сохранение...';
            }

            try {
                console.log(`🌐 Отправка запроса на создание ${type}...`);
                if (type === 'task') {
                    await post('/v1/tasks/', data);
                } else {
                    await post('/v1/meetings/', data);
                }
                
                console.log("✅ Успешно создано!");
                
                // ШАГ 1: Закрываем текущую модалку с формой
                const formModal = wrap.closest('.modal-overlay');
                if (formModal) {
                    formModal.remove();
                }
                
                // ШАГ 2: Обновляем данные календаря в фоне (перезаписывает eventsByDate)
                await loadAndRender();
                
                // ШАГ 3: Закрываем ВСЕ оставшиеся модалки (включая старую модалку дня), 
                // чтобы избежать эффекта "матрешки" (наложения модалок друг на друга)
                document.querySelectorAll('.modal-overlay').forEach(m => m.remove());
                
                // ШАГ 4: Открываем модалку дня заново. 
                // Так как loadAndRender() уже отработал, openDayDetails возьмет свежие данные из eventsByDate
                await openDayDetails(dateKey);
                
            } catch (e) {
                console.error("❌ ОШИБКА ОТ СЕРВЕРА:", e);
                alert(`Ошибка создания:\n${e.message}`);
                
                // Возвращаем кнопку в исходное состояние при ошибке
                const submitBtn = wrap.querySelector('button[type="submit"]') || wrap.querySelector('button');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = type === 'task' ? 'Добавить задачу' : 'Добавить встречу';
                }
            }
        }
    });

    // 4. Добавляем предупреждение, если команд нет (вставляем ПЕРЕД формой)
    if (type === 'meeting' && teamOptions.length === 0) {
        const warning = document.createElement('div');
        warning.className = 'warning-box';
        warning.innerHTML = `⚠️ У вас нет команд. <a href="#/teams">Создайте команду</a> перед планированием.`;
        wrap.insertBefore(warning, wrap.firstChild);
    }

    // 5. Открываем модалку
    showModal(type === 'task' ? '➕ Новая задача' : '➕ Новая встреча', wrap);
}