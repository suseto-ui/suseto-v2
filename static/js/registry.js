const list=document.querySelector('#reg-list'),q=document.querySelector('#reg-q'),form=document.querySelector('#reg-form'),prof=document.querySelector('#r-profile');const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;');

// Only run registry logic on pages that include registry elements
if (list || q || form || prof) {
  async function load(){
    // q may be present; guard access
    const qv = q ? q.value : '';
    let d = await (await fetch('/api/v1/registry?q='+encodeURIComponent(qv))).json();
    prof.innerHTML = '<option value="">Bez profilu</option>' + (d.profiles||[]).map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join('');
    list.innerHTML = (d.items && d.items.length) ? d.items.map(x=>`<div class="result-chip"><strong>${esc(x.name)}</strong> <span class="badge">${esc(x.status)}</span><br><small>${esc(x.payload)} · ${esc(x.tag||'bez tagu')}</small><br><a class="text-btn" target="_blank" href="/label-print/${x.id}">Tisk</a> <button class="text-btn" data-id="${x.id}" data-status="active">active</button> <button class="text-btn" data-id="${x.id}" data-status="reserved">reserved</button> <button class="text-btn" data-id="${x.id}" data-status="retired">retired</button></div>`).join('') : '<div class="result-chip">Zatím žádné položky.</div>';
    document.querySelectorAll('.text-btn').forEach(b=>b.onclick=async()=>{await fetch('/api/v1/registry/'+b.dataset.id+'/status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:b.dataset.status})});load()})
  }

  if (q) q.oninput = load;

  if (form) form.onsubmit = async e => {
    e.preventDefault();
    let d = {name:document.querySelector('#r-name').value,payload:document.querySelector('#r-payload').value,tag:document.querySelector('#r-tag').value,status:document.querySelector('#r-status').value,profile_id:prof.value};
    let r = await fetch('/api/v1/registry',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
    if(!r.ok) alert((await r.json()).error);
    else { form.reset(); load(); }
  };

  load();

  const registryImportEl = document.querySelector('#registry-import');
  if (registryImportEl) registryImportEl.onchange = async ev => { let f = ev.target.files[0]; if(!f) return; let fd = new FormData(); fd.append('file', f); let r = await fetch('/api/v1/registry/import',{method:'POST',body:fd}), d = await r.json(); if(!r.ok) alert(d.error); else { alert(`Import: ${d.added} přidáno, ${d.skipped.length} přeskočeno.`); load() } ev.target.value = '' };
}
