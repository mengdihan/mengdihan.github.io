document.querySelectorAll('.member-gallery').forEach(gallery => {
  const slides = [...gallery.querySelectorAll('.member-gallery-slide')];
  const thumbs = [...gallery.querySelectorAll('[data-gallery-index]')];
  const controls = gallery.querySelector('.member-gallery-controls');
  const count = gallery.querySelector('.member-gallery-count');
  if (!slides.length || !controls || !count) return;
  const windowSize = Math.min(3, slides.length);
  let first = 0;
  function show(index) {
    first = Math.max(0, Math.min(index, slides.length - windowSize));
    slides.forEach((slide, i) => { slide.hidden = i < first || i >= first + windowSize; });
    thumbs.forEach((thumb, i) => {
      if (i >= first && i < first + windowSize) thumb.setAttribute('aria-current', 'true');
      else thumb.removeAttribute('aria-current');
    });
    count.textContent = `${first + 1}–${first + windowSize} / ${slides.length}`;
    controls.querySelector('[data-gallery-action="previous"]').disabled = first === 0;
    controls.querySelector('[data-gallery-action="next"]').disabled = first === slides.length - windowSize;
  }
  thumbs.forEach((thumb, i) => thumb.addEventListener('click', event => {
    event.preventDefault();
    show(i < first ? i : i >= first + windowSize ? i - windowSize + 1 : first);
  }));
  controls.querySelector('[data-gallery-action="previous"]').addEventListener('click', () => show(first - 1));
  controls.querySelector('[data-gallery-action="next"]').addEventListener('click', () => show(first + 1));
  gallery.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); show(first + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  show(0); controls.hidden = slides.length <= windowSize; gallery.classList.add('gallery-ready');
});
