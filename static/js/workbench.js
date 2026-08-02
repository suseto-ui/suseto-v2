/* workbench.js — Data & Identifier Analysis Workbench */
const $ = id => document.getElementById(id);

async function postJSON(url, data) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  return await resp.json();
}

function showJSON(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

// Ingest
$('wb_ingest')?.addEventListener('click', async () => {
  const raw = ($('wb_raw')?.value || '').trim();
  if (!raw) return;
  const res = await postJSON('/api/v1/workbench/ingest', {raw});
  showJSON($('wb_analysis'), res);
  const badge = $('wb_type_badge');
  if (badge && res.identifier) {
    badge.textContent = '🔍 ' + res.identifier.type;
    badge.style.display = 'inline-block';
  }
});

// Analysis Pipeline
$('wb_run_analysis')?.addEventListener('click', async () => {
  const raw = ($('wb_raw')?.value || '').trim();
  if (!raw) return;
  const ingest = await postJSON('/api/v1/workbench/ingest', {raw});
  const res = await postJSON('/api/v1/workbench/analyze', {identifier: ingest.identifier || {raw}});
  showJSON($('wb_analysis'), res);
  const risk = $('wb_risk');
  if (risk && res.analysis) {
    const score = res.analysis.risk_score || 0;
    risk.style.display = 'block';
    risk.textContent = '⚠ Risk score: ' + score + (res.analysis.notes?.length ? ' — ' + res.analysis.notes.join(', ') : '');
    risk.style.background = score >= 25 ? '#5d1f1f' : score >= 10 ? '#4a3f00' : '#1f3d1f';
    risk.style.color = score >= 25 ? '#ff6b6b' : score >= 10 ? '#ffd54f' : '#69f0ae';
  }
});

// Reverse Engineering
$('wb_run_reverse')?.addEventListener('click', async () => {
  const raw = ($('wb_raw')?.value || '').trim();
  if (!raw) return;
  const res = await postJSON('/api/v1/workbench/reverse', {raw});
  showJSON($('wb_reverse'), res);
});

// Test Harness
$('wb_run_tests')?.addEventListener('click', async () => {
  const target = $('wb_target')?.value?.trim();
  const mode = $('wb_mode')?.value || 'url';
  const runs = parseInt($('wb_runs')?.value || '3', 10);
  if (!target) {
    $('wb_report').textContent = 'Chybí cílový endpoint.';
    return;
  }
  $('wb_report').textContent = 'Probíhají testy...';
  const res = await postJSON('/api/v1/workbench/test-run', {target, profile: {mode, runs}});
  showJSON($('wb_report'), res);
});