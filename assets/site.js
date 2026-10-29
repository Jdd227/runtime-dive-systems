const menu=document.querySelector('.menu');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('nav').classList.toggle('open',open)});
const search=document.querySelector('#search');
function filter(){let shown=0;const q=(search?.value||'').toLowerCase();const category=document.querySelector('#category')?.value||'';document.querySelectorAll('[data-post]').forEach(p=>{const match=p.dataset.post.includes(q)&&(!category||p.dataset.project===category);p.hidden=!match;if(match)shown++});const empty=document.querySelector('#no-results');if(empty)empty.hidden=shown!==0}
search?.addEventListener('input',filter);document.querySelector('#category')?.addEventListener('change',filter);
const dialog=document.querySelector('#photo-dialog');
document.querySelectorAll('[data-photo]').forEach(b=>b.addEventListener('click',()=>{dialog.querySelector('img').src=b.dataset.photo;dialog.querySelector('img').alt=b.dataset.alt;dialog.querySelector('p').textContent=b.dataset.caption;dialog.showModal()}));
dialog?.querySelector('button').addEventListener('click',()=>dialog.close());
dialog?.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});

// Downloadable 3D-print files on individual design pages.
// List files separately so multi-part designs show all of their STL downloads.
const designDownloads={
  'dpv-compass':[
    {file:'assets/designs/genesis-dpv-compass-mount.stl',label:'Compass mount STL'}
  ],
  'genesis-dpv-holder':[
    {file:'assets/designs/genesis-dpv-stand.stl',label:'Genesis DPV stand STL'},
    {file:'assets/designs/genesis-dpv-holder-spacer-insert.stl',label:'Spacer insert STL'},
    {file:'assets/designs/genesis-dpv-stand-end-cap.stl',label:'Stand end cap STL'}
  ],
  'dpv-light-holders':[
    {file:'assets/designs/ball-mount-blacktip.stl',label:'BlackTip ball mount STL'},
    {file:'assets/designs/tpu-squishy-insert.stl',label:'TPU squishy insert STL'}
  ]
};
const designSlug=window.location.pathname.match(/\/designs\/([^/]+)\/?(?:index\.html)?$/)?.[1];
const designDetails=document.querySelector('article.page-content.prose');
const designFiles=designDownloads[designSlug];
if(designDetails && designFiles?.length){
  const filesSection=document.createElement('section');
  filesSection.className='design-downloads';
  filesSection.setAttribute('aria-label','3D-print design files');
  const heading=document.createElement('h2');
  heading.textContent='3D print files';
  filesSection.appendChild(heading);
  const links=document.createElement('div');
  links.style.display='flex';
  links.style.flexWrap='wrap';
  links.style.gap='12px';
  for(const file of designFiles){
    const link=document.createElement('a');
    link.href='/'+file.file;
    link.download=file.file.split('/').pop();
    link.className='button';
    link.textContent=file.label;
    links.appendChild(link);
  }
  filesSection.appendChild(links);
  const meta=designDetails.querySelector('.detail-meta');
  if(meta)meta.insertAdjacentElement('afterend',filesSection);
}
