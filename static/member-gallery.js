document.querySelectorAll('.member-gallery').forEach(gallery => {
  const slides = [...gallery.querySelectorAll('.member-gallery-slide')];
  const thumbs = [...gallery.querySelectorAll('[data-gallery-index]')];
  const controls = gallery.querySelector('.member-gallery-controls');
  const count = gallery.querySelector('.member-gallery-count');
  if (!slides.length || !controls || !count) return;
  let active = 0;
  function show(index) {
    active = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== active; });
    thumbs.forEach((thumb, i) => {
      if (i === active) thumb.setAttribute('aria-current', 'true');
      else thumb.removeAttribute('aria-current');
    });
    count.textContent = `${active + 1} / ${slides.length}`;
  }
  thumbs.forEach((thumb, i) => thumb.addEventListener('click', event => {
    event.preventDefault(); show(i);
  }));
  controls.querySelector('[data-gallery-action="previous"]').addEventListener('click', () => show(active - 1));
  controls.querySelector('[data-gallery-action="next"]').addEventListener('click', () => show(active + 1));
  gallery.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); show(active + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  show(0); controls.hidden = false; gallery.classList.add('gallery-ready');
});
