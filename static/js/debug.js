const out=document.querySelector('#dbg-out');
const logEl=document.querySelector('#dbg-log');
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function log(msg){if(logEl)logEl.textContent+=(logEl.textContent==='Připraveno.'?'':'\n')+msg}
function chip(t,m){return `<div class="result-chip"><strong>${esc(t)}</strong><br><small>${m}</small></div>`} // changed ${esc(m)} to ${m} because we pass HTML sometimes
async function j(url,opt){
  log('FETCH '+url);
  let r;
  try {
    r=await fetch(url,opt);
  } catch(err){
    log(url+' -> CHYBA: '+err.message);
    return {ok:false, status:0, data:{error:err.message}};
  }
  let d={};
  try{d=await r.json()}catch(e){d={error:'Neplatný JSON'}}
  log(url+' -> '+r.status);
  return {ok:r.ok,status:r.status,data:d}
}

document.addEventListener('DOMContentLoaded', () => {
    const btnRoutes = document.querySelector('#dbg-routes');
    if(btnRoutes) btnRoutes.onclick=async()=>{
        let x=await j('/api/v1/debug/routes');
        out.innerHTML=x.ok?chip('Routy',`${(x.data.routes||[]).length} záznamů`)+`<pre class="hex-box">${esc((x.data.routes||[]).join('\n'))}</pre>`:chip('Chyba',x.data.error||x.status)
    };

    const btnPing = document.querySelector('#dbg-ping');
    if(btnPing) btnPing.onclick=async()=>{
        let x=await j('/api/v1/debug/ping',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({hello:'world'})});
        out.innerHTML=x.ok?chip('Ping OK',esc(JSON.stringify(x.data))):chip('Ping chyba',x.data.error||x.status)
    };

    const btnRun = document.querySelector('#dbg-run');
    if(btnRun) btnRun.onclick=async()=>{
        out.innerHTML='';
        if(logEl)logEl.textContent='Připraveno.';
        const tests=[['Health','/health'],['Auth me','/api/v1/auth/me'],['Routes','/api/v1/debug/routes'],['Status','/api/v1/system-status'],['Inventory','/api/v1/inventory/sessions'],['Locations','/api/v1/locations']];
        let html='';
        for(const [name,url] of tests){
            let r=await j(url);
            html+=chip(name,`HTTP ${r.status} · ${r.ok?'OK':'FAIL'}${r.data.error?' · '+esc(r.data.error):''}`)
        }
        out.innerHTML=html
    };

    const btnEnv = document.querySelector('#dbg-env');
    if(btnEnv) btnEnv.onclick=async()=>{
        let x=await j('/api/v1/debug/env');
        if(!x.ok){
            out.innerHTML=chip('Chyba kontroly', x.data.error || x.status);
            return;
        }
        const d = x.data;
        let html = chip('Systém', `Python: ${esc(d.python)} · Flask: ${esc(d.flask)}`);
        html += chip('Zápis do /data', d.data_write === 'OK' ? 'OK (máme práva zápisu)' : `CHYBA: ${esc(d.data_write)}`);

        const deps = Object.entries(d.deps||{}).map(([k,v]) => `${esc(k)}: ${esc(v)}`).join(' · ');
        html += chip('Knihovny', deps);
        if(d.sys_path) html += chip('Sys Path', `<div style="font-size:10px;line-height:1.2;word-break:break-all">${d.sys_path.map(esc).join('<br>')}</div>`);

        const files = Object.entries(d.files||{}).map(([k,v]) => `${esc(k)}: ${esc(v)}`).join('<br>');
        html += chip('Verze souborů (datum změny)', files);

        out.innerHTML = html;
    };

    const btnPip = document.querySelector('#dbg-pip');
    if(btnPip) btnPip.onclick=async()=>{
        out.innerHTML=chip('PIP', 'Zahajuji instalaci, čekejte prosím (může to trvat 10-30 vteřin)...');
        let x=await j('/api/v1/debug/install_pip', {method:'POST'});
        if(!x.ok){
            out.innerHTML=chip('PIP Chyba', x.data.error || x.status);
            return;
        }
        out.innerHTML=chip('PIP Výsledek', `<pre class="hex-box" style="font-size:10px">${esc(x.data.log)}</pre>`);
    };
});
