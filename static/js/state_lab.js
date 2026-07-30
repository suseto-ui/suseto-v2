const graphEl=document.getElementById('state-graph');
const detailEl=document.getElementById('state-detail');
const frontierEl=document.getElementById('frontier');
const timelineEl=document.getElementById('replay-timeline');
const statusEl=document.getElementById('run-status');
const selectedStatus=document.getElementById('selected-status');
const seedEl=document.getElementById('state-seed');
let graphData=null, selectedId='root';const queuePanel=document.getElementById('state-queue-panel'),queueEl=document.getElementById('state-queue');
const escapeHtml=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const api=(url,body)=>fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>{if(!r.ok)throw new Error('API '+r.status);return r.json()});
function chip(title,value){return `<div class="result-chip"><strong>${escapeHtml(title)}</strong><br><small>${escapeHtml(value)}</small></div>`}
function renderGraph(nodes){graphEl.innerHTML=''; nodes.forEach(n=>{const b=document.createElement('button');b.type='button';b.className=`state-node state-${n.status}${n.id===selectedId?' selected':''}`;b.dataset.id=n.id;b.innerHTML=`<span class="node-label">${escapeHtml(n.label)}</span><span class="node-meta">${Math.round(n.score*100)}% · ${escapeHtml(n.status)}</span>`;b.addEventListener('click',()=>selectState(n.id));graphEl.appendChild(b)})}
function renderFrontier(frontier){frontierEl.innerHTML=frontier.map((n,i)=>`<button class="frontier-row" data-state="${escapeHtml(n.id)}" type="button"><span>#${i+1} ${escapeHtml(n.label)}</span><strong>${Math.round(n.score*100)}%</strong></button>`).join('');frontierEl.querySelectorAll('[data-state]').forEach(b=>b.addEventListener('click',()=>selectState(b.dataset.state)))}
async function selectState(id){selectedId=id; statusEl.textContent='Načítám detail uzlu…';try{const d=await api('/api/v1/state-detail',{state_id:id});selectedStatus.textContent=d.status;selectedStatus.className=`status-badge status-${d.status}`;detailEl.innerHTML=chip(d.label,`${Math.round(d.score*100)}% confidence · ${d.notes}`)+`<div class="heuristics"><strong>Heuristiky</strong>${d.heuristics.map(h=>`<div class="weight-row"><span>${escapeHtml(h.name)}</span><span>${Math.round(h.weight*100)}%</span></div>`).join('')}</div>`+chip('Další přechody',(d.next||[]).join(' → '));renderGraph(graphData.nodes);statusEl.textContent=`Vybraný uzel: ${d.label}`}catch(e){detailEl.innerHTML=chip('Chyba',e.message);statusEl.textContent='Načtení detailu selhalo'}}
async function replay(){if(!graphData)return;statusEl.textContent='Přehrávám rozhodovací trasu…';const path=graphData.nodes.filter(n=>n.id!=='backtrack').map(n=>n.id);try{const d=await api('/api/v1/replay',{path});timelineEl.innerHTML=d.events.map(e=>`<li><span class="timeline-step">${e.step}</span><div><strong>${escapeHtml(e.label)}</strong><small>${escapeHtml(e.reason)} · ${Math.round(e.score*100)}%</small></div></li>`).join('');statusEl.textContent='Replay dokončen'}catch(e){timelineEl.innerHTML=`<li>Chyba: ${escapeHtml(e.message)}</li>`;statusEl.textContent='Replay selhal'}}
function setupQueue(){let q=[];try{q=JSON.parse(localStorage.getItem('susetoStateQueue')||'[]')}catch(e){};if(!q.length)return;queuePanel.hidden=false;queueEl.innerHTML=q.map((v,i)=>`<button class="frontier-row" data-q="${i}" type="button"><span>Scan ${i+1}</span><strong>${escapeHtml(v.length>42?v.slice(0,42)+'…':v)}</strong></button>`).join('');queueEl.querySelectorAll('[data-q]').forEach(b=>b.onclick=()=>{seedEl.value=q[+b.dataset.q];load()})}
async function load(){statusEl.textContent='Načítám stavový graf…';try{graphData=await api('/api/v1/state-graph',{seed:seedEl.value.trim()||'demo'});renderGraph(graphData.nodes);renderFrontier(graphData.frontier);timelineEl.innerHTML='';await selectState(selectedId);statusEl.textContent='Graf je připraven'}catch(e){graphEl.innerHTML=chip('Chyba',e.message);statusEl.textContent='Načtení grafu selhalo'}}
document.getElementById('load-graph').addEventListener('click',load);setupQueue();document.getElementById('replay-run').addEventListener('click',replay);load();
const strategyEl=document.getElementById('strategy'),budgetEl=document.getElementById('budget');document.getElementById('run-heuristic')?.addEventListener('click',async()=>{statusEl.textContent='Počítám heuristickou frontier…';try{const d=await api('/api/v1/heuristic-run',{seed:seedEl.value.trim()||'demo',strategy:strategyEl.value,budget:+budgetEl.value});renderFrontier(d.frontier.map(x=>({...x,status:d.strategy})));statusEl.textContent=`Běh ${d.run.id}: ${d.frontier.length} kandidátů`;timelineEl.innerHTML=d.frontier.map((x,i)=>`<li><span class="timeline-step">${i+1}</span><div><strong>${escapeHtml(x.label)}</strong><small>score ${Math.round(x.score*100)}% · ${escapeHtml(d.strategy)}</small></div></li>`).join('')}catch(e){statusEl.textContent='Heuristický běh selhal'}});
document.addEventListener('DOMContentLoaded', () => {
    try {
        const queueStr = localStorage.getItem('susetoStateQueue');
        if (queueStr) {
            const queue = JSON.parse(queueStr);
            if (Array.isArray(queue) && queue.length > 0) {
                // Vyplnime prvni zaznam z fronty do seedu a smazeme frontu (nebo nechame uzivateli moznost prepinat)
                const seedInput = document.getElementById('state-seed');
                if (seedInput) {
                    seedInput.value = queue[0];
                    localStorage.removeItem('susetoStateQueue');
                    // Volitelne muzeme rovnou spustit build grafu
                    setTimeout(() => {
                        const initBtn = document.getElementById('state-init');
                        if(initBtn) initBtn.click();
                    }, 200);
                }
            }
        }
    } catch(e) {
        console.error("Chyba pri zpracovani susetoStateQueue", e);
    }
});
