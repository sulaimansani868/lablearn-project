/* TUTORIAL LIST PANEL — open / close / current-page highlight
   Add this block to shared.js */
(function () {
  var btn      = document.getElementById('navTutBtn');
  var panel    = document.getElementById('tutListPanel');
  var overlay  = document.getElementById('tutListOverlay');
  var closeBtn = document.getElementById('tutListClose');
  if (!btn || !panel) return;   /* exits silently on non-tutorial pages */

  /* ── Highlight the current tutorial ── */
  var currentFile = window.location.pathname.split('/').pop() || 'index.html';
  panel.querySelectorAll('a[data-tut]').forEach(function (a) {
    if (a.getAttribute('href').split('/').pop() === currentFile) {
      a.classList.add('tut-list-current');
    }
  });

  function openPanel() {
    panel.classList.add('open');
    overlay.classList.add('open');
    btn.setAttribute('aria-expanded', 'true');
    panel.setAttribute('aria-hidden', 'false');
    var mob = document.getElementById('navMobile');
    if (mob && mob.classList.contains('open')) mob.classList.remove('open');
    var cur = panel.querySelector('.tut-list-current');
    if (cur) setTimeout(function () { cur.scrollIntoView({ block: 'center', behavior: 'smooth' }); }, 300);
  }

  function closePanel() {
    panel.classList.remove('open');
    overlay.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
    panel.setAttribute('aria-hidden', 'true');
  }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    panel.classList.contains('open') ? closePanel() : openPanel();
  });
  closeBtn.addEventListener('click', closePanel);
  overlay.addEventListener('click', closePanel);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel.classList.contains('open')) closePanel();
  });
  document.addEventListener('click', function (e) {
    if (panel.classList.contains('open') && !panel.contains(e.target) && e.target !== btn) closePanel();
  });
  panel.querySelectorAll('a[data-tut]').forEach(function (a) {
    a.addEventListener('click', closePanel);
  });
})();
