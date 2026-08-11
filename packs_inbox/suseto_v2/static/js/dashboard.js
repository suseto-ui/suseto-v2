const kpisEl = document.querySelector('#dash-kpis');
const chartEl = document.querySelector('#dash-chart');
const recentEl = document.querySelector('#dash-recent');
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');

async function load() {
    try {
        const r = await fetch('/api/v1/dashboard/stats');
        const d = await r.json();
        if(!r.ok) {
            kpisEl.innerHTML = `<div class="result-chip">${esc(d.error)}</div>`;
            return;
        }

        const kpis = d.kpis;
        kpisEl.innerHTML = `
            <div class="result-chip" style="flex:1"><strong>Uživatelé</strong><br><span style="font-size:24px">${kpis.users}</span></div>
            <div class="result-chip" style="flex:1"><strong>Lokace</strong><br><span style="font-size:24px">${kpis.locations}</span></div>
            <div class="result-chip" style="flex:1"><strong>Skeny/Akce</strong><br><span style="font-size:24px">${kpis.timeline_events}</span></div>
            <div class="result-chip" style="flex:1"><strong>Audit log</strong><br><span style="font-size:24px">${kpis.audit_events}</span></div>
        `;

        const maxCount = Math.max(...d.chart.map(c => c.count), 1);
        chartEl.innerHTML = d.chart.map(c => {
            const h = (c.count / maxCount) * 100;
            return `<div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:5px;">
                <div style="width:100%; background:#01696f; height:${h}%; min-height: 2px; border-radius:4px 4px 0 0;" title="${c.count} skenů"></div>
                <small style="font-size:10px; color:#64748b">${c.date.slice(5)}</small>
            </div>`;
        }).join('');

        recentEl.innerHTML = d.recent.map(x => `<div class="result-chip"><strong>${esc(x.action)}</strong><br><small>${esc(x.at.replace('T',' ').slice(0,19))} · ${esc(x.actor)} · ${esc(x.asset_key)}</small></div>`).join('') || '<div class="result-chip">Žádná aktivita.</div>';
    } catch(err) {
        kpisEl.innerHTML = `<div class="result-chip">Chyba: ${esc(err.message)}</div>`;
    }
}
load();