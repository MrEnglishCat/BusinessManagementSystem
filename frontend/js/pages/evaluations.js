import { get, post } from '../api.js';
import { renderTable } from '../ui.js';

export async function renderEvaluations(container) {
    container.innerHTML = `
        <h2>Оценки (Evaluations)</h2>
        <div class="filter-box">
            <input type="datetime-local" id="start_date">
            <input type="datetime-local" id="end_date">
            <button id="load-avg-btn" class="btn-primary">Показать среднее</button>
        </div>
        <div id="eval-list" class="mt-4"></div>
    `;

    document.getElementById('load-avg-btn').onclick = async () => {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        if (!startDate || !endDate) return alert('Выберите даты');

        const listContainer = document.getElementById('eval-list');
        listContainer.innerHTML = '<p>Загрузка...</p>';

        try {
            // Внимание: по вашему OpenAPI это POST запрос с JSON-телом!
            const data = await post('/v1/evaluations/average', { start_date: startDate, end_date: endDate });
            listContainer.innerHTML = '';
            
            // data здесь - это массив объектов { user_id, username, avg_score, ... }
            renderTable(listContainer, {
                columns: [
                    { key: 'user_id', label: 'User ID' },
                    { key: 'username', label: 'Username' },
                    { key: 'avg_score', label: 'Средняя оценка', render: r => `<b>${parseFloat(r.avg_score).toFixed(2)}</b>` },
                    { key: 'evaluations_count', label: 'Кол-во оценок' }
                ],
                rows: data || []
            });
        } catch (e) {
            listContainer.innerHTML = `<p class="error">${e.message}</p>`;
        }
    };
}