(function() {
  'use strict';

  var THEME_KEY = 'ndcTheme', READ_KEY = 'ndcReadState';

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function escapeRegExp(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function debounce(fn, wait) { var t; return function() { clearTimeout(t); t = setTimeout(fn, wait); }; }

  // ---------------- theme ----------------
  function applyTheme(theme) {
    if (theme === 'dark' || theme === 'light') document.documentElement.setAttribute('data-theme', theme);
    else document.documentElement.removeAttribute('data-theme');
  }
  function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var next = !current ? (prefersDark ? 'light' : 'dark') : (current === 'dark' ? 'light' : 'dark');
    store(THEME_KEY, next);
    applyTheme(next);
  }
  applyTheme(load(THEME_KEY));

  // ---------------- reading checkboxes ----------------
  function loadReadState() { try { return JSON.parse(load(READ_KEY)) || {}; } catch (e) { return {}; } }
  function initReadingCheckboxes() {
    var state = loadReadState();
    document.querySelectorAll('.read-checkbox').forEach(function(cb) {
      var id = cb.dataset.readId, li = cb.closest('li');
      if (state[id]) { cb.checked = true; if (li) li.classList.add('is-read'); }
      cb.addEventListener('change', function() {
        var s = loadReadState();
        if (cb.checked) s[id] = true; else delete s[id];
        store(READ_KEY, JSON.stringify(s));
        if (li) li.classList.toggle('is-read', cb.checked);
        updateProgress();
      });
    });
    updateProgress();
  }

  // ---------------- progress
  function updateProgress() {
    var req = document.querySelectorAll('.cite-req .read-checkbox'), done = 0;
    req.forEach(function(cb) { if (cb.checked) done++; });
    var el = document.getElementById('progLine');
    if (el) el.textContent = done + ' of ' + req.length + ' required readings marked read';
  }
  function nextUnread() {
    closeDrawer();
    var cbs = document.querySelectorAll('.cite-req .read-checkbox');
    for (var i = 0; i < cbs.length; i++) if (!cbs[i].checked) {
      var card = cbs[i].closest('details'); if (card) card.open = true;
      var li = cbs[i].closest('li'); setTimeout(function() { flash(li); }, 30); return;
    }
  }

  // ---------------- search ----------------
  var searchIndex = [];
  function buildSearchIndex() {
    searchIndex = Array.prototype.map.call(document.querySelectorAll('.session-card'), function(card) {
      return { card: card, code: card.dataset.code, text: card.textContent.toLowerCase() };
    });
  }
  function clearHighlights() {
    document.querySelectorAll('mark.search-hl').forEach(function(mark) {
      var parent = mark.parentNode;
      if (!parent) return;
      while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
      parent.removeChild(mark);
      parent.normalize();
    });
  }
  function highlightTerms(root, terms) {
    var src = terms.map(escapeRegExp).join('|');
    var testRe = new RegExp(src, 'i'), globalRe = new RegExp(src, 'gi');
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function(node) {
        var p = node.parentNode;
        if (!p || p.nodeName === 'SCRIPT' || p.nodeName === 'STYLE') return NodeFilter.FILTER_REJECT;
        return testRe.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function(node) {
      var text = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
      globalRe.lastIndex = 0;
      while ((m = globalRe.exec(text))) {
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var mark = document.createElement('mark');
        mark.className = 'search-hl';
        mark.textContent = m[0];
        frag.appendChild(mark);
        last = globalRe.lastIndex;
      }
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }
  function filterSessions() {
    var q = document.getElementById('searchBox').value.trim().toLowerCase();
    var terms = q ? q.split(/\s+/).filter(Boolean) : [];
    var visible = {}, count = 0;
    clearHighlights();
    searchIndex.forEach(function(e) {
      var match = !terms.length || terms.every(function(t) { return e.text.indexOf(t) !== -1; });
      e.card.style.display = match ? '' : 'none';
      if (match) {
        count++; visible[e.code] = true;
        if (terms.length) { e.card.open = true; e.card.querySelectorAll('details.more').forEach(function(d) { d.open = true; }); highlightTerms(e.card, terms); }
      }
    });
    document.getElementById('searchClearBtn').style.display = q ? 'flex' : 'none';
    document.getElementById('noResults').style.display = (terms.length && !count) ? 'block' : 'none';
    var status = document.getElementById('searchStatus');
    if (terms.length && count) { status.textContent = count + ' of ' + searchIndex.length + ' lessons match'; status.style.display = 'block'; }
    else status.style.display = 'none';
  }
  function expandAll() { document.querySelectorAll('.session-card').forEach(function(c) { c.open = true; }); }
  function collapseAll() { document.querySelectorAll('.session-card').forEach(function(c) { c.open = false; }); }

  // ---------------- navigation ----------------
  function flash(el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.add('flash');
    setTimeout(function() { el.classList.remove('flash'); }, 1600);
  }
  function jumpToSession(code) {
    var card = document.getElementById('card-' + code);
    if (!card) return;
    card.open = true;
    setTimeout(function() { flash(card); }, 30);
  }
  function jumpToRef(id) {
    var el = document.getElementById(id);
    if (el) { if (el.tagName === 'DETAILS') el.open = true; el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }
  function focusSearch() {
    openDrawer();
    var box = document.getElementById('searchBox');
    setTimeout(function() { box.focus(); }, 250);
  }

  // ---------------- drawer ----------------
  function openDrawer() {
    document.querySelector('.sidebar').classList.add('open');
    document.getElementById('drawerBackdrop').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    document.querySelector('.sidebar').classList.remove('open');
    document.getElementById('drawerBackdrop').classList.remove('open');
    document.body.style.overflow = '';
  }

  var ACTIONS = {
    'next-unread': nextUnread, 'expand-all': expandAll, 'collapse-all': collapseAll,
    'scroll-top': function() { window.scrollTo({ top: 0, behavior: 'smooth' }); },
    'focus-search': focusSearch, 'theme-toggle': toggleTheme, 'open-drawer': openDrawer, 'close-drawer': closeDrawer
  };
  document.addEventListener('click', function(e) {
    var a = e.target.closest('[data-action]');
    if (a && ACTIONS[a.dataset.action]) { ACTIONS[a.dataset.action](); return; }
    var s = e.target.closest('[data-jump-session]');
    if (s) { closeDrawer(); jumpToSession(s.dataset.jumpSession); return; }
    var r = e.target.closest('[data-jump-ref]');
    if (r) { closeDrawer(); jumpToRef(r.dataset.jumpRef); }
  });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeDrawer(); });

  var box = document.getElementById('searchBox');
  function clearSearchBox() { if (!box.value) return; box.value = ''; filterSessions(); box.focus(); }
  box.addEventListener('input', debounce(filterSessions, 100));
  box.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && this.value) { clearSearchBox(); e.stopPropagation(); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      var m = searchIndex.filter(function(x) { return x.card.style.display !== 'none'; })[0];
      if (m) { closeDrawer(); m.card.open = true; m.card.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }
  });
  document.getElementById('searchClearBtn').addEventListener('click', clearSearchBox);
  window.addEventListener('scroll', function() {
    document.getElementById('backToTop').classList.toggle('show', window.scrollY > 600);
  });
  window.addEventListener('resize', debounce(function() { if (window.innerWidth >= 1100) closeDrawer(); }, 200));

  // ---------------- init ----------------
  buildSearchIndex();
  initReadingCheckboxes();
})();
