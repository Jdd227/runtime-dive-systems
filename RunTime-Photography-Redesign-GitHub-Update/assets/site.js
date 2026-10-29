const menu=document.querySelector('.menu');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('nav').classList.toggle('open',open)});
const search=document.querySelector('#search');
function filter(){let shown=0;const q=(search?.value||'').toLowerCase();const category=document.querySelector('#category')?.value||'';document.querySelectorAll('[data-post]').forEach(p=>{const match=p.dataset.post.includes(q)&&(!category||p.dataset.project===category);p.hidden=!match;if(match)shown++});const empty=document.querySelector('#no-results');if(empty)empty.hidden=shown!==0}
search?.addEventListener('input',filter);document.querySelector('#category')?.addEventListener('change',filter);
// Photography gallery: uncropped masonry thumbnails and a keyboard/swipe lightbox.
// The site's photo captions remain hidden. Alt text is retained for accessibility.
const dialog=document.querySelector('#photo-dialog');
const galleryPhotos=[...document.querySelectorAll('.gallery [data-photo]')];
if(dialog && galleryPhotos.length){
  const image=dialog.querySelector('img');
  const close=dialog.querySelector('button');
  const counter=document.createElement('span');
  const toolbar=document.createElement('div');
  const stage=document.createElement('div');
  const hint=document.createElement('p');
  let currentPhoto=0;
  let touchStart=null;

  dialog.classList.add('photo-viewer');
  image.className='photo-viewer-image';
  close.className='photo-viewer-close';
  close.textContent='×';
  close.setAttribute('aria-label','Close photo viewer');
  toolbar.className='photo-viewer-toolbar';
  stage.className='photo-viewer-stage';
  hint.className='photo-viewer-hint';
  hint.textContent='Use ← → to browse · Esc to close';
  counter.setAttribute('aria-live','polite');
  toolbar.append(counter,close);

  function makeArrow(text,label,classname,step){
    const button=document.createElement('button');
    button.type='button';
    button.className='photo-viewer-arrow '+classname;
    button.textContent=text;
    button.setAttribute('aria-label',label);
    button.addEventListener('click',()=>showPhoto(currentPhoto+step));
    return button;
  }
  const previous=makeArrow('‹','Previous photograph','photo-viewer-previous',-1);
  const next=makeArrow('›','Next photograph','photo-viewer-next',1);
  stage.append(image,previous,next);
  dialog.replaceChildren(toolbar,stage,hint);

  function showPhoto(index){
    currentPhoto=(index+galleryPhotos.length)%galleryPhotos.length;
    const target=galleryPhotos[currentPhoto];
    image.src=target.dataset.photo;
    image.alt=target.dataset.alt||'Underwater photograph';
    counter.textContent=`${currentPhoto+1} / ${galleryPhotos.length}`;
  }

  galleryPhotos.forEach((button,index)=>button.addEventListener('click',()=>{
    showPhoto(index);
    if(!dialog.open)dialog.showModal();
    close.focus();
  }));
  close.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
  dialog.addEventListener('close',()=>galleryPhotos[currentPhoto]?.focus());
  dialog.addEventListener('keydown',event=>{
    if(event.key==='ArrowRight'){event.preventDefault();showPhoto(currentPhoto+1)}
    if(event.key==='ArrowLeft'){event.preventDefault();showPhoto(currentPhoto-1)}
  });
  stage.addEventListener('touchstart',event=>{
    if(event.touches.length===1)touchStart={x:event.touches[0].clientX,y:event.touches[0].clientY};
  },{passive:true});
  stage.addEventListener('touchend',event=>{
    if(!touchStart||!event.changedTouches.length)return;
    const dx=event.changedTouches[0].clientX-touchStart.x;
    const dy=event.changedTouches[0].clientY-touchStart.y;
    touchStart=null;
    if(Math.abs(dx)>55 && Math.abs(dx)>Math.abs(dy)*1.3)showPhoto(currentPhoto+(dx<0?1:-1));
  },{passive:true});

  // This small indicator is not a caption and requires no manual editing.
  if(galleryPhotos.length>3 && window.location.pathname.includes('/photos')){
    const gallery=document.querySelector('#main .page-content > .gallery');
    if(gallery){
      const info=document.createElement('div');
      info.className='photo-gallery-meta';
      const count=document.createElement('span');
      count.textContent=`${galleryPhotos.length} photographs`;
      const tip=document.createElement('span');
      tip.className='photo-gallery-tip';
      tip.textContent='Select any image to view full-screen';
      info.append(count,tip);
      gallery.insertAdjacentElement('beforebegin',info);
    }
  }
}

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
