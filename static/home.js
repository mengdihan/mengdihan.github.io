/* HOME: crossfade, dot navigation, and automatic rotation. */
(() => {
  'use strict';
  const carousel = document.querySelector('.home-carousel');
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll('.home-slide')];
  const dots = [...carousel.querySelectorAll('[data-slide]')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let timer;
  let hovering = false;
  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const active = i === current;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      slide.querySelectorAll('a').forEach(link => { link.tabIndex = active ? 0 : -1; });
      dots[i].setAttribute('aria-current', String(active));
      if (active) slide.querySelector('img').loading = 'eager';
    });
  }
  function schedule() {
    clearInterval(timer);
    if (!reduced.matches && !document.hidden && !hovering && !carousel.contains(document.activeElement)) {
      timer = setInterval(() => show(current + 1), 4000);
    }
  }
  dots.forEach((dot, index) => dot.addEventListener('click', () => { show(index); schedule(); }));
  carousel.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    show(current + (event.key === 'ArrowRight' ? 1 : -1));
    schedule();
  });
  carousel.addEventListener('mouseenter', () => { hovering = true; schedule(); });
  carousel.addEventListener('mouseleave', () => { hovering = false; schedule(); });
  carousel.addEventListener('focusin', schedule);
  carousel.addEventListener('focusout', () => setTimeout(schedule, 0));
  document.addEventListener('visibilitychange', schedule);
  reduced.addEventListener('change', schedule);
  schedule();
})();
