export function renderTable(container, { columns, rows, onEdit, onDelete, onView }) {
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
        <thead><tr>${columns.map(c => `<th>${c.label}</th>`).join('')}<th>Действия</th></tr></thead>
        <tbody>
            ${rows.map(r => `
                <tr data-id="${r.id}">
                    ${columns.map(c => `<td>${c.render ? c.render(r) : (r[c.key] ?? '-')}</td>`).join('')}
                    <td class="actions">
                        ${onView ? `<button class="btn-sm btn-info view-btn" title="Просмотр">👁️</button>` : ''}
                        ${onEdit ? `<button class="btn-sm btn-secondary edit-btn" title="Редактировать">✏️</button>` : ''}
                        ${onDelete ? `<button class="btn-sm btn-danger delete-btn" title="Удалить">🗑️</button>` : ''}
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    // Навешиваем обработчики событий
    table.querySelectorAll('tbody tr').forEach(tr => {
        const id = tr.dataset.id;
        tr.querySelector('.view-btn')?.addEventListener('click', () => onView(id));
        tr.querySelector('.edit-btn')?.addEventListener('click', () => onEdit(id));
        tr.querySelector('.delete-btn')?.addEventListener('click', () => onDelete(id));
    });

    container.appendChild(table);
}

export function renderForm(container, { fields, onSubmit, submitText = 'Сохранить' }) {
    const form = document.createElement('form');
    form.className = 'dynamic-form';
    
    // 🔥 Отключаем молчаливую блокировку отправки браузером
    form.setAttribute('novalidate', 'true'); 
    
    form.innerHTML = fields.map(f => {
        const currentValue = f.value !== undefined && f.value !== null ? f.value : '';
        
        let inputHtml;
        if (f.type === 'select') {
            inputHtml = `
                <select name="${f.key}" ${f.required ? 'required' : ''}>
                    ${f.options.map(o => `
                        <option value="${o.value}" ${String(o.value) === String(currentValue) ? 'selected' : ''}>
                            ${o.label}
                        </option>
                    `).join('')}
                </select>
            `;
        } else if (f.type === 'textarea') {
            inputHtml = `<textarea name="${f.key}" ${f.required ? 'required' : ''}>${currentValue}</textarea>`;
        } else if (f.type === 'checkbox') {
            inputHtml = `<input name="${f.key}" type="checkbox" ${currentValue ? 'checked' : ''}>`;
        } else {
            inputHtml = `<input name="${f.key}" type="${f.type || 'text'}" value="${currentValue}" ${f.required ? 'required' : ''} ${f.readonly ? 'readonly' : ''}>`;
        }

        return `
            <div class="form-group">
                <label>${f.label}</label>
                ${inputHtml}
            </div>
        `;
    }).join('') + `<button type="submit" class="btn-primary btn-submit">${submitText}</button>`;

    // ✅ ИСПРАВЛЕНО: убрана ошибочная ссылка на переменную 'f'
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Собираем данные как строки, а конкретная страница (calendar.js) 
        // сама решит, где сделать parseInt или добавить скрытые поля
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        console.log("📦 Данные из формы перед отправкой в onSubmit:", data);
        
        try {
            await onSubmit(data);
        } catch (err) {
            console.error('❌ Ошибка внутри onSubmit:', err);
        }
    });
    
    container.appendChild(form);
    return form;
}

export function showModal(title, contentElement, onClose, footerElement = null) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>${title}</h3>
            <div class="modal-body"></div>
        </div>
    `;
    
    modal.querySelector('.modal-body').appendChild(contentElement);
    
    // Создаём футер
    const footer = document.createElement('div');
    footer.className = 'modal-footer';
    
    if (footerElement) {
        // 🔥 Порядок: сначала пользовательские кнопки, потом "Закрыть"
        footer.appendChild(footerElement);
    }
    
    // Кнопка закрытия всегда внизу
    const closeBtn = document.createElement('button');
    closeBtn.className = 'btn-secondary close-modal';
    closeBtn.textContent = 'Закрыть';
    footer.appendChild(closeBtn);
    
    modal.querySelector('.modal').appendChild(footer);
    
    closeBtn.onclick = (e) => { 
        e.preventDefault();
        modal.remove(); 
        if (typeof onClose === 'function') onClose();
    };
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
            if (typeof onClose === 'function') onClose();
        }
    });
    
    document.body.appendChild(modal);
    return modal;
}