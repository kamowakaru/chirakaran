(()=>{
  const b=document.body,root=b.dataset.root||'';
  const menu=document.querySelector('.menu-btn'),nav=document.querySelector('.nav');
  if(menu&&nav)menu.addEventListener('click',()=>nav.classList.toggle('open'));
  const J=async p=>{const r=await fetch(root+p);if(!r.ok)throw new Error(p);return r.json()};
  const catName=async slug=>{const c=await J('data/categories.json');return c.find(x=>x.slug===slug)?.name||slug};
  function esc(s){return String(s).replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[m]))}
  async function makeCard(a){
    const cn=await catName(a.category),tags=await J('data/tags.json');
    const chips=a.tags.map(t=>{const n=tags.find(x=>x.slug===t)?.name||t;return `<a class="tag-link" href="${root}tags/${t}.html">${esc(n)}</a>`}).join('');
    const thumbnail=a.thumbnail||'assets/images/thumbnail-fallback.svg';
    return `<article class="card"><div class="thumb"><img src="${root}${thumbnail}" alt="${esc(a.title)}のサムネイル" loading="lazy"></div><div class="card-body"><span class="chip">${esc(cn)}</span><h3><a href="${root}articles/${a.slug}.html">${esc(a.title)}</a></h3><p>${esc(a.description)}</p><div class="meta">${chips}<time>${a.date.replaceAll('-','.')}</time></div></div></article>`;
  }
  async function renderCollection(){
    const el=document.querySelector('[data-collection]');if(!el)return;
    const mode=el.dataset.collection,key=el.dataset.key;const arts=await J('data/articles.json');let f=arts;
    if(mode==='category')f=arts.filter(a=>a.category===key);
    if(mode==='tag')f=arts.filter(a=>a.tags.includes(key));
    if(mode==='latest')f=arts.slice().sort((a,b)=>b.date.localeCompare(a.date));
    const lim=parseInt(el.dataset.limit||'0',10);if(lim)f=f.slice(0,lim);
    el.innerHTML=(await Promise.all(f.map(makeCard))).join('')||'<div class="empty-note">まだ記事がありません。</div>';
  }
  async function renderPopular(){
    const box=document.querySelector('[data-popular-tags]');if(!box)return;let pts=[];
    try{pts=await J('data/popular-tags.json')}catch{}
    if(!pts.length){const[arts,tgs]=await Promise.all([J('data/articles.json'),J('data/tags.json')]);pts=tgs.map(t=>({slug:t.slug,name:t.name,score:arts.filter(a=>a.tags.includes(t.slug)).length})).sort((a,b)=>b.score-a.score).slice(0,8)}
    box.innerHTML=pts.slice(0,8).map(t=>`<a href="${root}tags/${t.slug}.html">${esc(t.name)}</a>`).join('');
  }
  async function search(){
    const wrap=document.querySelector('[data-search-results]');if(!wrap)return;
    const q=new URLSearchParams(location.search).get('q')?.trim()||'';document.querySelector('[data-search-query]').textContent=q||'すべて';
    const arts=await J('data/articles.json'),tgs=await J('data/tags.json'),cats=await J('data/categories.json');
    const out=!q?arts:arts.filter(a=>{const cat=cats.find(c=>c.slug===a.category)?.name||'';const names=a.tags.map(x=>tgs.find(t=>t.slug===x)?.name||'').join(' ');return(a.title+' '+a.description+' '+cat+' '+names).toLowerCase().includes(q.toLowerCase())});
    wrap.innerHTML=out.map(a=>`<a class="search-row" href="${root}articles/${a.slug}.html"><strong>${esc(a.title)}</strong><small>${esc(a.description)}</small></a>`).join('')||'<div class="empty-note">該当する記事がありません。</div>';
  }
  async function related(){
    const el=document.querySelector('[data-related]');if(!el)return;
    const arts=await J('data/articles.json'),cat=el.dataset.category,slug=el.dataset.slug;
    const f=arts.filter(a=>a.category===cat&&a.slug!==slug).slice(0,3);
    el.innerHTML=(await Promise.all(f.map(makeCard))).join('')||'<div class="empty-note">関連する記事はまだありません。</div>';
  }
  renderCollection();renderPopular();search();related();
})();
