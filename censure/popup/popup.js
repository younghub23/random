document.addEventListener('DOMContentLoaded', () => {
  const globalToggle = document.getElementById('globalToggle');
  const filteredCount = document.getElementById('filteredCount');
  const keywordInput = document.getElementById('keywordInput');
  const addBtn = document.getElementById('addBtn');
  const keywordList = document.getElementById('keywordList');
  const filterModeRadios = document.querySelectorAll('input[name="filterMode"]');
  const whitelistBtn = document.getElementById('whitelistBtn');
  const blacklistBtn = document.getElementById('blacklistBtn');
  const optionsLink = document.getElementById('optionsLink');

  let currentHostname = '';

  const defaultSettings = {
    enabled: true,
    keywords: [],
    filterMode: 'redact',
    siteWhitelist: []
  };

  // --- Helpers ---

  function getActiveTab() {
    return chrome.tabs.query({ active: true, currentWindow: true });
  }

  function loadSettings() {
    return new Promise((resolve) => {
      chrome.storage.local.get(defaultSettings, (settings) => {
        resolve(settings);
      });
    });
  }

  function saveSettings(data) {
    return new Promise((resolve) => {
      chrome.storage.local.set(data, resolve);
    });
  }

  function sendToContentScript(message) {
    getActiveTab().then((tabs) => {
      if (tabs[0] && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, message).catch(() => {
          // Content script may not be injected on this page
        });
      }
    });
  }

  function notifySettingsUpdated() {
    loadSettings().then((settings) => {
      sendToContentScript({ type: 'settingsUpdated', settings });
    });
  }

  function updateBadge(enabled) {
    if (chrome.action && chrome.action.setBadgeText) {
      chrome.action.setBadgeText({ text: enabled ? '' : 'OFF' });
      chrome.action.setBadgeBackgroundColor({ color: '#666' });
    }
  }

  function updateWhitelistButtons(hostname, whitelist) {
    const isWhitelisted = whitelist.includes(hostname);
    whitelistBtn.style.display = isWhitelisted ? 'none' : 'block';
    blacklistBtn.style.display = isWhitelisted ? 'block' : 'none';
  }

  // --- Render ---

  function renderKeywords(keywords) {
    keywordList.innerHTML = '';
    keywords.forEach((keyword, index) => {
      const item = document.createElement('div');
      item.className = 'keyword-item';

      const text = document.createElement('span');
      text.className = 'keyword-text';
      text.textContent = keyword;

      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'delete-btn';
      deleteBtn.textContent = '\u00d7';
      deleteBtn.title = 'Remove keyword';
      deleteBtn.addEventListener('click', () => {
        removeKeyword(index);
      });

      item.appendChild(text);
      item.appendChild(deleteBtn);
      keywordList.appendChild(item);
    });
  }

  // --- Actions ---

  function addKeyword(keyword) {
    loadSettings().then((settings) => {
      const kw = keyword.trim();
      if (!kw || settings.keywords.includes(kw)) return;
      settings.keywords.push(kw);
      saveSettings({ keywords: settings.keywords }).then(() => {
        renderKeywords(settings.keywords);
        notifySettingsUpdated();
      });
    });
  }

  function removeKeyword(index) {
    loadSettings().then((settings) => {
      settings.keywords.splice(index, 1);
      saveSettings({ keywords: settings.keywords }).then(() => {
        renderKeywords(settings.keywords);
        notifySettingsUpdated();
      });
    });
  }

  // --- Event Listeners ---

  globalToggle.addEventListener('change', () => {
    const enabled = globalToggle.checked;
    saveSettings({ enabled }).then(() => {
      sendToContentScript({ type: 'toggle', enabled });
      updateBadge(enabled);
    });
  });

  addBtn.addEventListener('click', () => {
    const value = keywordInput.value.trim();
    if (value) {
      addKeyword(value);
      keywordInput.value = '';
      keywordInput.focus();
    }
  });

  keywordInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const value = keywordInput.value.trim();
      if (value) {
        addKeyword(value);
        keywordInput.value = '';
      }
    }
  });

  filterModeRadios.forEach((radio) => {
    radio.addEventListener('change', () => {
      saveSettings({ filterMode: radio.value }).then(() => {
        notifySettingsUpdated();
      });
    });
  });

  whitelistBtn.addEventListener('click', () => {
    if (!currentHostname) return;
    loadSettings().then((settings) => {
      if (!settings.siteWhitelist.includes(currentHostname)) {
        settings.siteWhitelist.push(currentHostname);
        saveSettings({ siteWhitelist: settings.siteWhitelist }).then(() => {
          updateWhitelistButtons(currentHostname, settings.siteWhitelist);
          notifySettingsUpdated();
        });
      }
    });
  });

  blacklistBtn.addEventListener('click', () => {
    if (!currentHostname) return;
    loadSettings().then((settings) => {
      const idx = settings.siteWhitelist.indexOf(currentHostname);
      if (idx !== -1) {
        settings.siteWhitelist.splice(idx, 1);
        saveSettings({ siteWhitelist: settings.siteWhitelist }).then(() => {
          updateWhitelistButtons(currentHostname, settings.siteWhitelist);
          notifySettingsUpdated();
        });
      }
    });
  });

  optionsLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });

  // --- Initialize ---

  loadSettings().then((settings) => {
    // Set toggle state
    globalToggle.checked = settings.enabled;

    // Set filter mode
    filterModeRadios.forEach((radio) => {
      radio.checked = radio.value === settings.filterMode;
    });

    // Render keywords
    renderKeywords(settings.keywords);

    // Get current tab info
    getActiveTab().then((tabs) => {
      if (tabs[0] && tabs[0].url) {
        try {
          const url = new URL(tabs[0].url);
          currentHostname = url.hostname;
          updateWhitelistButtons(currentHostname, settings.siteWhitelist);
        } catch (e) {
          // Invalid URL (e.g., chrome:// pages)
          whitelistBtn.style.display = 'none';
          blacklistBtn.style.display = 'none';
        }
      }

      // Query content script for filtered count
      if (tabs[0] && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'getCount' })
          .then((response) => {
            if (response && typeof response.count === 'number') {
              filteredCount.textContent = response.count;
            }
          })
          .catch(() => {
            // Content script not available on this page
            filteredCount.textContent = '0';
          });
      }
    });
  });
});
