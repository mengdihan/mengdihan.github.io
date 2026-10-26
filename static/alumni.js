document.querySelectorAll('button.alumni-publications-toggle[aria-controls]').forEach((button) => {
  button.addEventListener('click', () => {
    const panel = document.getElementById(button.getAttribute('aria-controls'));
    if (!panel) return;
    const expanded = button.getAttribute('aria-expanded') !== 'true';
    if (expanded) document.querySelectorAll('button.alumni-publications-toggle[aria-controls]').forEach(other => {
      if (other === button) return;
      other.setAttribute('aria-expanded', 'false');
      const otherPanel = document.getElementById(other.getAttribute('aria-controls'));
      if (otherPanel) otherPanel.hidden = true;
    });
    button.setAttribute('aria-expanded', String(expanded));
    panel.hidden = !expanded;
  });
});
