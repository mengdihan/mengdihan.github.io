'use strict';
const toggle=document.querySelector('.lab-menu-toggle');
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));document.querySelector('#lab-navigation').classList.toggle('is-open',open)});
document.querySelectorAll('.lab-menu').forEach(menu=>menu.addEventListener('toggle',()=>{if(menu.open)document.querySelectorAll('.lab-menu').forEach(other=>{if(other!==menu)other.open=false})}));
document.addEventListener('click',event=>{if(!event.target.closest('.lab-menu'))document.querySelectorAll('.lab-menu').forEach(menu=>menu.open=false)});
document.addEventListener('keydown',event=>{if(event.key==='Escape')document.querySelectorAll('.lab-menu').forEach(menu=>menu.open=false)});
document.querySelectorAll('.lab-carousel').forEach(carousel=>{
 const slides=[...carousel.querySelectorAll('.lab-carousel-slide')];let index=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const show=next=>{index=(next+slides.length)%slides.length;slides.forEach((s,i)=>s.hidden=i!==index)};
 carousel.querySelectorAll('[data-direction]').forEach(b=>b.addEventListener('click',()=>show(index+Number(b.dataset.direction))));
 const pause=carousel.querySelector('.lab-pause');const paint=()=>{pause.textContent=paused?'Play':'Pause';pause.setAttribute('aria-label',paused?'Play slideshow':'Pause slideshow')};
 pause.addEventListener('click',()=>{paused=!paused;paint()});paint();
 setInterval(()=>{if(!paused&&!document.hidden&&!carousel.matches(':hover')&&!carousel.contains(document.activeElement))show(index+1)},12000);
});
document.addEventListener('click',event=>{const a=event.target.closest('a[data-lightbox]');if(!a)return;event.preventDefault();const dialog=document.createElement('dialog');dialog.className='lab-lightbox';const img=document.createElement('img');img.src=a.href;img.alt=a.querySelector('img')?.alt||'';const button=document.createElement('button');button.textContent='Close';button.addEventListener('click',()=>dialog.close());dialog.append(button,img);document.body.append(dialog);dialog.addEventListener('close',()=>{dialog.remove();a.focus()});dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});dialog.showModal();});
