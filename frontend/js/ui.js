export function renderTable(container, { columns, rows, onEdit, onDelete }) {
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
        <thead><tr>${columns.map(c => `<th>${c.label}</th>`).join('')}<th>Действия</th></tr></thead>
        <tbody>
            ${rows.map(r => `
                <tr data-id="${r.id}">
                    ${columns.map(c => `<td>${c.render ? c.render(r) : (r[c.key] ?? '-')}</td>`).join('')}
                    <td class="actions">
                        ${onEdit ? `<button class="btn-sm" onclick="window.editItem('${r.id}')">Edit</button>` : ''}
                        ${onDelete ? `<button class="btn-sm btn-danger" onclick="window.deleteItem('${r.id}')">Del</button>` : ''}
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    container.appendChild(table);
}

export function renderForm(container, { fields, onSubmit, submitText = 'Сохранить' }) {
    const form = document.createElement('form');
    form.innerHTML = fields.map(f => `
        <div class="form-group">
            <label>${f.label}</label>
            ${f.type === 'select' 
                ? `<select name="${f.key}" ${f.required ? 'required' : ''}>
                     ${f.options.map(o => `<option value="${o.value}">${o.label}</option>`).join('')}
                   </select>`
                : `<input name="${f.key}" type="${f.type || 'text'}" value="${f.value || ''}" ${f.required ? 'required' : ''}>`
            }
        </div>
    `).join('') + `<button type="submit" class="btn-primary">${submitText}</button>`;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Преобразуем числа и null
        Object.keys(data).forEach(key => {
            if (data[key] === '') data[key] = null;
            else if (!isNaN(data[key]) && f?.type === 'number') data[key] = parseInt(data[key]);
        });
        
        onSubmit(data);
    });
    container.appendChild(form);
}

export function showModal(title, contentElement, onClose) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>${title}</h3>
            <div class="modal-body"></div>
            <button class="btn-secondary close-modal">Отмена</button>
        </div>
    `;
    modal.querySelector('.modal-body').appendChild(contentElement);
    modal.querySelector('.close-modal').onclick = () => { 
        modal.remove(); 
        onClose?.(); 
    };
    document.body.appendChild(modal);
    
    return modal;
}