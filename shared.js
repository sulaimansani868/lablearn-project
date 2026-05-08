/*
 * LabLearn — shared.js */

(function () {
  'use strict';

  function initMobileNav() {
    var burger = document.getElementById('navBurger');
    var mob    = document.getElementById('navMobile');

    /* If either element is missing on this page, do nothing */
    if (!burger || !mob) return;

    function openNav() {
      mob.classList.add('open');
      burger.classList.add('open');
      burger.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden'; /* prevent background scroll */
    }

    function closeNav() {
      mob.classList.remove('open');
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    function toggleNav() {
      mob.classList.contains('open') ? closeNav() : openNav();
    }

    /* Set initial aria state */
    burger.setAttribute('aria-expanded', 'false');

    /* Burger tap → toggle menu */
    burger.addEventListener('click', toggleNav);

    /* Tapping any link inside the mobile menu → close menu */
    mob.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeNav);
    });

    /* Pressing Escape key → close menu */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeNav();
    });

    /* Tapping outside the menu panel content → close */
    document.addEventListener('click', function (e) {
      if (
        mob.classList.contains('open') &&
        !mob.contains(e.target) &&
        !burger.contains(e.target)
      ) {
        closeNav();
      }
    });
  }

  function initComingSoon() {
    var overlay  = document.getElementById('csOverlay');
    var pageSpan = document.getElementById('csPageName');
    var closeBtn = document.getElementById('csClose');

    /* Only run on pages that have the dialog */
    if (!overlay || !pageSpan || !closeBtn) return;

    function openCS(label) {
      pageSpan.textContent = label || 'this page';
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }

    function closeCS() {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }

    /* "Got it" button */
    closeBtn.addEventListener('click', closeCS);

    /* Click on dark backdrop */
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeCS();
    });

    /* Escape key */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeCS();
    });

    /* Intercept ALL clicks on [data-cs] elements anywhere on the page */
    document.addEventListener('click', function (e) {
      var el = e.target.closest('[data-cs]');
      if (!el) return;
      e.preventDefault();
      openCS(el.dataset.cs);
    });
  }

  function initFaqAccordion() {
    var questions = document.querySelectorAll('.faq-q');
    if (!questions.length) return;

    questions.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item   = btn.closest('.faq-item');
        var isOpen = item.classList.contains('open');
        /* Close all items first */
        document.querySelectorAll('.faq-item').forEach(function (i) {
          i.classList.remove('open');
        });
        /* Re-open clicked item if it was closed */
        if (!isOpen) item.classList.add('open');
      });
    });
  }

  function initScrollReveal() {
    var elements = document.querySelectorAll('.reveal, .reveal-grid');
    if (!elements.length) return;

    /* IntersectionObserver is supported in all modern browsers */
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target); /* animate once then stop watching */
        }
      });
    }, { threshold: 0.1 });

    elements.forEach(function (el) { observer.observe(el); });
  }

  function initTocHighlight() {
    /* Only run on pages that have a TOC sidebar */
    var tocLinks = document.querySelectorAll('.toc-list a');
    if (!tocLinks.length) return;

    /* Collect all headings on the page that have an id */
    var headings = document.querySelectorAll('.article h2[id], .article h3[id]');
    if (!headings.length) return;

    function setActive(id) {
      /* Remove .active from all TOC links */
      tocLinks.forEach(function (link) {
        link.classList.remove('active');
      });
      /* Add .active to the link whose href matches the heading id */
      var activeLink = document.querySelector('.toc-list a[href="#' + id + '"]');
      if (activeLink) activeLink.classList.add('active');
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setActive(entry.target.id);
        }
      });
    }, { rootMargin: '-10% 0px -80% 0px' });

    headings.forEach(function (h) { observer.observe(h); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initMobileNav();
    initComingSoon();
    initFaqAccordion();
    initScrollReveal();
    initTocHighlight();
    initMobileToc();
  });

  function initMobileToc() {
    var btn      = document.getElementById('mobTocBtn');
    var panel    = document.getElementById('mobTocPanel');
    var overlay  = document.getElementById('mobTocOverlay');
    var closeBtn = document.getElementById('mobTocClose');
    if (!btn || !panel) return;

    function openPanel() {
      panel.classList.add('open');
      if (overlay) overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      btn.setAttribute('aria-expanded', 'true');
    }
    function closePanel() {
      panel.classList.remove('open');
      if (overlay) overlay.classList.remove('open');
      document.body.style.overflow = '';
      btn.setAttribute('aria-expanded', 'false');
    }

    btn.addEventListener('click', function () {
      panel.classList.contains('open') ? closePanel() : openPanel();
    });
    if (closeBtn) closeBtn.addEventListener('click', closePanel);
    if (overlay)  overlay.addEventListener('click', closePanel);

    /* Close and scroll when a TOC link is tapped */
    panel.querySelectorAll('.toc-list a').forEach(function (link) {
      link.addEventListener('click', closePanel);
    });

    /* Escape key closes panel */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closePanel();
    });
  }

})(); /* end IIFE — keeps all variables private, no global pollution */

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

(function () {
  var panel = document.getElementById('tutListPanel');
  if (!panel) return;

  var resizeTimer;
  window.addEventListener('resize', function () {
    panel.classList.add('resizing');
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      panel.classList.remove('resizing');
    }, 150);
  });
})();

(function () {
  var btn     = document.querySelector('.mob-toc-btn');
  var sidebar = document.querySelector('.toc-sidebar');
  var footer  = document.querySelector('footer');
  if (!btn || !sidebar || !footer) return;

  var sidebarVisible = false;
  var footerVisible  = false;

  function update() {
    /* Button should show only when sidebar is gone AND footer is not yet visible */
    if (sidebarVisible || footerVisible) {
      btn.classList.add('mob-toc-hidden');
    } else {
      btn.classList.remove('mob-toc-hidden');
    }
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.target === sidebar) sidebarVisible = entry.isIntersecting;
      if (entry.target === footer)  footerVisible  = entry.isIntersecting;
    });
    update();
  }, {
    threshold: 0.05   /* triggers when 5% of the element enters or leaves */
  });

  observer.observe(sidebar);
  observer.observe(footer);

  /* Start hidden if sidebar is already in view on load */
  btn.classList.add('mob-toc-hidden');
})();