/* The research gallery is manual: no timers, no unexpected movement. */
(() => {
  'use strict';
  document.querySelectorAll('.rd-carousel').forEach(carousel => {
    const slides = [...carousel.querySelectorAll('.rd-slide')];
    const controls = carousel.querySelector('.rd-carousel-controls');
    if (slides.length < 2) return;
    let current = 0;
    controls.hidden = false;
    function show(next) {
      current = (next + slides.length) % slides.length;
      slides.forEach((slide, index) => { slide.hidden = index !== current; });
      controls.querySelector('.rd-slide-count').textContent = `${current + 1} / ${slides.length}`;
    }
    controls.querySelectorAll('button').forEach(button => {
      button.addEventListener('click', () => show(current + Number(button.dataset.direction)));
    });
    carousel.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1));
    });
  });
})();
