const menu=document.querySelector('.menu');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('nav').classList.toggle('open',open)});
const search=document.querySelector('#search');
function filter(){let shown=0;const q=(search?.value||'').toLowerCase();const category=document.querySelector('#category')?.value||'';document.querySelectorAll('[data-post]').forEach(p=>{const match=p.dataset.post.includes(q)&&(!category||p.dataset.project===category);p.hidden=!match;if(match)shown++});const empty=document.querySelector('#no-results');if(empty)empty.hidden=shown!==0}
search?.addEventListener('input',filter);document.querySelector('#category')?.addEventListener('change',filter);
const dialog=document.querySelector('#photo-dialog');
document.querySelectorAll('[data-photo]').forEach(b=>b.addEventListener('click',()=>{dialog.querySelector('img').src=b.dataset.photo;dialog.querySelector('img').alt=b.dataset.alt;dialog.querySelector('p').textContent=b.dataset.caption;dialog.showModal()}));
dialog?.querySelector('button').addEventListener('click',()=>dialog.close());
dialog?.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});

// Add downloadable design files on individual design pages.
// Future downloads can be added to the map without changing the site generator.
const designDownloads={
  'dpv-compass':{file:'assets/designs/genesis-dpv-compass-mount.stl',label:'Download STL file'}
};
const designSlug=window.location.pathname.match(/\/designs\/([^/]+)\/?(?:index\.html)?$/)?.[1];
const designDetails=document.querySelector('article.page-content.prose');
if(designSlug && designDetails && designDownloads[designSlug]){
  const item=designDownloads[designSlug];
  const link=document.createElement('a');
  link.href='/'+item.file;
  link.download=item.file.split('/').pop();
  link.className='button';
  link.textContent=item.label;
  const meta=designDetails.querySelector('.detail-meta');
  if(meta)meta.insertAdjacentElement('afterend',link);
}
