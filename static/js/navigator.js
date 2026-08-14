const f = document.getElementById('analyze-form'),
      p = document.getElementById('payload'),
      c = document.getElementById('classes'),
      r = document.getElementById('reco'),
      t = document.getElementById('tree'),
      s = document.getElementById('sample');

const esc = v => String(v).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

const chip = (k, v) => {
    const d = document.createElement('div');
    d.className = 'result-chip';
    d.innerHTML = `<strong>${esc(k)}</strong><br><small>${esc(v)}</small>`;
    return d;
};

async function go(q) {
    const z = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload: q })
    });
    if (!z.ok) {
        throw new Error('Chyba serveru při analýze (HTTP ' + z.status + ')');
    }
    return await z.json();
}

f?.addEventListener('submit', async e => {
    e.preventDefault();
    c.innerHTML = '';
    r.innerHTML = '';
    t.innerHTML = '';
    
    try {
        const d = await go(p.value.trim());
        (d.classifications || []).forEach(i => c.appendChild(chip(i.type, i.confidence)));
        (d.recommendations || []).forEach(i => r.appendChild(chip('tip', i)));
        (d.tree || []).forEach(n => t.appendChild(chip(n.label, n.value || '')));
    } catch (err) {
        c.appendChild(chip('Chyba spojení', err.message || 'Nepodařilo se dokončit analýzu'));
    }
});

s?.addEventListener('click', () => p.value = 'eyJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiJob3N0In0.sig');
