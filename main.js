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
  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    if (nav) {
      if (y > lastY + 6 && y > 320 && !nav.classList.contains('open')) nav.classList.add('nav-hidden');
      else if (y < lastY - 6 || y < 320) nav.classList.remove('nav-hidden');
    }
    lastY = y;
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

  // ---- Hero dive: scrolling zooms into the portrait's eye; the headline opens through it ----
  const dive = $('.dive');
  const face = dive && $('.dive-face img', dive);
  if (dive && face && !reduceMotion) {
    dive.classList.add('is-dive');
    const stage = $('.dive-stage', dive);
    const EYE = { x: 611.5, y: 524, w: 69 };        // the lit eye in portrait.jpg (1100 x 1525); assets/eye.svg is its traced contour
    const IMG = { w: 1100, h: 1525, posX: .5, posY: .3 };
    const clamp = (v) => Math.min(1, Math.max(0, v));
    const ease = (t) => t * t * (3 - 2 * t);
    let eye = { x: 0, y: 0, w: 0 };
    const scene = $('.dive-scene', dive);
    let box = { cx: 0, cy: 0, w: 1, h: 1 };
    const measure = () => {
      const W = stage.clientWidth, H = stage.clientHeight;
      const k = Math.max(W / IMG.w, H / IMG.h);   // object-fit: cover
      const ox = (W - IMG.w * k) * IMG.posX, oy = (H - IMG.h * k) * IMG.posY;
      eye = { x: ox + EYE.x * k, y: oy + EYE.y * k, w: EYE.w * k, big: Math.hypot(W, H) };
      // the headline block's own size and centre at scale 1 (padding excluded), relative to the stage
      const prev = scene.style.transform; scene.style.transform = 'none';
      const st = stage.getBoundingClientRect();
      const rs = Array.from(scene.children).map((c) => c.getBoundingClientRect());
      const L = Math.min(...rs.map((r) => r.left)), R = Math.max(...rs.map((r) => r.right));
      const T = Math.min(...rs.map((r) => r.top)), B = Math.max(...rs.map((r) => r.bottom));
      box = { cx: (L + R) / 2 - st.left, cy: (T + B) / 2 - st.top, w: R - L, h: B - T };
      scene.style.transform = prev;
      stage.style.setProperty('--ex', eye.x + 'px');
      stage.style.setProperty('--ey', eye.y + 'px');
    };
    let queued = false;
    const update = () => {
      queued = false;
      const r = dive.getBoundingClientRect();
      const p = clamp(-r.top / (r.height - window.innerHeight));
      const z = ease(clamp((p - 0.04) / 0.66));      // the dive itself
      const open = ease(clamp((z - 0.1) / 0.28));     // the eye itself opening into a window
      const s = 1 + z * z * 9;
      // matches the real eye once open, then widens past it until the window fills the screen
      const hw = Math.max(1, eye.w * s * open * (1 + Math.max(0, z - 0.38) * 16));
      const v = stage.style;
      v.setProperty('--s', s.toFixed(3));
      v.setProperty('--hw', hw.toFixed(1) + 'px');
      v.setProperty('--fb', (1 - z * 0.75).toFixed(3));   // skin darkens as it magnifies, hiding the blur
      v.setProperty('--fo', (1 - clamp((z - 0.82) / 0.16)).toFixed(3));
      v.setProperty('--io', (1 - clamp(p / 0.1)).toFixed(3));
      dive.classList.toggle('past-intro', p > 0.1);
      rest = p < 0.08;
      // the headline is a whole miniature inside the eye: it fits the opening and grows with it,
      // travelling from the eye to the centre of the screen
      const fit = Math.min(1, (hw * 0.62) / box.w, (hw * 0.29 * 0.62) / box.h);
      v.setProperty('--ss', fit.toFixed(4));
      v.setProperty('--tx', ((eye.x - box.cx) * (1 - fit)).toFixed(1) + 'px');
      v.setProperty('--ty', ((eye.y - box.cy) * (1 - fit)).toFixed(1) + 'px');
      v.setProperty('--so', clamp((open - 0.05) / 0.35).toFixed(3));
      if (open > 0.1) dive.classList.add('opened');   // headline entrance plays once, as the eye opens
      // the face layer stops catching clicks once the scene is through
      $('.dive-face', dive).style.pointerEvents = z > 0.6 ? 'none' : '';
    };
    const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
    // at rest the portrait leans toward the pointer, eased so it trails like a spring (mouse only)
    let rest = true;
    const drift = { x: 0, y: 0, tx: 0, ty: 0, raf: 0 };
    const driftStep = () => {
      drift.x += (drift.tx - drift.x) * 0.08; drift.y += (drift.ty - drift.y) * 0.08;
      stage.style.setProperty('--mx', drift.x.toFixed(2) + 'px'); stage.style.setProperty('--my', drift.y.toFixed(2) + 'px');
      drift.raf = Math.abs(drift.tx - drift.x) + Math.abs(drift.ty - drift.y) > 0.05 ? requestAnimationFrame(driftStep) : 0;
    };
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      window.addEventListener('pointermove', (e) => {
        const k = rest ? 1 : 0;
        drift.tx = (e.clientX / innerWidth - 0.5) * -18 * k; drift.ty = (e.clientY / innerHeight - 0.5) * -12 * k;
        if (!drift.raf) drift.raf = requestAnimationFrame(driftStep);
      }, { passive: true });
    }
    // keyboard: tabbing into the hidden headline scene scrolls the dive open first
    $('.dive-scene', dive).addEventListener('focusin', () => {
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
