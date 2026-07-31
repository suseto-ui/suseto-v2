const out=document.querySelector('#decode-out');
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const form=document.querySelector('#decode-form');
const payloadEl=document.querySelector('#decode-payload');
const manyEl=document.querySelector('#decode-many');
const libBtn=document.querySelector('#decode-library-btn');
function empty(msg){out.innerHTML=`<div class="result-chip"><strong>Výstup</strong><br><small>${esc(msg)}</small></div>`}
async function callApi(url, body){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  let d={};
  try{d=await r.json()}catch(e){d={error:'Server nevrátil JSON odpověď.'}}
  if(!r.ok) throw new Error(d.error||('HTTP '+r.status));
  return d;
}
function renderChain(d){
  const items=(d.candidates||[]);
  if(!items.length){empty('Žádní kandidáti k zobrazení.'); return;}
  out.innerHTML=items.map(c=>`<div class="result-chip"><strong>${esc(c.type||'candidate')}</strong><br><small>${Math.round((c.confidence||0)*100)}% · entropy ${esc(c.entropy)} · ascii ${esc(c.ascii_ratio)}</small><pre class="hex-box">${esc(c.output||'')}</pre><small>${esc(((c.patterns||[]).map(x=>(x.name||'')+': '+(x.detail||'')).join(' | ')) || c.reason || '')}</small></div>`).join('');
}
function renderLibrary(d){
  const groups=d.groups||[];
  const rows=d.rows||[];
  out.innerHTML=(groups.map(g=>`<div class="result-chip"><strong>${esc(g.pattern_set)}</strong><br><small>${esc(g.count)} položek · ${esc((g.examples||[]).join(', '))}</small></div>`).join('')||'') + (rows.length?`<pre class="hex-box">${esc(JSON.stringify(rows,null,2))}</pre>`:'');
  if(!groups.length && !rows.length) empty('Pattern Library nenašla žádná data.');
}
const doChain = async (e) => {
  if(e) e.preventDefault();
  const payload=(payloadEl?.value||'').trim();
  if(!payload){empty('Nejprve vlož payload.'); return;}
  empty('Analyzuji…');
  try{renderChain(await callApi('/api/v1/decode/chain',{payload}))}catch(err){empty(err.message)}
};
form?.addEventListener('submit', doChain);
libBtn?.addEventListener('click', async ()=>{
  const vals=(manyEl?.value||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  if(!vals.length){empty('Vlož alespoň jeden payload pro Pattern Library.'); return;}
  empty('Počítám Pattern Library…');
  try{renderLibrary(await callApi('/api/v1/decode/library',{payloads:vals}))}catch(err){empty(err.message)}
});
empty('Vlož payload a spusť analýzu.');
document.addEventListener('DOMContentLoaded', () => {
    const queue = localStorage.getItem('susetoDecodeQueue');
    if (queue) {
        const payloadEl = document.querySelector('#decode-payload');
        if (payloadEl) {
            payloadEl.value = queue;
            localStorage.removeItem('susetoDecodeQueue');
            // Auto-trigger analysis
            setTimeout(() => {
                const form = document.querySelector('#decode-form');
                if (form) doChain();
            }, 100);
        }
    }
});
