const C = window.LCS || {};
document.querySelectorAll('[data-f]').forEach(el => { const v = C[el.dataset.f]; if (v !== undefined && v !== '') el.textContent = v; else if (el.dataset.hideEmpty !== undefined) el.style.display='none'; });
const L = document.getElementById('links');
if (L && C.links) L.innerHTML = C.links.map((t,i)=>`<span class="pill ${i%2?'pink':''}">${t}</span>`).join('');
const clock = document.getElementById('clock');
if (clock) { const t=()=>clock.textContent=new Date().toLocaleTimeString([], {hour:'numeric',minute:'2-digit'}); t(); setInterval(t,5000); }
