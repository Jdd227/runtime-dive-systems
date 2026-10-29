const menu=document.querySelector('.menu');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('nav').classList.toggle('open',open)});
const search=document.querySelector('#search');
function filter(){let shown=0;const q=(search?.value||'').toLowerCase();const category=document.querySelector('#category')?.value||'';document.querySelectorAll('[data-post]').forEach(p=>{const match=p.dataset.post.includes(q)&&(!category||p.dataset.project===category);p.hidden=!match;if(match)shown++});const empty=document.querySelector('#no-results');if(empty)empty.hidden=shown!==0}
search?.addEventListener('input',filter);document.querySelector('#category')?.addEventListener('change',filter);
const dialog=document.querySelector('#photo-dialog');
document.querySelectorAll('[data-photo]').forEach(b=>b.addEventListener('click',()=>{dialog.querySelector('img').src=b.dataset.photo;dialog.querySelector('img').alt=b.dataset.alt;dialog.querySelector('p').textContent=b.dataset.caption;dialog.showModal()}));
dialog?.querySelector('button').addEventListener('click',()=>dialog.close());
dialog?.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
