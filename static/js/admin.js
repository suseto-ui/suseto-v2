const box = document.querySelector('#admin-users'),
      msg = document.querySelector('#admin-msg'),
      audit = document.querySelector('#audit-log'),
      esc = x => String(x ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;');

// Spuštění administrační logiky pouze při přítomnosti příslušných prvků
if (box || msg || audit) {
    async function loadUsers() {
        let r = await fetch('/api/v1/admin/users'), d = await r.json();
        if (!r.ok) { box.innerHTML = '<div class="result-chip text-danger">' + esc(d.error) + '</div>'; return; }
        
        box.innerHTML = (d.users || []).map(u => `
            <div class="result-chip mb-2 p-3 border rounded bg-white">
                <strong>${esc(u.username)}</strong><br>
                <small class="text-muted">${esc(u.role)} · ${u.active ? 'aktivní' : 'vypnutý'} · změna hesla: ${u.must_change_password ? 'vyžadována' : 'ok'} · last login: ${esc(u.last_login || 'nikdy')}</small>
                <div class="form-actions mt-2 d-flex gap-2 flex-wrap">
                    <button class="btn btn-sm btn-secondary" data-toggle="${esc(u.username)}" type="button">Aktivovat / deaktivovat</button>
                    <select class="form-select form-select-sm w-auto" data-role="${esc(u.username)}">
                        <option ${u.role === 'viewer' ? 'selected' : ''}>viewer</option>
                        <option ${u.role === 'operator' ? 'selected' : ''}>operator</option>
                        <option ${u.role === 'admin' ? 'selected' : ''}>admin</option>
                    </select>
                    <button class="btn btn-sm btn-secondary" data-save="${esc(u.username)}" type="button">Uložit roli</button>
                    <button class="btn btn-sm btn-warning" data-reset="${esc(u.username)}" type="button">Reset hesla</button>
                    <button class="btn btn-sm btn-danger" data-delete="${esc(u.username)}" type="button">Smazat</button>
                </div>
            </div>
        `).join('');

        box.querySelectorAll('[data-toggle]').forEach(b => b.onclick = async () => {
            await fetch('/api/v1/admin/users/toggle', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: b.dataset.toggle }) });
            loadUsers();
        });
        box.querySelectorAll('[data-save]').forEach(b => b.onclick = async () => {
            let sel = box.querySelector(`[data-role="${b.dataset.save}"]`);
            await fetch('/api/v1/admin/users/role', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: b.dataset.save, role: sel.value }) });
            loadUsers();
        });
        box.querySelectorAll('[data-reset]').forEach(b => b.onclick = async () => {
            let np = prompt('Nové heslo pro ' + b.dataset.reset);
            if (!np) return;
            let r = await fetch('/api/v1/admin/users/reset-password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: b.dataset.reset, new_password: np }) }),
                d = await r.json();
            alert(r.ok ? 'Heslo resetováno' : d.error);
            loadUsers();
        });
        box.querySelectorAll('[data-delete]').forEach(b => b.onclick = async () => {
            if (!confirm('Opravdu smazat ' + b.dataset.delete + '?')) return;
            let r = await fetch('/api/v1/admin/users/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: b.dataset.delete }) }),
                d = await r.json();
            if (!r.ok) alert(d.error);
            loadUsers();
        });
    }

    async function loadAudit() {
        let r = await fetch('/api/v1/admin/audit'), d = await r.json();
        audit.innerHTML = !r.ok ? '<div class="result-chip text-danger">' + esc(d.error) + '</div>' : (d.entries || []).map(x => `<div class="result-chip mb-1"><strong>${esc(x.action)}</strong><br><small class="text-muted">${esc(x.at)} · ${esc(x.actor)} · ${esc(x.detail)}</small></div>`).join('') || '<div class="result-chip">Zatím bez záznamů.</div>';
    }

    async function load() {
        await loadUsers();
        await loadAudit();
    }

    const createUserForm = document.querySelector('#create-user-form');
    if (createUserForm) {
        createUserForm.onsubmit = async e => {
            e.preventDefault();
            let r = await fetch('/api/v1/admin/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.querySelector('#new-user').value,
                    password: document.querySelector('#new-pass').value,
                    role: document.querySelector('#new-role').value
                })
            }),
            d = await r.json();
            msg.textContent = r.ok ? `Vytvořen ${d.username}` : d.error;
            load();
        };
    }

    load();
}
