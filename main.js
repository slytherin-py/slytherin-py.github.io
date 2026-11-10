(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  // ---- Mobile menu ----
  const nav = $('#nav');
  const menuBtn = $('#menu-btn');
  if (nav && menuBtn) {
    const setMenu = (open) => {
      nav.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    menuBtn.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
    $$('#nav-links a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });
  }

  // ---- Count-up numbers ----
  const countUp = (el) => {
    const target = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const suffix = el.dataset.suffix || '';
    const fmt = (v) => v.toFixed(decimals) + suffix;
    if (reduceMotion) { el.textContent = fmt(target); return; }
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / 1400);
      el.textContent = fmt(target * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  // ---- Hero headline: split into words so they arrive one after another ----
  const heroTitle = $('.hero h1');
  if (heroTitle && !reduceMotion) {
    let i = 0;
    const wrap = (node) => {
      if (node.nodeType === 3) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const w = document.createElement('span');
          w.className = 'w'; w.style.setProperty('--i', i++); w.textContent = part;
          frag.appendChild(w);
        });
        node.replaceWith(frag);
      } else if (node.classList && node.classList.contains('gradient-text')) {
        // background-clip text can't reach into transformed children, so the gradient phrase moves as one
        node.classList.add('w'); node.style.setProperty('--i', i++);
      }
    };
    Array.from(heroTitle.childNodes).forEach(wrap);
    heroTitle.classList.add('words');
  }

  // ---- Reveal on scroll ----
  // Elements that arrive together stagger (60ms apart, capped); once settled, the reveal
  // class comes off so hover and press styles apply and no blur layer lingers.
  const settle = (el) => {
    const d = parseFloat(getComputedStyle(el).getPropertyValue('--d')) || 0;
    setTimeout(() => el.classList.remove('reveal'), 1700 + d * 1000);
  };
  const io = new IntersectionObserver((entries) => {
    const arriving = entries.filter((en) => en.isIntersecting).map((en) => en.target);
    arriving.forEach((el, n) => {
      if (arriving.length > 1 && !el.closest('.hero')) el.style.setProperty('--d', Math.min(n, 5) * 0.06 + 's');
      el.classList.add('in');
      $$('[data-count]', el).forEach(countUp);
      if (el.classList.contains('reveal')) settle(el);
      io.unobserve(el);
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
  $$('.reveal, [data-observe]').forEach((el) => io.observe(el));

  // ---- Hub-network schematic: population dots + hubs (any number per page) ----
  const svgNS = 'http://www.w3.org/2000/svg';
  const hubs = [[150, 150], [300, 118], [470, 130], [540, 255], [400, 300], [250, 290], [110, 280]];
  const R = 58;
  $$('svg.hub-map').forEach((svg) => {
    const pop = $('.pop', svg);
    const hubG = $('.hubs', svg);
    if (!pop || !hubG || pop.childElementCount) return;
    let seed = 7;
    const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const frag = document.createDocumentFragment();
    for (let x = 40; x < 620; x += 14) {
      for (let y = 40; y < 400; y += 14) {
        const jx = x + (rand() - .5) * 8;
        const jy = y + (rand() - .5) * 8;
        const covered = hubs.some(([hx, hy]) => Math.hypot(jx - hx, jy - hy) < R);
        const c = document.createElementNS(svgNS, 'circle');
        c.setAttribute('cx', jx.toFixed(1));
        c.setAttribute('cy', jy.toFixed(1));
        c.setAttribute('r', (1.1 + rand() * 1.2).toFixed(2));
        c.setAttribute('fill', covered ? '#9cc9ff' : '#3a3a3e');
        frag.appendChild(c);
      }
    }
    pop.appendChild(frag);
    hubs.forEach(([x, y], i) => {
      hubG.insertAdjacentHTML('beforeend',
        `<circle cx="${x}" cy="${y}" r="${R}" fill="url(#hubFill)" stroke="#2997ff" stroke-opacity=".45" stroke-width="1"/>` +
        `<circle class="hub-ring" style="animation-delay:${(i * 0.45).toFixed(2)}s" cx="${x}" cy="${y}" r="${R * 0.7}" fill="none" stroke="#2997ff" stroke-width="1.5"/>` +
        `<circle cx="${x}" cy="${y}" r="6" fill="#fff" stroke="#2997ff" stroke-width="2.5"/>`);
    });
  });

  // ---- Lightbox for case-study images ----
  const zoomables = $$('[data-zoom]');
  if (zoomables.length && typeof HTMLDialogElement === 'function') {
    const dlg = document.createElement('dialog');
    dlg.className = 'lightbox';
    dlg.innerHTML = '<button class="lightbox-close" aria-label="Close image">×</button><img alt="">';
    document.body.appendChild(dlg);
    const big = $('img', dlg);
    zoomables.forEach((img) => {
      img.tabIndex = 0;
      img.setAttribute('role', 'button');
      img.setAttribute('aria-label', 'Enlarge image: ' + img.alt);
      const open = () => { big.src = img.dataset.zoom; big.alt = img.alt; dlg.showModal(); };
      img.addEventListener('click', open);
      img.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    });
    dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.closest('.lightbox-close')) dlg.close(); });
  }

  // ---- Hero portrait parallax + mobile hire bar ----
  const heroVisual = $('#hero-visual');
  const hireBar = $('#hire-bar');
  const contact = $('#contact');
  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY;
    if (heroVisual && !reduceMotion && y < window.innerHeight * 1.5) {
      const p = Math.min(1, y / window.innerHeight);
      heroVisual.style.transform = `translateY(${p * -40}px) scale(${1 + p * 0.06})`;
    }
    if (hireBar && contact) {
      const contactTop = contact.getBoundingClientRect().top;
      hireBar.classList.toggle('show', y > window.innerHeight * 0.9 && contactTop > window.innerHeight * 0.6);
    }
    ticking = false;
  };
  window.addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  onScroll();

  // ---- Active section in nav (homepage) ----
  const links = $$('#nav-links a').filter((a) => a.getAttribute('href').startsWith('#'));
  if (links.length) {
    const sectionIO = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((a) => {
          if (a.getAttribute('href') === '#' + en.target.id) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach((a) => { const s = $(a.getAttribute('href')); if (s) sectionIO.observe(s); });
  }

  // ---- Nav glass: a pill glides to the hovered link, else the current one; glare follows the pointer ----
  const navLinks = $('#nav-links');
  if (nav && navLinks) {
    const pill = document.createElement('span');
    pill.className = 'nav-pill'; pill.setAttribute('aria-hidden', 'true');
    navLinks.prepend(pill);
    const place = (a) => {
      if (!a) { pill.style.setProperty('--po', 0); return; }
      pill.style.setProperty('--px', a.offsetLeft + 'px');
      pill.style.setProperty('--pw', a.offsetWidth + 'px');
      pill.style.setProperty('--po', 1);
    };
    const current = () => place($('a[aria-current="true"]', navLinks));
    $$('a', navLinks).forEach((a) => a.addEventListener('pointerenter', () => place(a)));
    navLinks.addEventListener('pointerleave', current);
    new MutationObserver(current).observe(navLinks, { subtree: true, attributeFilter: ['aria-current'] });
    const inner = $('.nav-inner', nav);
    inner.addEventListener('pointermove', (ev) => {
      const r = inner.getBoundingClientRect();
      inner.style.setProperty('--gx', (ev.clientX - r.left) + 'px');
    }, { passive: true });
    const scrolled = () => nav.classList.toggle('scrolled', window.scrollY > 40);
    window.addEventListener('scroll', scrolled, { passive: true }); scrolled();
  }

  // ---- Contact form → prefilled email ----
  const form = $('#contact-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = form.name.value.trim();
      const message = form.message.value.trim();
      if (!name || !message) {
        const bad = name ? form.message : form.name;
        bad.setAttribute('aria-invalid', 'true');
        bad.focus();
        return;
      }
      const company = form.company.value.trim();
      const subject = `Opportunity for Mohammed${company ? ' · ' + company : ''}`;
      const body = `${message}\n\n${name}${company ? '\n' + company : ''}`;
      window.location.href = `mailto:mohammedsaleeqs@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  }

  // ---- Hero: the full-screen portrait glides into a card while the headline arrives ----
  const dive = $('.dive');
  const face = dive && $('.dive-face img', dive);
  if (dive && face && !reduceMotion) {
    dive.classList.add('is-dive');
    const stage = $('.dive-stage', dive);
    const scene = $('.dive-scene', dive);
    const IMG = { w: 1100, h: 1525, focusX: 0.5, focusY: 0.34 };   // portrait.jpg; focus sits on the face
    const clamp = (v) => Math.min(1, Math.max(0, v));
    const ease = (t) => 1 - Math.pow(1 - t, 3);                      // ease-out: settles into place
    const mix = (a, b, t) => a + (b - a) * t;
    let g = null;
    // cover-fit the photo into a rect, keeping the face near the given point
    const coverIn = (x, y, w, h) => {
      const k = Math.max(w / IMG.w, h / IMG.h);
      const ix = Math.min(x, Math.max(x + w - IMG.w * k, x + w / 2 - IMG.w * k * IMG.focusX));
      const iy = Math.min(y, Math.max(y + h - IMG.h * k, y + h * 0.42 - IMG.h * k * IMG.focusY));
      return { k, ix, iy };
    };
    const measure = () => {
      const W = stage.clientWidth, H = stage.clientHeight;
      const stacked = W < 900;
      dive.classList.toggle('stacked', stacked);
      const v = stage.style;
      let card;
      if (!stacked) {
        const ch = Math.min(H * 0.74, 760), cw = ch * 0.8;
        const edge = Math.max(22, (W - 1200) / 2 + 22);
        card = { x: W - edge - cw, y: (H - ch) / 2 + 10, w: cw, h: ch };
        v.setProperty('--sl', edge + 'px');
        v.setProperty('--sw', Math.max(320, card.x - edge - 56) + 'px');
        v.setProperty('--st', '50%'); v.setProperty('--sy', '-50%');
      } else {
        const ch = Math.min(H * 0.4, W * 1.1), cw = ch * 0.8;
        card = { x: (W - cw) / 2, y: Math.max(64, H * 0.08), w: cw, h: ch };
        v.setProperty('--sl', '22px');
        v.setProperty('--sw', (W - 44) + 'px');
        v.setProperty('--st', card.y + card.h + 22 + 'px'); v.setProperty('--sy', '0px');
      }
      g = { W, H, card, from: coverIn(0, 0, W, H), to: coverIn(card.x, card.y, card.w, card.h) };
    };
    // at rest the portrait leans toward the pointer, eased so it trails like a spring (mouse only)
    let rest = true;
    const drift = { x: 0, y: 0, tx: 0, ty: 0, raf: 0 };
    let queued = false;
    const update = () => {
      queued = false;
      if (!g) return;
      const r = dive.getBoundingClientRect();
      const p = clamp(-r.top / (r.height - window.innerHeight));
      const e = ease(clamp((p - 0.04) / 0.62));
      const { W, H, card, from, to } = g;
      const v = stage.style;
      // clip from the full stage to the card
      v.setProperty('--ct', mix(0, card.y, e).toFixed(1) + 'px');
      v.setProperty('--cl', mix(0, card.x, e).toFixed(1) + 'px');
      v.setProperty('--cr', mix(0, W - card.x - card.w, e).toFixed(1) + 'px');
      v.setProperty('--cb', mix(0, H - card.y - card.h, e).toFixed(1) + 'px');
      v.setProperty('--cR', mix(0, 28, e).toFixed(1) + 'px');
      // the photo moves and shrinks with the card, so the face stays in frame
      v.setProperty('--ik', mix(from.k, to.k, e).toFixed(4));
      v.setProperty('--ix', (mix(from.ix, to.ix, e) + drift.x * (1 - e)).toFixed(1) + 'px');
      v.setProperty('--iy', (mix(from.iy, to.iy, e) + drift.y * (1 - e)).toFixed(1) + 'px');
      v.setProperty('--fb', mix(0.9, 1, e).toFixed(3));
      // the intro steps aside quickly; the headline follows the card in
      const io = 1 - clamp(p / 0.12);
      v.setProperty('--io', io.toFixed(3));
      v.setProperty('--iy2', ((1 - io) * 24).toFixed(1) + 'px');
      dive.classList.toggle('past-intro', p > 0.12);
      const so = clamp((e - 0.78) / 0.2);   // after the card has nearly settled
      v.setProperty('--so', so.toFixed(3));
      v.setProperty('--sd', ((1 - so) * 24).toFixed(1) + 'px');
      if (e > 0.6) dive.classList.add('opened');   // headline words play once, as the card settles
      rest = p < 0.04;
    };
    const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
    const driftStep = () => {
      drift.x += (drift.tx - drift.x) * 0.08; drift.y += (drift.ty - drift.y) * 0.08;
      update();
      drift.raf = Math.abs(drift.tx - drift.x) + Math.abs(drift.ty - drift.y) > 0.05 ? requestAnimationFrame(driftStep) : 0;
    };
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      window.addEventListener('pointermove', (ev) => {
        const k = rest ? 1 : 0;
        drift.tx = (ev.clientX / innerWidth - 0.5) * -16 * k; drift.ty = (ev.clientY / innerHeight - 0.5) * -10 * k;
        if (!drift.raf) drift.raf = requestAnimationFrame(driftStep);
      }, { passive: true });
    }
    // keyboard: tabbing into the headline scrolls the hero to where it is fully shown
    scene.addEventListener('focusin', () => {
      if (dive.getBoundingClientRect().bottom > innerHeight + 2) window.scrollTo({ top: dive.offsetTop + dive.offsetHeight - innerHeight, behavior: 'instant' });
    });
    measure(); update();
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', () => { measure(); queue(); });
  }

  // ---- Reading progress bar (CSS scroll timeline does the animating) ----
  const bar = document.createElement('div');
  bar.className = 'scroll-progress'; bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);

  // ---- Page transitions: the clicked project's image morphs into its case-study header ----
  const cardFor = (url) => $$('.work-card').find((a) => a.href === url);
  const inView = (el) => { const r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < window.innerHeight; };
  window.addEventListener('pageswap', (e) => {
    if (!e.viewTransition) return;
    const to = e.activation && e.activation.entry && e.activation.entry.url;
    const card = to && cardFor(to);
    const hero = $('.case-hero-media');
    if (card) $('.work-media', card).style.viewTransitionName = 'case-media';
    // case to case is a plain crossfade; case back to home carries the image only if it's on screen
    if (hero && (card || /\/work\//.test(to || '') || !inView(hero))) hero.style.viewTransitionName = 'none';
  });
  window.addEventListener('pagereveal', (e) => {
    if (!e.viewTransition) return;
    document.documentElement.classList.add('vt-in');
    const from = window.navigation && navigation.activation && navigation.activation.from && navigation.activation.from.url;
    const card = from && cardFor(from);
    if (!card) return;
    const media = $('.work-media', card);
    media.style.viewTransitionName = 'case-media';
    e.viewTransition.finished.finally(() => { media.style.viewTransitionName = ''; });
  });

  const year = $('#year');
  if (year) year.textContent = new Date().getFullYear();
})();
