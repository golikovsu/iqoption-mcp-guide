/* IQ Option · AI Integrations — analytics (visits + on-site events)
 *
 * Privacy-first, cookieless, no consent banner required (Plausible).
 * Provider-agnostic: everything funnels through one track() shim, so the
 * provider can be swapped in ONE place. Fully decoupled from main.js and
 * safe to remove (delete this file + its <script> tag).
 *
 * Configured with the Plausible "pa-*" site script (the site is identified by
 * the script URL itself). To point at a different Plausible site, swap the URL
 * in CONFIG.plausibleScript. To turn analytics off, set CONFIG.provider = 'none'.
 */
(() => {
  'use strict';

  const CONFIG = {
    provider: 'plausible',          // 'plausible' | 'ga4' | 'umami' | 'none'
    plausibleScript: 'https://plausible.io/js/pa-xMQR3EgsY6R-w0NrpihxY.js',  // site-specific Plausible script
    // ga4Id: 'G-XXXXXXXXXX',
    // umami: { src: 'https://cloud.umami.is/script.js', websiteId: '' },
    respectDNT: false,              // set true to skip tracking when Do-Not-Track / GPC is on
    debug: false,                   // console.debug every event
  };

  const $$ = (s, c = document) => Array.from((c || document).querySelectorAll(s));

  // Always keep a local trail for debugging / inspection (no PII, in-memory only).
  window.__analytics = window.__analytics || [];

  const dnt =
    navigator.doNotTrack === '1' || window.doNotTrack === '1' ||
    navigator.msDoNotTrack === '1' || navigator.globalPrivacyControl === true;

  let send = () => {};   // becomes the real sender once a provider is configured

  function track(name, props) {
    window.__analytics.push([name, props || null]);
    if (CONFIG.debug) console.debug('[analytics]', name, props || '');
    try { send(name, props); } catch (e) { /* never let analytics break the page */ }
  }
  window.track = track;  // exposed for optional manual calls

  // ── provider bootstrap ──────────────────────────────────────────────
  function initProvider() {
    if (CONFIG.respectDNT && dnt) {
      if (CONFIG.debug) console.debug('[analytics] disabled: Do-Not-Track');
      return false;
    }
    if (CONFIG.provider === 'plausible') {
      if (!CONFIG.plausibleScript) {
        console.info('[analytics] Plausible script not set — events recorded to window.__analytics only.');
        return false;
      }
      const s = document.createElement('script');
      s.async = true;
      s.src = CONFIG.plausibleScript;
      document.head.appendChild(s);
      window.plausible = window.plausible || function () { (window.plausible.q = window.plausible.q || []).push(arguments); };
      window.plausible.init = window.plausible.init || function (i) { window.plausible.o = i || {}; };
      window.plausible.init();   // auto-tracks the pageview (one per page load, MPA)
      send = (name, props) => window.plausible(name, props ? { props } : undefined);
      return true;
    }
    if (CONFIG.provider === 'ga4' && CONFIG.ga4Id) {
      const s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.ga4Id;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', CONFIG.ga4Id);
      send = (name, props) => window.gtag('event', name, props || {});
      return true;
    }
    if (CONFIG.provider === 'umami' && CONFIG.umami && CONFIG.umami.websiteId) {
      const s = document.createElement('script');
      s.defer = true;
      s.src = CONFIG.umami.src;
      s.setAttribute('data-website-id', CONFIG.umami.websiteId);
      document.head.appendChild(s);
      send = (name, props) => window.umami && window.umami.track(name, props || {});
      return true;
    }
    return false;
  }

  initProvider();   // pageview is auto-tracked by the provider on script load (MPA = 1 per page)

  // ── on-site event layer (delegated, decoupled from main.js) ─────────
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const lang = document.documentElement.lang || 'en';

  document.addEventListener('click', (e) => {
    // Copy buttons → distinguish config vs server URL
    const copy = e.target.closest('.copy-btn');
    if (copy) {
      if (copy.hasAttribute('data-copy-code')) {
        const tab = document.querySelector('.picker-tabs .pt[aria-selected="true"]');
        track('Copy: Config', { assistant: tab ? tab.dataset.tab : 'unknown' });
      } else {
        const card = copy.closest('.srv-card');
        const name = card ? clean(card.querySelector('.srv-name')?.textContent) : (copy.dataset.copy || '');
        track('Copy: Server URL', { server: name.replace(/^▸\s*/, '') });
      }
      return;
    }
    // Assistant tab selection
    const tab = e.target.closest('.picker-tabs .pt');
    if (tab) { track('Select Assistant', { assistant: tab.dataset.tab }); return; }

    // Language switch
    const langLink = e.target.closest('.lang-menu a');
    if (langLink) {
      track('Switch Language', { from: lang, to: langLink.getAttribute('lang') || clean(langLink.textContent) });
      return;
    }

    // Primary CTAs (hero + step buttons)
    const cta = e.target.closest('.hero-cta .qeds-button, .step a.qeds-button');
    if (cta) { track('CTA: Click', { cta: clean(cta.textContent).replace(/\s*→$/, ''), lang }); return; }

    // Outbound links
    const link = e.target.closest('a[href^="http"]');
    if (link) {
      try {
        const u = new URL(link.href);
        if (u.host !== location.host) track('Outbound Link: Click', { url: u.host + u.pathname });
      } catch (_) { /* ignore */ }
    }
  }, true);

  // FAQ expand
  $$('.faq-item').forEach((d) => {
    d.addEventListener('toggle', () => {
      if (d.open) track('FAQ: Open', { q: clean(d.querySelector('summary')?.textContent).slice(0, 120) });
    });
  });

  // Scroll depth (25 / 50 / 75 / 100), each fired once
  const marks = [25, 50, 75, 100];
  const hit = new Set();
  let ticking = false;
  const checkDepth = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const pct = max > 0 ? ((h.scrollTop || document.body.scrollTop) / max) * 100 : 100;
    for (const m of marks) {
      if (pct >= m && !hit.has(m)) { hit.add(m); track('Scroll Depth', { percent: String(m) }); }
    }
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { window.requestAnimationFrame(checkDepth); ticking = true; }
  }, { passive: true });
})();
