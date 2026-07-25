import { post } from '../api.js';

export async function renderDashboard(container) {
    container.innerHTML = `
        <h2>Панель управления (Demo)</h2>
        <p>Используйте эти инструменты для быстрого наполнения или очистки базы данных во время демонстрации.</p>
        
        <div style="display: flex; gap: 2rem; margin-top: 2rem;">
            <div class="card" style="flex: 1; padding: 2rem; background: white; border-radius: 8px; text-align: center;">
                <h3>🎲 Сгенерировать данные</h3>
                <p>Создает тестовых пользователей, команды, задачи и встречи.</p>
                <button id="generate-btn" class="btn-primary" style="margin-top: 1rem;">Запустить генерацию</button>
            </div>
            
            <div class="card" style="flex: 1; padding: 2rem; background: white; border-radius: 8px; text-align: center;">
                <h3>🗑️ Очистить таблицы</h3>
                <p>Безвозвратно удаляет все данные из системы.</p>
                <button id="clear-btn" class="btn-danger" style="margin-top: 1rem;">Очистить всё</button>
            </div>
        </div>
        <div id="demo-status" class="mt-4"></div>
    `;

    const statusDiv = document.getElementById('demo-status');

    document.getElementById('generate-btn').onclick = async () => {
        statusDiv.innerHTML = '<p>Генерация... ⏳</p>';
        try {
            await post('/v1/data_generate', {});
            statusDiv.innerHTML = '<p class="success" style="color: green;">✅ Данные успешно сгенерированы!</p>';
        } catch (e) {
            statusDiv.innerHTML = `<p class="error">❌ Ошибка: ${e.message}</p>`;
        }
    };

    document.getElementById('clear-btn').onclick = async () => {
        if (!confirm('ВНИМАНИЕ: Это удалит ВСЕ данные. Продолжить?')) return;
        statusDiv.innerHTML = '<p>Очистка... ⏳</p>';
        try {
            await post('/v1/clear_tables', {});
            statusDiv.innerHTML = '<p class="success" style="color: green;">✅ Таблицы очищены!</p>';
        } catch (e) {
            statusDiv.innerHTML = `<p class="error">❌ Ошибка: ${e.message}</p>`;
        }
    };
}