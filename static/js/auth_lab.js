const form=document.getElementById('auth-form'),out=document.getElementById('auth-output'),tl=document.getElementById('auth-timeline'),risk=document.getElementById('risk');
const e=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');

if (form) {
  form.addEventListener('submit',async x=>{
    x.preventDefault();
    if (out) out.innerHTML='<div class="result-chip">Probíhá sandbox simulace…</div>';

    const scenarioEl = document.getElementById('scenario');
    const attemptsEl = document.getElementById('attempts');
    const rateLimitEl = document.getElementById('rate-limit');
    const uniformEl = document.getElementById('uniform');
    const mfaEl = document.getElementById('mfa');

    const body = {
      scenario: scenarioEl ? scenarioEl.value : '',
      attempts: attemptsEl ? +attemptsEl.value : 0,
      defense: {
        rate_limit: rateLimitEl ? +rateLimitEl.value : 0,
        uniform_response: uniformEl ? uniformEl.checked : false,
        mfa_required: mfaEl ? mfaEl.checked : false
      }
    };

    try{
      const r = await fetch('/api/v1/auth-simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const d = await r.json();
      if (risk) { risk.textContent = d.risk; risk.className = 'status-badge risk-'+d.risk }
      if (out) out.innerHTML = `<div class="result-chip"><strong>${e(d.title)}</strong><br><small>${e(d.owasp)} · ${e(d.mitigation)}</small></div>` + (d.finding||[]).map(i=>`<div class="result-chip"><strong>Nález</strong><br><small>${e(i)}</small></div>`).join('') + `<div class="result-chip"><strong>Bezpečnostní režim</strong><br><small>Sandbox: ${d.sandbox}; externí požadavky: ${d.external_requests}; run: ${e(d.run.id)}</small></div>`;
      if (tl) tl.innerHTML = (d.timeline||[]).map(i=>`<li><span class="timeline-step">${i.step}</span><div><strong>${e(i.state)}</strong><small>${e(i.reason)}</small></div></li>`).join('');
    }catch(err){ if (out) out.innerHTML=`<div class="result-chip"><strong>Chyba</strong><br><small>${e(err.message)}</small></div>` }
  });
}
