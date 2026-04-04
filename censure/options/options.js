(function () {
  'use strict';

  /* ==================================================
     Default settings — mirrors utils/storage.js
     ================================================== */
  var DEFAULTS = {
    enabled: true,
    keywords: [],
    categories: {},
    siteWhitelist: [],
    siteBlacklist: [],
    filterMode: 'redact',
    imageUrlPatterns: [],
    faceEmbeddings: [],
    similarityThreshold: 0.65,
    blockedCount: 0
  };

  /* ==================================================
     Storage helpers (uses chrome.storage.local directly)
     ================================================== */
  function getSettings() {
    return new Promise(function (resolve, reject) {
      chrome.storage.local.get(DEFAULTS, function (result) {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(result);
        }
      });
    });
  }

  function saveSettings(partial) {
    return new Promise(function (resolve, reject) {
      chrome.storage.local.set(partial, function () {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve();
        }
      });
    });
  }

  function notifyContentScripts() {
    chrome.tabs.query({}, function (tabs) {
      tabs.forEach(function (tab) {
        chrome.tabs.sendMessage(tab.id, { type: 'settingsUpdated' }).catch(function () {});
      });
    });
  }

  /* ==================================================
     State
     ================================================== */
  var settings = null;
  var activeCategoryFilter = null; // null = show all

  /* ==================================================
     DOM references
     ================================================== */
  var $ = function (sel) { return document.querySelector(sel); };
  var $$ = function (sel) { return document.querySelectorAll(sel); };

  /* ==================================================
     Init
     ================================================== */
  document.addEventListener('DOMContentLoaded', function () {
    initTabs();
    loadAndRender();
  });

  function loadAndRender() {
    getSettings().then(function (s) {
      settings = s;
      renderCategorySelect();
      renderCategoryFilters();
      renderKeywords();
      renderUrlPatterns();
      renderWhitelistSites();
      renderAdvanced();
      bindEvents();
    });
  }

  /* ==================================================
     Tab Switching
     ================================================== */
  function initTabs() {
    $$('.tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        $$('.tab').forEach(function (t) { t.classList.remove('active'); });
        $$('.tab-content').forEach(function (c) { c.classList.remove('active'); });
        btn.classList.add('active');
        var tabId = 'tab-' + btn.getAttribute('data-tab');
        var panel = $('#' + tabId);
        if (panel) panel.classList.add('active');
      });
    });
  }

  /* ==================================================
     Keywords — Rendering
     ================================================== */
  function getCategoryForKeyword(keyword) {
    var cats = settings.categories || {};
    var found = [];
    Object.keys(cats).forEach(function (cat) {
      if (cats[cat].indexOf(keyword) !== -1) {
        found.push(cat);
      }
    });
    return found;
  }

  function renderKeywords() {
    var list = $('#keywordsList');
    if (!list) return;
    list.innerHTML = '';

    var keywords = settings.keywords || [];
    if (keywords.length === 0) {
      list.innerHTML = '<div class="empty-state">No blocked keywords yet. Add one above.</div>';
      return;
    }

    var filtered = keywords;
    if (activeCategoryFilter) {
      var catKeywords = (settings.categories || {})[activeCategoryFilter] || [];
      filtered = keywords.filter(function (kw) {
        return catKeywords.indexOf(kw) !== -1;
      });
    }

    if (filtered.length === 0) {
      list.innerHTML = '<div class="empty-state">No keywords in this category.</div>';
      return;
    }

    filtered.forEach(function (kw) {
      var row = document.createElement('div');
      row.className = 'keyword-row';

      var text = document.createElement('span');
      text.className = 'keyword-text';
      text.textContent = kw;
      row.appendChild(text);

      var cats = getCategoryForKeyword(kw);
      cats.forEach(function (cat) {
        var badge = document.createElement('span');
        badge.className = 'keyword-category-badge';
        badge.textContent = cat;
        row.appendChild(badge);
      });

      var del = document.createElement('button');
      del.className = 'keyword-delete';
      del.textContent = '\u00d7';
      del.title = 'Remove keyword';
      del.setAttribute('data-keyword', kw);
      del.addEventListener('click', function () {
        deleteKeyword(kw);
      });
      row.appendChild(del);

      list.appendChild(row);
    });
  }

  function renderCategorySelect() {
    var sel = $('#categorySelect');
    if (!sel) return;
    // Keep "No category" option, clear the rest
    sel.innerHTML = '<option value="">No category</option>';
    var cats = settings.categories || {};
    Object.keys(cats).sort().forEach(function (cat) {
      var opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      sel.appendChild(opt);
    });
  }

  function renderCategoryFilters() {
    var container = $('#categoryFilters');
    if (!container) return;
    container.innerHTML = '';

    var cats = settings.categories || {};
    var catNames = Object.keys(cats).sort();
    if (catNames.length === 0) return;

    // "All" chip
    var allChip = document.createElement('button');
    allChip.className = 'category-chip' + (activeCategoryFilter === null ? ' active' : '');
    allChip.textContent = 'All';
    allChip.addEventListener('click', function () {
      activeCategoryFilter = null;
      renderCategoryFilters();
      renderKeywords();
    });
    container.appendChild(allChip);

    catNames.forEach(function (cat) {
      var chip = document.createElement('button');
      chip.className = 'category-chip' + (activeCategoryFilter === cat ? ' active' : '');
      chip.textContent = cat + ' (' + cats[cat].length + ')';
      chip.addEventListener('click', function () {
        activeCategoryFilter = activeCategoryFilter === cat ? null : cat;
        renderCategoryFilters();
        renderKeywords();
      });
      container.appendChild(chip);
    });
  }

  /* ==================================================
     Keywords — Add / Delete
     ================================================== */
  function addKeyword() {
    var input = $('#newKeyword');
    var keyword = (input.value || '').trim();
    if (!keyword) return;

    var catSelect = $('#categorySelect');
    var catNew = $('#newCategory');
    var category = (catNew.value || '').trim() || catSelect.value;

    // Add to keywords array
    if (settings.keywords.indexOf(keyword) === -1) {
      settings.keywords.push(keyword);
    }

    // Add to category
    if (category) {
      if (!settings.categories[category]) {
        settings.categories[category] = [];
      }
      if (settings.categories[category].indexOf(keyword) === -1) {
        settings.categories[category].push(keyword);
      }
    }

    saveSettings({
      keywords: settings.keywords,
      categories: settings.categories
    }).then(function () {
      input.value = '';
      catNew.value = '';
      catSelect.value = '';
      renderCategorySelect();
      renderCategoryFilters();
      renderKeywords();
      notifyContentScripts();
    });
  }

  function deleteKeyword(keyword) {
    var idx = settings.keywords.indexOf(keyword);
    if (idx !== -1) {
      settings.keywords.splice(idx, 1);
    }
    var cats = settings.categories;
    Object.keys(cats).forEach(function (cat) {
      var catIdx = cats[cat].indexOf(keyword);
      if (catIdx !== -1) {
        cats[cat].splice(catIdx, 1);
      }
    });

    saveSettings({
      keywords: settings.keywords,
      categories: cats
    }).then(function () {
      renderCategorySelect();
      renderCategoryFilters();
      renderKeywords();
      notifyContentScripts();
    });
  }

  /* ==================================================
     Import / Export
     ================================================== */
  function exportSettings() {
    getSettings().then(function (s) {
      var json = JSON.stringify(s, null, 2);
      var blob = new Blob([json], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'censure-settings.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  function importSettings(file) {
    var reader = new FileReader();
    reader.onload = function (e) {
      try {
        var parsed = JSON.parse(e.target.result);
        // Validate: must have keywords array at minimum
        if (!Array.isArray(parsed.keywords)) {
          alert('Invalid settings file: missing keywords array.');
          return;
        }
        saveSettings(parsed).then(function () {
          notifyContentScripts();
          window.location.reload();
        });
      } catch (err) {
        alert('Failed to parse settings file: ' + err.message);
      }
    };
    reader.readAsText(file);
  }

  /* ==================================================
     Image URL Patterns
     ================================================== */
  function renderUrlPatterns() {
    var list = $('#urlPatternsList');
    if (!list) return;
    list.innerHTML = '';

    var patterns = settings.imageUrlPatterns || [];
    if (patterns.length === 0) {
      list.innerHTML = '<div class="empty-state">No URL patterns yet.</div>';
      return;
    }

    patterns.forEach(function (pattern, index) {
      var row = document.createElement('div');
      row.className = 'pattern-row';

      var text = document.createElement('span');
      text.className = 'pattern-text';
      text.textContent = pattern;
      row.appendChild(text);

      var del = document.createElement('button');
      del.className = 'pattern-delete';
      del.textContent = '\u00d7';
      del.title = 'Remove pattern';
      del.addEventListener('click', function () {
        deleteUrlPattern(index);
      });
      row.appendChild(del);

      list.appendChild(row);
    });
  }

  function addUrlPattern() {
    var input = $('#newUrlPattern');
    var pattern = (input.value || '').trim();
    if (!pattern) return;

    if (!settings.imageUrlPatterns) {
      settings.imageUrlPatterns = [];
    }
    settings.imageUrlPatterns.push(pattern);

    saveSettings({ imageUrlPatterns: settings.imageUrlPatterns }).then(function () {
      input.value = '';
      renderUrlPatterns();
      notifyContentScripts();
    });
  }

  function deleteUrlPattern(index) {
    settings.imageUrlPatterns.splice(index, 1);
    saveSettings({ imageUrlPatterns: settings.imageUrlPatterns }).then(function () {
      renderUrlPatterns();
      notifyContentScripts();
    });
  }

  /* ==================================================
     Sites Management — Whitelist
     ================================================== */
  function renderWhitelistSites() {
    var list = $('#whitelistSites');
    if (!list) return;
    list.innerHTML = '';

    var sites = settings.siteWhitelist || [];
    if (sites.length === 0) {
      list.innerHTML = '<div class="empty-state">No whitelisted sites. Filtering is active on all sites.</div>';
      return;
    }

    sites.forEach(function (site, index) {
      var row = document.createElement('div');
      row.className = 'site-row';

      var text = document.createElement('span');
      text.className = 'site-text';
      text.textContent = site;
      row.appendChild(text);

      var del = document.createElement('button');
      del.className = 'site-delete';
      del.textContent = '\u00d7';
      del.title = 'Remove site';
      del.addEventListener('click', function () {
        deleteWhitelistSite(index);
      });
      row.appendChild(del);

      list.appendChild(row);
    });
  }

  function addWhitelistSite() {
    var input = $('#newWhitelistSite');
    var site = (input.value || '').trim().toLowerCase();
    if (!site) return;

    if (!settings.siteWhitelist) {
      settings.siteWhitelist = [];
    }
    if (settings.siteWhitelist.indexOf(site) === -1) {
      settings.siteWhitelist.push(site);
    }

    saveSettings({ siteWhitelist: settings.siteWhitelist }).then(function () {
      input.value = '';
      renderWhitelistSites();
      notifyContentScripts();
    });
  }

  function deleteWhitelistSite(index) {
    settings.siteWhitelist.splice(index, 1);
    saveSettings({ siteWhitelist: settings.siteWhitelist }).then(function () {
      renderWhitelistSites();
      notifyContentScripts();
    });
  }

  /* ==================================================
     Advanced Settings
     ================================================== */
  function renderAdvanced() {
    var modeSelect = $('#filterModeSelect');
    if (modeSelect) {
      modeSelect.value = settings.filterMode || 'redact';
    }

    var slider = $('#thresholdSlider');
    var display = $('#thresholdValue');
    if (slider && display) {
      slider.value = settings.similarityThreshold || 0.65;
      display.textContent = slider.value;
    }
  }

  /* ==================================================
     Event Bindings
     ================================================== */
  function bindEvents() {
    // Add keyword
    var addBtn = $('#addKeywordBtn');
    if (addBtn) {
      addBtn.addEventListener('click', addKeyword);
    }

    // Enter key on keyword input
    var kwInput = $('#newKeyword');
    if (kwInput) {
      kwInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') addKeyword();
      });
    }

    // Export
    var exportBtn = $('#exportBtn');
    if (exportBtn) {
      exportBtn.addEventListener('click', exportSettings);
    }

    // Import
    var importBtn = $('#importBtn');
    var importFile = $('#importFile');
    if (importBtn && importFile) {
      importBtn.addEventListener('click', function () {
        importFile.click();
      });
      importFile.addEventListener('change', function (e) {
        if (e.target.files && e.target.files[0]) {
          importSettings(e.target.files[0]);
        }
      });
    }

    // URL patterns
    var addUrlBtn = $('#addUrlPatternBtn');
    if (addUrlBtn) {
      addUrlBtn.addEventListener('click', addUrlPattern);
    }
    var urlInput = $('#newUrlPattern');
    if (urlInput) {
      urlInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') addUrlPattern();
      });
    }

    // Whitelist sites
    var addWlBtn = $('#addWhitelistBtn');
    if (addWlBtn) {
      addWlBtn.addEventListener('click', addWhitelistSite);
    }
    var wlInput = $('#newWhitelistSite');
    if (wlInput) {
      wlInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') addWhitelistSite();
      });
    }

    // Filter mode
    var modeSelect = $('#filterModeSelect');
    if (modeSelect) {
      modeSelect.addEventListener('change', function () {
        settings.filterMode = modeSelect.value;
        saveSettings({ filterMode: modeSelect.value }).then(notifyContentScripts);
      });
    }

    // Threshold slider
    var slider = $('#thresholdSlider');
    var display = $('#thresholdValue');
    if (slider && display) {
      slider.addEventListener('input', function () {
        display.textContent = slider.value;
      });
      slider.addEventListener('change', function () {
        var val = parseFloat(slider.value);
        settings.similarityThreshold = val;
        saveSettings({ similarityThreshold: val }).then(notifyContentScripts);
      });
    }

    // Reset
    var resetBtn = $('#resetBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        if (confirm('Are you sure you want to reset ALL Censure settings? This cannot be undone.')) {
          chrome.storage.local.clear(function () {
            notifyContentScripts();
            window.location.reload();
          });
        }
      });
    }
  }
})();
