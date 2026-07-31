(function(){
  const input = document.getElementById('scan-payload');
  const report = document.getElementById('scan-report');
  const hex = document.getElementById('scan-hex');
  const historyEl = document.getElementById('scan-history');
  const imageInput = document.getElementById('scan-image');
  if (!input || !report || !historyEl) return; // nothing to do on other pages

  let scanner = null, scannerLibraryPromise = null;
  let scanHistory = JSON.parse(localStorage.getItem('susetoScanHistory')||'[]');
  let selected = new Set();
  const esc = v => String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');

  function saveHistory(){ localStorage.setItem('susetoScanHistory', JSON.stringify(scanHistory)) }
  function renderHistory(){
    if(!scanHistory.length){ historyEl.innerHTML = '<div class="result-chip">Zatím žádné scany.</div>'; return }
    historyEl.innerHTML = scanHistory.map((x,i)=>`<label class="history-row"><input type="checkbox" data-i="${i}" ${selected.has(i)?'checked':''}><span><strong>${esc(x.classification)}</strong><br><small>${esc(x.at.replace('T',' ').slice(0,19))} · ${esc(x.payload)}</small></span><button type="button" data-use="${i}" class="text-btn">Použít</button></label>`).join('');
    historyEl.querySelectorAll('input[data-i]').forEach(x=>x.onchange=()=>{x.checked?selected.add(+x.dataset.i):selected.delete(+x.dataset.i)});
    historyEl.querySelectorAll('[data-use]').forEach(x=>x.onclick=()=>{ input.value = scanHistory[+x.dataset.use].payload; analyze(input.value) });
  }

  function showHex(d){ if(hex) hex.textContent = `HEX\n${d.hex||'—'}\n\nASCII\n${d.ascii||'—'}` }
  function addHistory(d){ const duplicate = scanHistory.findIndex(x=>x.payload===d.payload); if(duplicate>=0) scanHistory.splice(duplicate,1); scanHistory.unshift({payload:d.payload,classification:d.classification,at:new Date().toISOString()}); scanHistory = scanHistory.slice(0,50); saveHistory(); renderHistory() }

  function loadScannerLibrary(){
    if(window.Html5Qrcode) return Promise.resolve();
    if(scannerLibraryPromise) return scannerLibraryPromise;
    const sources = ['https://cdn.jsdelivr.net/npm/html5-qrcode@2.3.8/html5-qrcode.min.js','https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'];
    scannerLibraryPromise = new Promise((resolve,reject)=>{
      let i=0; const next = ()=>{ if(i>=sources.length) return reject(Error('Knihovnu html5-qrcode se nepodařilo načíst. Zkontroluj připojení nebo CDN blokování.')); const s=document.createElement('script'); s.src=sources[i++]; s.async=true; s.onload = ()=> window.Html5Qrcode ? resolve() : next(); s.onerror = next; document.head.appendChild(s) };
      next();
    });
    return scannerLibraryPromise;
  }

  async function analyze(value){
    report.innerHTML = '<div class="result-chip">Analyzuji…</div>';
    try{
      const r = await fetch('/api/v1/aidc/analyze-scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({payload:value})});
      const d = await r.json();
      if(!r.ok) throw Error(d.error||'Analýza selhala');
      report.innerHTML = (d.registry_match?`<div class="result-chip"><strong>Registry match: ${esc(d.registry_match.name)}</strong><br><small>${esc(d.registry_match.status)} · ${esc(d.registry_match.tag||'bez tagu')}</small></div>`:'') +
        `<div class="result-chip"><strong>${esc(d.classification)}</strong><br><small>Délka: ${d.length||0} · run: ${esc(d.run.id)}</small></div>` +
        (d.findings||[]).map(x=>`<div class="result-chip"><strong>Nález</strong><br><small>${esc(x)}</small></div>`).join('');
      addHistory(d); showHex(d);
    } catch(e){ report.textContent = e.message }
  }

  const scanAnalyzeBtn = document.getElementById('scan-analyze'); if (scanAnalyzeBtn) scanAnalyzeBtn.onclick = ()=>analyze(input.value);
  input.onkeydown = e=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); analyze(input.value) } };
  const toNavigatorBtn = document.getElementById('scan-to-navigator'); if (toNavigatorBtn) toNavigatorBtn.onclick = ()=>{ localStorage.setItem('susetoDecodeQueue', input.value); location.href='/decode-lab'; };
  const historyClearBtn = document.getElementById('history-clear'); if (historyClearBtn) historyClearBtn.onclick = ()=>{ if(confirm('Vymazat lokální historii scanů?')){ scanHistory=[]; selected.clear(); saveHistory(); renderHistory() } };
  const historyToStateBtn = document.getElementById('history-to-state'); if (historyToStateBtn) historyToStateBtn.onclick = ()=>{ const entries = (selected.size ? [...selected].sort((a,b)=>a-b).map(i=>scanHistory[i]) : scanHistory).map(x=>x.payload); if(!entries.length){ report.innerHTML = '<div class="result-chip">Vyber alespoň jeden scan.</div>'; return } localStorage.setItem('susetoStateQueue', JSON.stringify(entries)); location.href='/state-lab?queue=1' };
  const cameraStartBtn = document.getElementById('camera-start'); if (cameraStartBtn) cameraStartBtn.onclick = async ()=>{ try{ report.innerHTML = '<div class="result-chip">Načítám kamerový scanner…</div>'; await loadScannerLibrary(); scanner = new Html5Qrcode('qr-reader'); await scanner.start({facingMode:'environment'},{fps:10,qrbox:{width:240,height:240}}, async v=>{ input.value = v; await analyze(v); if(scanner) await scanner.stop() }); report.innerHTML = '<div class="result-chip"><strong>Kamera je aktivní</strong><br><small>Zaměř QR nebo podporovaný 1D barcode.</small></div>' } catch(e){ report.innerHTML = `<div class="result-chip"><strong>Kamera není dostupná</strong><br><small>${esc(e.message)}</small></div>` } };
  const cameraStopBtn = document.getElementById('camera-stop'); if (cameraStopBtn) cameraStopBtn.onclick = async ()=>{ if(scanner) try{ await scanner.stop(); report.innerHTML = '<div class="result-chip"><strong>Kamera zastavena</strong></div>' } catch(e){} };

  renderHistory();

  if (imageInput) imageInput.addEventListener('change',async e=>{ const file = e.target.files && e.target.files[0]; if(!file) return; try{ await loadScannerLibrary(); const tmp='scan-image-reader'; let el = document.getElementById(tmp); if(!el){ el = document.createElement('div'); el.id = tmp; el.style.display = 'none'; document.body.appendChild(el) } const reader = new Html5Qrcode(tmp); const decoded = await reader.scanFile(file,true); input.value = decoded; await analyze(decoded); reader.clear && reader.clear() } catch(err){ if (report) report.innerHTML = `<div class="result-chip"><strong>Fotku se nepodařilo přečíst</strong><br><small>${esc(err.message||err)}</small></div>` } });
})();
