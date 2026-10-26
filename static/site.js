'use strict';
// Remember Radar activation only for this tab's browsing session.
(()=>{
 const key='hmd-bioe-radar-visited';
 const stop=()=>document.documentElement.classList.add('lab-radar-visited');
 try{if(sessionStorage.getItem(key)==='1')stop();}catch{}
 const activate=event=>{
  if(!event.target.closest?.('a.lab-radar-link'))return;
  if(event.type==='auxclick'&&event.button!==1)return;
  stop();
  try{sessionStorage.setItem(key,'1');}catch{}
 };
 document.addEventListener('click',activate);
 document.addEventListener('auxclick',activate);
})();
document.querySelectorAll('details.member-publications').forEach(panel=>{
 panel.setAttribute('name','member-selected-publications');
 panel.addEventListener('toggle',()=>{if(panel.open)document.querySelectorAll('details.member-publications').forEach(other=>{if(other!==panel)other.open=false;});});
});
const toggle=document.querySelector('.lab-menu-toggle');
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));document.querySelector('#lab-navigation').classList.toggle('is-open',open)});
document.querySelectorAll('.lab-menu').forEach(menu=>{
 menu.addEventListener('toggle',()=>{if(menu.open)document.querySelectorAll('.lab-menu').forEach(other=>{if(other!==menu)other.open=false})});
 menu.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse')menu.open=true});
 menu.addEventListener('pointermove',event=>{if(event.pointerType==='mouse'&&!menu.open)menu.open=true});
 menu.addEventListener('pointerleave',event=>{if(event.pointerType==='mouse'&&!menu.querySelector(':focus-visible'))menu.open=false});
 menu.addEventListener('focusout',event=>{if(!menu.contains(event.relatedTarget)&&!menu.matches(':hover'))menu.open=false});
});
document.addEventListener('click',event=>{if(!event.target.closest('.lab-menu')&&!document.querySelector('.lab-menu:hover'))document.querySelectorAll('.lab-menu').forEach(menu=>menu.open=false)});
document.addEventListener('keydown',event=>{if(event.key==='Escape')document.querySelectorAll('.lab-menu').forEach(menu=>menu.open=false)});
document.querySelectorAll('.lab-carousel').forEach(carousel=>{
 const slides=[...carousel.querySelectorAll('.lab-carousel-slide')],dots=[...carousel.querySelectorAll('[data-slide]')],motion=matchMedia('(prefers-reduced-motion: reduce)');let index=0,timer;
 if(!slides.length)return;
 const show=next=>{index=(next+slides.length)%slides.length;slides.forEach((s,i)=>{s.hidden=false;s.classList.toggle('is-active',i===index);s.setAttribute('aria-hidden',String(i!==index));s.inert=i!==index});dots.forEach((dot,i)=>dot.setAttribute('aria-pressed',String(i===index)))};
 const restart=()=>{clearInterval(timer);if(!motion.matches)timer=setInterval(()=>{if(!document.hidden)show(index+1)},8000)};
 dots.forEach(dot=>dot.addEventListener('click',()=>{show(Number(dot.dataset.slide));restart()}));
 motion.addEventListener('change',restart);show(0);restart();
});
document.addEventListener('click',event=>{const a=event.target.closest('a[data-lightbox]');if(!a)return;event.preventDefault();const dialog=document.createElement('dialog');dialog.className='lab-lightbox'+(a.dataset.lightbox==='compact'?' lab-lightbox-compact':'');dialog.setAttribute('aria-label',a.getAttribute('aria-label')||'Image preview');const img=document.createElement('img');img.src=a.href;img.alt=a.querySelector('img')?.alt||a.getAttribute('aria-label')||'';const button=document.createElement('button');button.textContent='Close';button.addEventListener('click',()=>dialog.close());dialog.append(button,img);document.body.append(dialog);dialog.addEventListener('close',()=>{dialog.remove();a.focus()});dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});dialog.showModal();});

// A shared, keyboard-accessible return-to-top control for long pages.
(()=>{
 const button=document.createElement('button');
 button.type='button';button.className='lab-back-to-top';button.hidden=true;
 button.setAttribute('aria-label','Back to top');button.title='Back to top';
 button.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 12l6-6 6 6M12 6v13"/></svg>';
 document.body.append(button);
 const update=()=>{button.hidden=window.scrollY<Math.max(600,window.innerHeight*.8)};
 window.addEventListener('scroll',update,{passive:true});
 window.addEventListener('resize',update);update();
 button.addEventListener('click',()=>window.scrollTo({top:0,left:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
})();
