/* ============================================================
   PORTFOLIO — Main JavaScript
   Handles: scroll effects, nav, hero transitions, animations
   ============================================================ */

(function () {
  'use strict';

  // ── Utility ──
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  // ── Progress bar ──
  const progressBar = $('#page-progress');
  function updateProgress() {
    if (!progressBar) return;
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    progressBar.style.width = total > 0 ? (scrolled / total * 100) + '%' : '0%';
  }

  // ── Navbar scroll ──
  const navbar = $('#navbar');
  function updateNavbar() {
    if (!navbar) return;
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }

  // ── Hamburger ──
  const hamburger = $('#hamburger');
  const navLinks  = $('#nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      navLinks.classList.toggle('open');
    });
    // Close on nav link click
    $$('.nav-link', navLinks).forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        navLinks.classList.remove('open');
      });
    });
  }

  // ── Smooth scroll for Contact buttons ──
  function initContactScroll() {
    $$('.contact-scroll-btn, [href="#contact-section"]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        const target = document.getElementById('contact-section');
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ── Home Page scroll behaviour ──
  //
  // State A (scrollY === 0):
  //   - Image visible on right
  //   - Heading on left, body text invisible
  //
  // The instant scrollY > 0:
  //   - Image fades + slides right (proportional to scroll)
  //   - Text column shifts toward centre (proportional to scroll)
  //   - Scroll hint disappears
  //
  // Once image is fully gone (scrollY >= TRAVEL):
  //   - Body text fades in
  //   - Page continues scrolling normally below the sticky block
  //
  function initHomeScrollEffects() {
    const imageCol  = document.getElementById('home-image-col');
    const textCol   = document.getElementById('home-text-col');
    const bodyText  = document.getElementById('home-body-text');
    const scrollHint = document.getElementById('home-scroll-hint');
    // If there's no image, nothing to animate
    if (!imageCol || !textCol) return;

    // How many px of scroll until the image is fully gone & text is centred
    const TRAVEL = window.innerHeight * 0.3;

    // Measure how far right the text column needs to shift to be visually centred.
    // We calculate this lazily on first scroll so layout is settled.
    let centreShift = null;
    function getCentreShift() {
      if (centreShift !== null) return centreShift;
      const sceneRect   = textCol.parentElement.getBoundingClientRect();
      const textRect    = textCol.getBoundingClientRect();
      // current left edge of text column relative to scene
      const currentLeft = textRect.left - sceneRect.left;
      // where left edge should be so the column is centred in scene
      const targetLeft  = (sceneRect.width - textRect.width) / 2;
      centreShift = targetLeft - currentLeft;
      return centreShift;
    }

    let bodyRevealed = false;

    function onScroll() {
      const scrollY = window.scrollY;
      const p = Math.min(scrollY / TRAVEL, 1); // 0 → 1

      // ── Image: fade out + slide right immediately ──
      /*imageCol.style.opacity   = 1 - p;
      imageCol.style.transform = `translateX(${p * 80}px)`;*/

      // ── Text column: slide toward centre ──
      /*const shift = getCentreShift();
      textCol.style.transform = `translateX(${p * shift}px)`;*/

      // ── Scroll hint: hide immediately ──
      if (scrollHint) scrollHint.style.opacity = Math.max(1 - p * 3, 0);

      // ── Body text: fade in only after image is fully gone ──
      //if (p >= 1 && !bodyRevealed)
      if (true) {
        bodyRevealed = true;
        // Small delay then CSS transition kicks in
        bodyText.style.transition = 'opacity 0.6s ease, transform 0.6s cubic-bezier(0.16,1,0.3,1)';
        bodyText.style.transform  = 'translateY(0)';
        bodyText.style.opacity    = '1';
      } else if (p < 1 && bodyRevealed) {
        bodyRevealed = false;
        bodyText.style.transition = '';
        bodyText.style.opacity    = '0';
        bodyText.style.transform  = 'translateY(16px)';
      }
    }

    // Set initial hidden state for body text
    bodyText.style.transform = 'translateY(16px)';

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Intersection Observer: animate content blocks ──
  function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const delay = (el.dataset.index || 0) * 0;
          setTimeout(() => el.classList.add('in-view'), delay);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

    $$('.content-block').forEach(el => observer.observe(el));
  }

  // ── Contact cards stagger animation ──
  function initContactAnimations() {
    const contactCards = $$('.contact-card');
    if (!contactCards.length) return;

    const observer = new IntersectionObserver((entries) => {
      if (entries.some(e => e.isIntersecting)) {
        contactCards.forEach((card, i) => {
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, i * 60);
        });
        observer.disconnect();
      }
    }, { threshold: 0.1 });

    contactCards.forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = 'opacity 0.5s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1), border-color 0.25s ease, box-shadow 0.25s ease';
    });

    const contactSection = $('#contact-section');
    if (contactSection) observer.observe(contactSection);
  }

  // ── Tab page header animation ──
  function initTabPageAnimations() {
    const header = $('.tab-page-header');
    if (!header) return;
    const title = $('.tab-page-title');
    const underline = $('.tab-title-underline');
    const breadcrumb = $('.tab-breadcrumb');

    [breadcrumb, title, underline].forEach((el, i) => {
      if (!el) return;
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = `opacity 0.7s ease, transform 0.7s cubic-bezier(0.16,1,0.3,1)`;
      setTimeout(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, 100 + i * 120);
    });
  }

  // ── CV: enhance typography ──
  function initCVPage() {
    const cvContent = $('.cv-content');
    if (!cvContent) return;
    // Already rendered, just ensure links open in new tab
    $$('a', cvContent).forEach(a => a.setAttribute('target', '_blank'));
  }

  // ── Cursor glow effect (desktop only) ──
  function initCursorGlow() {
    if (window.matchMedia('(hover: none)').matches) return;
    const glow = document.createElement('div');
    glow.style.cssText = `
      position: fixed; pointer-events: none; z-index: 9990;
      width: 300px; height: 300px; border-radius: 50%;
      background: radial-gradient(circle, rgba(201,168,76,0.1) 0%, transparent 70%);
      transform: translate(-50%, -50%);
      transition: opacity 0.3s ease;
      top: -999px; left: -999px;
    `;
    document.body.appendChild(glow);

    let active = false;
    document.addEventListener('mousemove', e => {
      glow.style.left = e.clientX + 'px';
      glow.style.top  = e.clientY + 'px';
      if (!active) { glow.style.opacity = '1'; active = true; }
    });
    document.addEventListener('mouseleave', () => {
      glow.style.opacity = '0';
      active = false;
    });
  }

  // ── Scroll listener ──
  window.addEventListener('scroll', () => {
    updateProgress();
    updateNavbar();
  }, { passive: true });

  // ── Init ──
  document.addEventListener('DOMContentLoaded', () => {
    updateNavbar();
    updateProgress();
    initContactScroll();
    initHomeScrollEffects();
    initScrollAnimations();
    initContactAnimations();
    initTabPageAnimations();
    initCVPage();
    initCursorGlow();

    // Add transition class to body after load (prevents flash)
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.4s ease';
        document.body.style.opacity = '1';
      });
    });
  });
})();
