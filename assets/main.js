/* MzansiWins - Static Site JS */
(function() {
  'use strict';

  /* ===== SAFE STORAGE (in-memory, persists for session) ===== */
  var memStore = {};
  var store = {
    get: function(k) { return memStore[k] || null; },
    set: function(k, v) { memStore[k] = v; }
  };

  /* ===== DARK MODE ===== */
  var html = document.documentElement;
  var stored = store.get('mw-theme');
  if (stored) html.setAttribute('data-theme', stored);

  function toggleTheme() {
    var current = html.getAttribute('data-theme') || 'light';
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    store.set('mw-theme', next);
    updateThemeIcons();
  }
  function updateThemeIcons() {
    var isDark = html.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.theme-btn').forEach(function(btn) {
      btn.innerHTML = isDark
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    });
  }
  document.addEventListener('DOMContentLoaded', updateThemeIcons);
  window.toggleTheme = toggleTheme;

  /* ===== MOBILE MENU ===== */
  window.toggleMobileMenu = function() {
    var overlay = document.querySelector('.mobile-overlay');
    var menu = document.querySelector('.mobile-menu');
    if (!overlay || !menu) return;
    var isOpen = menu.classList.contains('open');
    if (isOpen) {
      menu.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    } else {
      menu.classList.add('open');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    // Update hamburger icon
    var btn = document.querySelector('.hamburger');
    if (btn) {
      btn.innerHTML = menu.classList.contains('open')
        ? '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
        : '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
    }
  };

  window.closeMobileMenu = function() {
    var overlay = document.querySelector('.mobile-overlay');
    var menu = document.querySelector('.mobile-menu');
    if (overlay) overlay.classList.remove('open');
    if (menu) menu.classList.remove('open');
    document.body.style.overflow = '';
    var btn = document.querySelector('.hamburger');
    if (btn) btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
  };

  window.toggleSubmenu = function(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle('open');
    // Rotate chevron
    var btn = el.previousElementSibling;
    if (btn) {
      var chevron = btn.querySelector('.mobile-chevron');
      if (chevron) chevron.style.transform = el.classList.contains('open') ? 'rotate(180deg)' : 'rotate(0)';
    }
  };

  /* ===== FAQ ACCORDION ===== */
  window.toggleFaq = function(el) {
    var item = el.closest('.faq-item');
    if (!item) return;
    var wasOpen = item.classList.contains('open');
    // Close all
    document.querySelectorAll('.faq-item.open').forEach(function(f) { f.classList.remove('open'); });
    // Toggle clicked
    if (!wasOpen) item.classList.add('open');
  };

  /* ===== COPY PROMO CODE ===== */
  window.copyCode = function(btn, code) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).then(function() {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function() { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      });
    }
  };

  /* ===== STAR / FAVOURITE ===== */
  function getStarred() {
    try { return JSON.parse(store.get('mw-starred') || '[]'); } catch(e) { return []; }
  }
  function saveStarred(arr) {
    store.set('mw-starred', JSON.stringify(arr));
  }
  window.toggleStar = function(brandId) {
    var starred = getStarred();
    var idx = starred.indexOf(brandId);
    if (idx >= 0) starred.splice(idx, 1); else starred.push(brandId);
    saveStarred(starred);
    updateStarButtons();
    reorderStarred();
    updateBonusCounter();
  };
  function updateStarButtons() {
    var starred = getStarred();
    document.querySelectorAll('.star-btn').forEach(function(btn) {
      var id = btn.getAttribute('data-brand');
      if (starred.indexOf(id) >= 0) {
        btn.classList.add('starred');
        btn.setAttribute('aria-label', 'Remove from favourites');
      } else {
        btn.classList.remove('starred');
        btn.setAttribute('aria-label', 'Add to favourites');
      }
    });
  }
  function reorderStarred() {
    var starred = getStarred();

    // Reorder homepage card grid
    var cardGrid = document.querySelector('.bookmaker-grid');
    if (cardGrid) {
      var cards = Array.from(cardGrid.children);
      stableSortStarred(cards, starred);
      cards.forEach(function(c) { cardGrid.appendChild(c); });
    }

    // Reorder desktop table rows (betting-sites / casino-sites)
    var tbody = document.querySelector('.data-table tbody');
    if (tbody) {
      var rows = Array.from(tbody.querySelectorAll('tr[data-brand-id]'));
      stableSortStarred(rows, starred);
      rows.forEach(function(r, i) {
        tbody.appendChild(r);
        // Update rank number in first cell
        var rankCell = r.querySelector('td:first-child');
        if (rankCell && rankCell.getAttribute('data-sort')) {
          rankCell.textContent = i + 1;
          rankCell.setAttribute('data-sort', i + 1);
        }
        // Update row striping
        r.style.background = '';
      });
    }

    // Reorder mobile listing cards
    var mobileList = document.querySelector('.listing-mobile');
    if (mobileList) {
      var mCards = Array.from(mobileList.querySelectorAll('.listing-card[data-brand-id]'));
      stableSortStarred(mCards, starred);
      mCards.forEach(function(c) { mobileList.appendChild(c); });
    }

    // Reorder promo code cards
    var promoGrid = document.querySelector('.promo-card-grid');
    if (promoGrid) {
      var pCards = Array.from(promoGrid.querySelectorAll('.promo-card[data-brand-id]'));
      stableSortStarred(pCards, starred);
      pCards.forEach(function(c) { promoGrid.appendChild(c); });
    }
  }

  function stableSortStarred(items, starred) {
    // Tag each item with its original index for stable sort
    items.forEach(function(el, i) { el._origIdx = i; });
    items.sort(function(a, b) {
      var aId = a.getAttribute('data-brand-id') || '';
      var bId = b.getAttribute('data-brand-id') || '';
      var aS = starred.indexOf(aId) >= 0 ? 0 : 1;
      var bS = starred.indexOf(bId) >= 0 ? 0 : 1;
      if (aS !== bS) return aS - bS;
      return a._origIdx - b._origIdx;
    });
  }
  /* ===== BONUS COUNTER (listing pages) ===== */
  function updateBonusCounter() {
    var starredTotal = document.querySelector('.starred-total');
    var starredCount = document.querySelector('.starred-count');
    if (!starredTotal || !starredCount) return;
    var starred = getStarred();
    var total = 0;
    var count = 0;
    // Use data from table rows or mobile cards
    var elements = document.querySelectorAll('[data-brand-id][data-bonus-val]');
    var seen = {};
    elements.forEach(function(el) {
      var id = el.getAttribute('data-brand-id');
      if (seen[id]) return;
      seen[id] = true;
      if (starred.indexOf(id) >= 0) {
        total += parseInt(el.getAttribute('data-bonus-val') || '0');
        count++;
      }
    });
    starredTotal.textContent = 'R' + total.toLocaleString('en-ZA');
    starredCount.textContent = count + ' bookmaker' + (count !== 1 ? 's' : '') + ' starred';
  }

  document.addEventListener('DOMContentLoaded', function() {
    updateStarButtons();
    reorderStarred();
    updateBonusCounter();
  });

  /* ===== FILTER TABS ===== */
  window.filterCards = function(btn, filterVal) {
    // Update active tab
    var tabs = btn.parentElement.querySelectorAll('.filter-tab, .filter-pill');
    tabs.forEach(function(t) { t.classList.remove('active'); });
    btn.classList.add('active');

    // Filter cards
    var container = btn.closest('.section, section')?.querySelector('.filterable-grid, .bookmaker-grid');
    if (!container) return;
    var cards = container.querySelectorAll('[data-filter]');
    cards.forEach(function(card) {
      if (filterVal === 'all') {
        card.style.display = '';
      } else {
        var val = card.getAttribute('data-filter') || '';
        card.style.display = val.indexOf(filterVal) >= 0 ? '' : 'none';
      }
    });
  };

  /* ===== SORTABLE TABLES ===== */
  window.sortTable = function(th) {
    var table = th.closest('table');
    if (!table) return;
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var idx = Array.from(th.parentElement.children).indexOf(th);
    var dir = th.getAttribute('data-sort-dir') === 'asc' ? 'desc' : 'asc';

    // Reset all headers
    th.parentElement.querySelectorAll('th').forEach(function(h) {
      h.removeAttribute('data-sort-dir');
      h.classList.remove('sorted');
    });
    th.setAttribute('data-sort-dir', dir);
    th.classList.add('sorted');

    rows.sort(function(a, b) {
      var aVal = a.children[idx]?.getAttribute('data-sort') || a.children[idx]?.textContent?.trim() || '';
      var bVal = b.children[idx]?.getAttribute('data-sort') || b.children[idx]?.textContent?.trim() || '';
      var aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
      var bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return dir === 'asc' ? aNum - bNum : bNum - aNum;
      }
      return dir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    rows.forEach(function(r) { tbody.appendChild(r); });

    // Update sort icons
    th.parentElement.querySelectorAll('th .sort-icon').forEach(function(icon) {
      icon.textContent = '\u2195';
    });
    var icon = th.querySelector('.sort-icon');
    if (icon) icon.textContent = dir === 'asc' ? '\u2191' : '\u2193';
  };

  /* ===== SEARCH ===== */
  window.searchCards = function(input) {
    var val = input.value.toLowerCase();
    var container = input.closest('.section, section')?.querySelector('.filterable-grid, .bookmaker-grid') || document.querySelector('.filterable-grid, .bookmaker-grid');
    if (!container) return;
    container.querySelectorAll('[data-name]').forEach(function(card) {
      var name = (card.getAttribute('data-name') || '').toLowerCase();
      card.style.display = name.indexOf(val) >= 0 ? '' : 'none';
    });
  };

  /* ===== SORT SELECT (payment hub) ===== */
  window.sortMethods = function(select) {
    var val = select.value;
    var container = document.querySelector('.method-list');
    if (!container) return;
    var items = Array.from(container.children);
    items.sort(function(a, b) {
      if (val === 'name') return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '');
      if (val === 'speed') {
        var aFast = (a.getAttribute('data-speed') || '').toLowerCase().indexOf('instant') >= 0 ? 0 : 1;
        var bFast = (b.getAttribute('data-speed') || '').toLowerCase().indexOf('instant') >= 0 ? 0 : 1;
        return aFast - bFast;
      }
      if (val === 'brands') return parseInt(b.getAttribute('data-brands') || 0) - parseInt(a.getAttribute('data-brands') || 0);
      return 0;
    });
    items.forEach(function(i) { container.appendChild(i); });
  };


  /* ===== SEARCH TABLE (for listing pages) ===== */
  window.searchTable = function(input) {
    var val = input.value.toLowerCase();
    var table = document.querySelector('.data-table');
    if (!table) return;
    var rows = table.querySelectorAll('tbody tr');
    rows.forEach(function(row) {
      var name = '';
      row.querySelectorAll('td').forEach(function(td) { name += ' ' + td.textContent.toLowerCase(); });
      row.style.display = name.indexOf(val) >= 0 ? '' : 'none';
    });
  };

  /* ===== LIGHTBOX (site preview) ===== */
  window.openLightbox = function(src) {
    var overlay = document.querySelector('.lightbox-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'lightbox-overlay';
      overlay.innerHTML = '<button class="lightbox-close" onclick="closeLightbox()">&times;</button><img src="" alt="Preview">';
      overlay.onclick = function(ev) { if (ev.target === overlay) closeLightbox(); };
      document.body.appendChild(overlay);
    }
    overlay.querySelector('img').src = src;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  window.closeLightbox = function() {
    var overlay = document.querySelector('.lightbox-overlay');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  };
  document.addEventListener('keydown', function(ev) {
    if (ev.key === 'Escape') closeLightbox();
  });

  /* ===== SEARCH LISTING (table + cards) ===== */
  window.searchListing = function(input) {
    var val = input.value.toLowerCase();
    // Search desktop table rows
    var table = document.querySelector('.data-table');
    if (table) {
      var rows = table.querySelectorAll('tbody tr');
      rows.forEach(function(row) {
        var name = (row.getAttribute('data-name') || '').toLowerCase();
        var text = row.textContent.toLowerCase();
        row.style.display = (name.indexOf(val) >= 0 || text.indexOf(val) >= 0) ? '' : 'none';
      });
    }
    // Search mobile cards
    document.querySelectorAll('.listing-card').forEach(function(card) {
      var name = (card.getAttribute('data-name') || '').toLowerCase();
      card.style.display = name.indexOf(val) >= 0 ? '' : 'none';
    });
  };
})();

/* ===== NEWS CATEGORY FILTER ===== */
function filterNews(btn, cat) {
  // Update active tab
  document.querySelectorAll('.news-filter-tab').forEach(function(t) {
    t.classList.remove('active');
  });
  btn.classList.add('active');

  // Filter cards
  var cards = document.querySelectorAll('.news-grid .news-card');
  var visible = 0;
  cards.forEach(function(card) {
    if (cat === 'all' || card.getAttribute('data-category') === cat) {
      card.style.display = '';
      visible++;
    } else {
      card.style.display = 'none';
    }
  });

  // Show/hide empty state
  var empty = document.querySelector('.news-empty-state');
  if (empty) empty.style.display = visible === 0 ? '' : 'none';

  // Update URL without reload
  if (cat === 'all') {
    history.replaceState(null, '', window.location.pathname);
  } else {
    history.replaceState(null, '', '?cat=' + encodeURIComponent(cat));
  }
}

// On page load, check for ?cat= param
(function() {
  var params = new URLSearchParams(window.location.search);
  var cat = params.get('cat');
  if (cat) {
    var tab = document.querySelector('.news-filter-tab[data-cat="' + cat + '"]');
    if (tab) {
      filterNews(tab, cat);
    }
  }
})();
