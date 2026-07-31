const f=document.querySelector('#label-form');
const p=document.querySelector('#label-preview');
const e=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;');

function renderSingle(){
  p.innerHTML=`<div class="eyebrow">${e(document.querySelector('#ld-note').value)}</div><h2>${e(document.querySelector('#ld-title').value)}</h2><code>${e(document.querySelector('#ld-payload').value)}</code><br><button class="btn btn-secondary" onclick="window.print()">Tisk</button>`;
}

f?.addEventListener('submit', x=>{x.preventDefault();renderSingle()});

document.querySelector('#ld-sheet')?.addEventListener('click', ()=>{
  const items=document.querySelector('#ld-batch').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  p.innerHTML=items.map(v=>`<div class="print-label"><div class="eyebrow">${e(document.querySelector('#ld-note').value)}</div><h2>${e(document.querySelector('#ld-title').value)}</h2><code>${e(v)}</code></div>`).join('')+`<div style="margin-top:16px"><button class="btn btn-secondary" onclick="window.print()">Tisk archu</button></div>`;
});

f?.requestSubmit();