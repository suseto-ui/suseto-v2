(function () {
  const keys = {
    history: 'susetoWorkspaceHistory'
  };

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (e) {
      return fallback;
    }
  }

  function writeJson(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {}
  }

  function pushWorkspaceHistory(entry) {
    const items = readJson(keys.history, []);
    items.unshift({
      at: new Date().toISOString(),
      ...entry
    });
    writeJson(keys.history, items.slice(0, 50));
  }

  function getWorkspaceHistory() {
    return readJson(keys.history, []);
  }

  function esc(v) {
    return String(v ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  }

  function renderWorkspaceHistory() {
    const host = document.getElementById('workspace-history');
    if (!host) return;
    const items = getWorkspaceHistory();
    if (!items.length) {
      host.innerHTML = '<div class="result-chip"><strong>Zatím bez historie</strong><br><small>Poslední práce se objeví po prvním scanování, decode analýze nebo navazujícím kroku.</small></div>';
      return;
    }
    host.innerHTML = items.slice(0, 8).map(item => `
      <div class="result-chip">
        <strong>${esc(item.module || 'workspace')}</strong><br>
        <small>${esc((item.at || '').replace('T', ' ').slice(0, 19))} · ${esc(item.label || item.payload || '')}</small>
      </div>
    `).join('');
  }

  window.SusetoCore = {
    pushWorkspaceHistory,
    getWorkspaceHistory,
    renderWorkspaceHistory
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderWorkspaceHistory);
  } else {
    renderWorkspaceHistory();
  }
})();
