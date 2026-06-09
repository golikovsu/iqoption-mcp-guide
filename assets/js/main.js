/* IQ Option · AI Integrations — progressive-enhancement interactions
 * Vanilla JS, no dependencies. All ARIA wiring is applied here so the markup
 * stays clean and the page degrades gracefully without JS. */
(() => {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $  = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ── Decorative icons: remove from the accessibility tree ───────────── */
  $$('.cap-ic, .info-ic, .pb-test-ic, .perm-head-ic, .safety-ic, .badge-dot, .step-num')
    .forEach(el => el.setAttribute('aria-hidden', 'true'));

  /* ── Tabs: WAI-ARIA tablist + roving tabindex + arrow-key navigation ── */
  const tablist = $('.picker-tabs');
  if (tablist) {
    const tabs   = $$('.pt', tablist);
    const panels = $$('.pb-tab');
    tablist.setAttribute('role', 'tablist');
    tablist.setAttribute('aria-label', 'AI assistant configurations');

    tabs.forEach(tab => {
      const key      = tab.dataset.tab;
      const panel    = panels.find(p => p.dataset.tab === key);
      const selected = tab.classList.contains('active');
      const diff     = $('.pt-diff', tab)?.textContent.trim();
      // Clean accessible name: strip emoji + difficulty chip.
      const name = tab.textContent.replace(diff || '', '')
        .replace(/[\u{1F000}-\u{1FAFF}←-➿️‍]/gu, '').trim();

      tab.id = `tab-${key}`;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-selected', selected ? 'true' : 'false');
      tab.setAttribute('aria-controls', `panel-${key}`);
      tab.setAttribute('tabindex', selected ? '0' : '-1');
      tab.setAttribute('aria-label', diff ? `${name} — ${diff} setup` : name);

      if (panel) {
        panel.id = `panel-${key}`;
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', `tab-${key}`);
        panel.setAttribute('tabindex', '0');
      }
    });

    const activate = (tab, focus) => {
      tabs.forEach(t => {
        const on = t === tab;
        t.classList.toggle('active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.setAttribute('tabindex', on ? '0' : '-1');
      });
      panels.forEach(p => p.classList.toggle('active', p.dataset.tab === tab.dataset.tab));
      if (focus) tab.focus();
    };

    tablist.addEventListener('click', e => {
      const tab = e.target.closest('.pt');
      if (tab) activate(tab, false);
    });

    tablist.addEventListener('keydown', e => {
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      let next = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (i + 1) % tabs.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (i - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') next = 0;
      else if (e.key === 'End') next = tabs.length - 1;
      if (next !== null) { e.preventDefault(); activate(tabs[next], true); }
    });
  }

  /* ── Permission rows: real checkbox semantics on the QEDS buttons ───── */
  $$('.qeds-checkbox').forEach(cb => {
    cb.setAttribute('role', 'checkbox');
    cb.setAttribute('aria-checked', cb.dataset.checked === 'checked' ? 'true' : 'false');
    const label = $('.qeds-checkbox__label', cb)?.textContent.trim();
    if (label) cb.setAttribute('aria-label', label);
    if (cb.disabled) { cb.setAttribute('aria-disabled', 'true'); return; }
    // <button> already fires click on Space/Enter — no extra key handler needed.
    cb.addEventListener('click', () => {
      const next = cb.dataset.checked === 'checked' ? 'unchecked' : 'checked';
      cb.dataset.checked = next;
      cb.setAttribute('aria-checked', next === 'checked' ? 'true' : 'false');
    });
  });

  /* ── Copy-to-clipboard with live-region feedback + execCommand fallback ─ */
  const toast = $('#toast');
  let toastTimer;
  const announce = msg => {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 1900);
  };

  const copyText = async text => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch { /* noop */ }
      document.body.removeChild(ta);
      return ok;
    }
  };

  $$('.copy-btn').forEach(btn => {
    if (!btn.getAttribute('aria-label')) {
      btn.setAttribute('aria-label', btn.dataset.copy ? 'Copy to clipboard' : 'Copy code to clipboard');
    }
    btn.addEventListener('click', async () => {
      let text = btn.dataset.copy;
      if (!text && btn.hasAttribute('data-copy-code')) {
        text = $('pre', btn.closest('.code-block'))?.innerText || '';
      }
      if (!text) return;
      const ok = await copyText(text);
      if (!ok) { announce('Copy failed — select the text manually'); return; }
      const original = btn.innerHTML;
      btn.innerHTML = '✓ Copied';
      btn.classList.add('copied');
      announce('Copied to clipboard');
      setTimeout(() => { btn.innerHTML = original; btn.classList.remove('copied'); }, 1500);
    });
  });

  /* ── Reveal-on-scroll (honors prefers-reduced-motion) ───────────────── */
  const revealEls = $$('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealEls.forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(el => io.observe(el));
  }

  /* ── Scroll progress bar + back-to-top (injected, non-essential chrome) ─ */
  const progress = document.createElement('div');
  progress.className = 'scroll-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.appendChild(progress);

  const toTop = document.createElement('button');
  toTop.type = 'button';
  toTop.className = 'to-top';
  toTop.setAttribute('aria-label', 'Back to top');
  toTop.innerHTML = '<span aria-hidden="true">↑</span>';
  toTop.addEventListener('click', () =>
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }));
  document.body.appendChild(toTop);

  let ticking = false;
  const onScroll = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const pct = max > 0 ? (h.scrollTop || document.body.scrollTop) / max : 0;
    progress.style.transform = `scaleX(${pct})`;
    toTop.classList.toggle('show', (h.scrollTop || document.body.scrollTop) > 600);
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  /* ── Language switcher dropdown ─────────────────────────────────────── */
  const langSwitch = $('.lang-switch');
  if (langSwitch) {
    const toggle = $('.lang-toggle', langSwitch);
    const menu = $('.lang-menu', langSwitch);
    const open = () => { menu.hidden = false; toggle.setAttribute('aria-expanded', 'true'); };
    const close = () => { menu.hidden = true; toggle.setAttribute('aria-expanded', 'false'); };
    toggle.addEventListener('click', e => {
      e.stopPropagation();
      menu.hidden ? open() : close();
    });
    document.addEventListener('click', e => { if (!langSwitch.contains(e.target)) close(); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !menu.hidden) { close(); toggle.focus(); }
    });
  }

  /* ── Mobile nav (hamburger → dropdown of section anchors) ───────────── */
  const nav = $('.nav');
  const navToggle = $('.nav-toggle');
  const navLinks = $('#nav-links');
  if (nav && navToggle) {
    const closeNav = () => { nav.classList.remove('nav-open'); navToggle.setAttribute('aria-expanded', 'false'); };
    navToggle.addEventListener('click', e => {
      e.stopPropagation();
      const open = nav.classList.toggle('nav-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navLinks?.addEventListener('click', e => { if (e.target.closest('a')) closeNav(); });
    document.addEventListener('click', e => { if (!nav.contains(e.target)) closeNav(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNav(); });
  }
})();
