import { post } from '../api.js';

export async function renderDashboard(container) {
    container.innerHTML = `
        <h2>Панель управления (Demo)</h2>
        <p style="color: #64748b; margin-bottom: 2rem;">
            Настройте количество генерируемых сущностей и запустите генерацию.
        </p>
        
        <div class="card" style="padding: 2rem; background: white; border-radius: 8px; margin-bottom: 2rem;">
            <h3 style="margin-top: 0;">⚙️ Настройки генерации</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
                <div class="form-group">
                    <label>👥 Пользователи</label>
                    <input type="number" id="users_count" value="100" min="0" max="10000" class="form-input">
                </div>
                <div class="form-group">
                    <label>🏢 Команды</label>
                    <input type="number" id="teams_count" value="20" min="0" max="1000" class="form-input">
                </div>
                <div class="form-group">
                    <label>📋 Задачи</label>
                    <input type="number" id="tasks_count" value="200" min="0" max="10000" class="form-input">
                </div>
                <div class="form-group">
                    <label>📅 Встречи</label>
                    <input type="number" id="meetings_count" value="50" min="0" max="1000" class="form-input">
                </div>
                <div class="form-group">
                    <label>⭐ Оценки</label>
                    <input type="number" id="evaluations_count" value="300" min="0" max="10000" class="form-input">
                </div>
                <div class="form-group">
                    <label>💬 Мин. комментариев/задачу</label>
                    <input type="number" id="comments_min" value="2" min="0" max="50" class="form-input">
                </div>
                <div class="form-group">
                    <label>💬 Макс. комментариев/задачу</label>
                    <input type="number" id="comments_max" value="5" min="0" max="50" class="form-input">
                </div>
            </div>
            
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                <button id="generate-btn" class="btn-primary">🎲 Запустить генерацию</button>
                <button id="reset-defaults-btn" class="btn-secondary">🔄 Сбросить к дефолтам</button>
            </div>
        </div>
        
        <div class="card" style="padding: 2rem; background: white; border-radius: 8px; text-align: center;">
            <h3 style="margin-top: 0; color: #dc2626;">🗑️ Очистить таблицы</h3>
            <p style="color: #475569; font-size: 0.9rem;">Безвозвратно удаляет все данные (кроме администратора).</p>
            <button id="clear-btn" class="btn-danger" style="margin-top: 1rem;">Очистить всё</button>
        </div>
        
        <div id="demo-status" class="mt-4" style="margin-top: 2rem; text-align: center;"></div>
    `;

    // 🔥 1. Используем container.querySelector для 100% надежности
    const statusDiv = container.querySelector('#demo-status');
    const generateBtn = container.querySelector('#generate-btn');
    const clearBtn = container.querySelector('#clear-btn');
    const resetBtn = container.querySelector('#reset-defaults-btn');

    const defaults = {
        users_count: 100, teams_count: 20, tasks_count: 200,
        meetings_count: 50, evaluations_count: 300, comments_min: 2, comments_max: 5
    };

    resetBtn.onclick = () => {
        container.querySelector('#users_count').value = defaults.users_count;
        container.querySelector('#teams_count').value = defaults.teams_count;
        container.querySelector('#tasks_count').value = defaults.tasks_count;
        container.querySelector('#meetings_count').value = defaults.meetings_count;
        container.querySelector('#evaluations_count').value = defaults.evaluations_count;
        container.querySelector('#comments_min').value = defaults.comments_min;
        container.querySelector('#comments_max').value = defaults.comments_max;
        if (statusDiv) statusDiv.innerHTML = '<p style="color: #2563eb;">✅ Значения сброшены к дефолтным</p>';
    };

    generateBtn.onclick = async () => {
        const payload = {
            users_count: parseInt(container.querySelector('#users_count').value),
            teams_count: parseInt(container.querySelector('#teams_count').value),
            tasks_count: parseInt(container.querySelector('#tasks_count').value),
            meetings_count: parseInt(container.querySelector('#meetings_count').value),
            evaluations_count: parseInt(container.querySelector('#evaluations_count').value),
            comments_per_task_min: parseInt(container.querySelector('#comments_min').value),
            comments_per_task_max: parseInt(container.querySelector('#comments_max').value),
        };

        if (payload.comments_per_task_min > payload.comments_per_task_max) {
            if (statusDiv) statusDiv.innerHTML = '<p style="color: #dc2626;">❌ Мин. комментариев не может быть больше макс.</p>';
            return;
        }

        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.textContent = 'Генерация... ⏳';
        }
        if (statusDiv) statusDiv.innerHTML = '<p style="color: #2563eb; font-weight: 500;">⏳ Идет генерация данных...</p>';

        try {
            const response = await post('/v1/mock_manager/data_generate', payload);
            
            // 🔥 2. Абсолютно безопасное извлечение сообщения (защита от null)
            const message = (response && response.message) ? response.message : 'Данные успешно сгенерированы!';
            if (statusDiv) statusDiv.innerHTML = `<p style="color: #16a34a; font-weight: 600; font-size: 1.1rem;">✅ ${message}</p>`;
            
        } catch (e) {
            console.error('Ошибка генерации:', e);
            // 🔥 3. Максимальная защита: проверяем, что e существует и имеет свойство message
            const errorMsg = (e && e.message) ? e.message : (typeof e === 'string' ? e : 'Неизвестная ошибка');
            if (statusDiv) statusDiv.innerHTML = `<p style="color: #dc2626; font-weight: 500;">❌ Ошибка: ${errorMsg}</p>`;
            
        } finally {
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.textContent = '🎲 Запустить генерацию';
            }
        }
    };

    clearBtn.onclick = async () => {
        if (!confirm('⚠️ ВНИМАНИЕ: Это удалит ВСЕ данные (кроме администратора). Продолжить?')) return;
        
        if (clearBtn) {
            clearBtn.disabled = true;
            clearBtn.textContent = 'Очистка... ⏳';
        }
        if (statusDiv) statusDiv.innerHTML = '<p style="color: #dc2626; font-weight: 500;">⏳ Идет очистка таблиц...</p>';

        try {
            await post('/v1/mock_manager/clear_tables', {});
            if (statusDiv) statusDiv.innerHTML = '<p style="color: #16a34a; font-weight: 600; font-size: 1.1rem;">✅ Таблицы успешно очищены!</p>';
            
        } catch (e) {
            console.error('Ошибка очистки:', e);
            // 🔥 4. Та же максимальная защита для кнопки очистки
            const errorMsg = (e && e.message) ? e.message : (typeof e === 'string' ? e : 'Неизвестная ошибка');
            if (statusDiv) statusDiv.innerHTML = `<p style="color: #dc2626; font-weight: 500;">❌ Ошибка: ${errorMsg}</p>`;
            
        } finally {
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.textContent = 'Очистить всё';
            }
        }
    };
}