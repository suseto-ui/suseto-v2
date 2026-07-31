const out=document.querySelector('#exp-out');
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;');

const form=document.querySelector('#exp-form');
form?.addEventListener('submit', async e => {
  e.preventDefault();
  const expected = document.querySelector('#exp-expected').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  const scanned = document.querySelector('#exp-scanned').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  const r = await fetch('/api/v1/expected-audit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expected,scanned})});
  const d = await r.json();
  out.innerHTML = `
    <div class="result-chip"><strong>Nalezené</strong><br><small>${esc(d.found.join(', ')||'—')}</small></div>
    <div class="result-chip"><strong>Chybějící</strong><br><small>${esc(d.missing.join(', ')||'—')}</small></div>
    <div class="result-chip"><strong>Nečekané</strong><br><small>${esc(d.unexpected.join(', ')||'—')}</small></div>`;
});