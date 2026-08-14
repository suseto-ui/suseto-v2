// static/js/workbench.js
// Workbench frontend – Data & Identifier Analysis Workbench
// Aktualizováno: Přidán robustní error handling a zamezení pádům skriptu

(function () {
  'use strict';

  // --- ROBUSTNÍ FETCH WRAPPER ---
  async function postJSON(url, data) {
    try {
      const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const contentType = r.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const json = await r.json();
        if (!r.ok) {
          return { ok: false, error: json.error || json.message || `Chyba API (HTTP ${r.status})` };
        }
        return { ok: true, ...json };
      } else {
        return { ok: false, error: `Kritická chyba serveru (HTTP ${r.status}). Očekáván JSON, vráceno HTML.` };
      }
    } catch (err) {
      return { ok: false, error: `Chyba spojení: ${err.message}` };
    }
  }

  function el(id) { return document.getElementById(id); }

  function renderPre(id, data) {
    const target = el(id);
    if (!target) return;
    target.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
  }

  // Type → color mapping
  const TYPE_COLORS = {
    url: '#3b82f6', hex: '#8b5cf6', ean: '#10b981', imei: '#f59e0b',
    jwt: '#ef4444', base64: '#6366f1', json: '#14b8a6', mac: '#f97316',
    uuid: '#ec4899', data_uri: '#84cc16', unknown: '#9ca3af',
  };

  function renderTypeBadge(type) {
    const badge = el('wb_type_badge');
    if (!badge) return;
    const color = TYPE_COLORS[type] || '#9ca3af';
    badge.innerHTML = `<span class="wb-badge" style="background:${color}20;color:${color};border:1px solid ${color}40;">${type}</span>`;
  }

  function renderRiskBar(score, level) {
    const bar = el('wb_risk_bar');
    if (!bar) return;
    const levelColors = { low: '#22c55e', medium: '#facc15', high: '#f97316', critical: '#ef4444' };
    const color = levelColors[level] || '#9ca3af';
    bar.innerHTML = `
      <div class="wb-risk-bar" title="Risk score: ${score}/100">
        <div class="wb-risk-cursor" style="left:${score}%;background:${color};"></div>
      </div>
      <div style="font-size:.8rem;font-weight:700;color:${color};text-transform:uppercase;">
        ${level} &nbsp;·&nbsp; ${score}/100
      </div>`;
  }

  function renderEntropyBar(entropy) {
    const bar = el('wb_entropy_bar');
    if (!bar) return;
    const pct = Math.min(Math.round((entropy / 8) * 100), 100);
    const color = pct > 70 ? '#ef4444' : pct > 45 ? '#f97316' : '#22c55e';
    bar.innerHTML = `
      <div style="font-size:.8rem;margin-bottom:.25rem;">
        Shannon entropie: <strong style="color:${color}">${entropy}</strong> bits/char
        &nbsp;<span style="color:${color};font-size:.75rem;">${pct > 70 ? '(vysoká – šifrováno/komprimováno)' : pct > 45 ? '(střední)' : '(nízká – plaintext)'}</span>
      </div>
      <div style="background:#e5e7eb;border-radius:4px;height:6px;">
        <div style="background:${color};height:6px;border-radius:4px;width:${pct}%;transition:width .4s;"></div>
      </div>`;
  }

  let lastIdentifier = null;

  // ── INGEST ──
  el('wb_btn_ingest') && el('wb_btn_ingest').addEventListener('click', async function () {
    const raw = el('wb_raw').value.trim();
    if (!raw) return;
    this.disabled = true;
    this.textContent = '…';
    try {
      const res = await postJSON('/api/v1/workbench/ingest', { raw });
      if (!res.ok) { renderPre('wb_identifier', '⚠ ' + res.error); return; }
      lastIdentifier = res.identifier;
      renderTypeBadge(res.identifier.type);
      renderPre('wb_identifier', res.identifier);
      el('wb_analysis').textContent = '–';
      el('wb_reverse').textContent = '–';
      el('wb_risk_bar').innerHTML = '';
      el('wb_entropy_bar').innerHTML = '';
    } finally {
      this.disabled = false;
      this.textContent = 'Normalizovat & typovat';
    }
  });

  // ── ANALYZE ──
  el('wb_btn_analyze') && el('wb_btn_analyze').addEventListener('click', async function () {
    const raw = el('wb_raw').value.trim();
    if (!raw && !lastIdentifier) { alert('Nejprve vlož identifikátor.'); return; }
    this.disabled = true;
    this.textContent = '…';
    try {
      if (!lastIdentifier || lastIdentifier.raw !== raw) {
        const ir = await postJSON('/api/v1/workbench/ingest', { raw });
        if (!ir.ok) { renderPre('wb_analysis', '⚠ Ingest selhal: ' + ir.error); return; }
        lastIdentifier = ir.identifier;
        renderTypeBadge(ir.identifier.type);
        renderPre('wb_identifier', ir.identifier);
      }
      const res = await postJSON('/api/v1/workbench/analyze', { identifier: lastIdentifier });
      if (!res.ok) { renderPre('wb_analysis', '⚠ ' + res.error); return; }
      renderRiskBar(res.risk_score, res.risk_level);
      renderPre('wb_analysis', { risk_score: res.risk_score, risk_level: res.risk_level, notes: res.notes });
    } finally {
      this.disabled = false;
      this.textContent = '▶ Analyzovat pipeline';
    }
  });

  // ── REVERSE ──
  el('wb_btn_reverse') && el('wb_btn_reverse').addEventListener('click', async function () {
    const raw = el('wb_raw').value.trim();
    if (!raw) { alert('Nejprve vlož identifikátor.'); return; }
    this.disabled = true;
    this.textContent = '…';
    try {
      const res = await postJSON('/api/v1/workbench/reverse', { raw });
      if (!res.ok) { renderPre('wb_reverse', '⚠ ' + res.error); return; }
      renderEntropyBar(res.entropy);
      renderPre('wb_reverse', { detected_layers: res.detected_layers, entropy: res.entropy, candidates: res.candidates });
    } finally {
      this.disabled = false;
      this.textContent = '🔍 Reverzní inženýrství';
    }
  });

  // ── CLEAR ──
  el('wb_btn_clear') && el('wb_btn_clear').addEventListener('click', function () {
    el('wb_raw').value = '';
    lastIdentifier = null;
    ['wb_identifier', 'wb_analysis', 'wb_reverse', 'wb_report'].forEach(id => {
      const e = el(id); if (e) e.textContent = '–';
    });
    ['wb_type_badge', 'wb_risk_bar', 'wb_entropy_bar', 'wb_test_summary'].forEach(id => {
      const e = el(id); if (e) e.innerHTML = '';
    });
  });

  // ── TEST HARNESS ──
  el('wb_btn_test') && el('wb_btn_test').addEventListener('click', async function () {
    const target = el('wb_target').value.trim();
    const mode = el('wb_mode').value;
    const runs = parseInt(el('wb_runs').value, 10) || 5;
    if (!target) { alert('Zadej cílový endpoint.'); return; }
    this.disabled = true;
    this.textContent = 'Testuje…';
    try {
      const res = await postJSON('/api/v1/workbench/test-run', { target, profile: { mode, runs } });
      if (!res.ok) { renderPre('wb_report', '⚠ ' + res.error); return; }
      const summary = el('wb_test_summary');
      if (summary) {
        const passColor = res.failed === 0 ? '#22c55e' : '#ef4444';
        summary.innerHTML = `<span style="font-size:.85rem;font-weight:700;color:${passColor};">
          ✓ ${res.passed} OK &nbsp;·&nbsp; ✗ ${res.failed} selhalo &nbsp;·&nbsp; celkem ${res.total}
        </span>`;
      }
      renderPre('wb_report', res.results);
    } finally {
      this.disabled = false;
      this.textContent = 'Spustit testy';
    }
  });

  // ── Auto-run ingest ──
  el('wb_raw') && el('wb_raw').addEventListener('paste', function () {
    setTimeout(async () => {
      const raw = this.value.trim();
      if (!raw) return;
      try {
        const res = await postJSON('/api/v1/workbench/ingest', { raw });
        if (res.ok) {
          lastIdentifier = res.identifier;
          renderTypeBadge(res.identifier.type);
          renderPre('wb_identifier', res.identifier);
        }
      } catch (_) {}
    }, 50);
  });

})();
