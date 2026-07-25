import { get, post, patch, del } from '../api.js';
import { renderTable, renderForm, showModal } from '../ui.js';

export async function renderTeams(container) {
    container.innerHTML = `
        <h2>Команды</h2>
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
            <button id="add-team-btn" class="btn-primary">+ Создать команду</button>
            <button id="join-team-btn" class="btn-secondary">Вступить по коду</button>
        </div>
        <div id="teams-list" class="mt-4"></div>
    `;

    const loadTeams = async () => {
        const list = document.getElementById('teams-list');
        list.innerHTML = '<p>Загрузка...</p>';
        try {
            const teams = await get('/v1/teams/');
            list.innerHTML = '';
            renderTable(list, {
                columns: [
                    { key: 'id', label: 'ID' },
                    { key: 'name', label: 'Название' },
                    { key: 'description', label: 'Описание' },
                    { key: 'invite_code', label: 'Код приглашения', render: r => `<code>${r.invite_code}</code>` }
                ],
                rows: teams || [],
                onEdit: (id) => openTeamForm(id),
                onDelete: async (id) => {
                    if (confirm('Удалить команду?')) {
                        await del(`/v1/teams/${id}`);
                        loadTeams();
                    }
                }
            });
        } catch (e) { list.innerHTML = `<p class="error">${e.message}</p>`; }
    };

    window.editItem = openTeamForm;
    window.deleteItem = async (id) => { await del(`/v1/teams/${id}`); loadTeams(); };
    document.getElementById('add-team-btn').onclick = () => openTeamForm();
    document.getElementById('join-team-btn').onclick = openJoinForm;

    async function openTeamForm(id = null) {
        const wrap = document.createElement('div');
        const team = id ? (await get(`/v1/teams/${id}`)) : {};
        
        renderForm(wrap, {
            fields: [
                { key: 'name', label: 'Название', required: true, value: team.name },
                { key: 'description', label: 'Описание', value: team.description },
                { key: 'invite_code', label: 'Код приглашения', required: true, value: team.invite_code }
            ],
            submitText: id ? 'Обновить' : 'Создать',
            onSubmit: async (data) => {
                try {
                    if (id) await patch(`/v1/teams/${id}`, data);
                    else await post('/v1/teams/', data);
                    modal.remove();
                    loadTeams();
                } catch (e) { alert(e.message); }
            }
        });
        const modal = showModal(id ? 'Редактировать команду' : 'Новая команда', wrap);
    }

    function openJoinForm() {
        const wrap = document.createElement('div');
        renderForm(wrap, {
            fields: [
                { key: 'username', label: 'Ваш Username', required: true },
                { key: 'invite_code', label: 'Код команды', required: true }
            ],
            submitText: 'Вступить',
            onSubmit: async (data) => {
                try {
                    // API требует POST /v1/teams/{invite_team_code}
                    await post(`/v1/teams/${data.invite_code}`, data);
                    alert('Вы успешно присоединились к команде!');
                    modal.remove();
                    loadTeams();
                } catch (e) { alert(e.message); }
            }
        });
        showModal('Вступление в команду', wrap);
    }

    await loadTeams();
}