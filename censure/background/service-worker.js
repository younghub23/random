'use strict';

// Censure — Background Service Worker (Manifest V3)
// Minimal: handles badge updates and extension lifecycle

const DEFAULT_SETTINGS = {
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

// Initialize default settings on install
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.storage.local.get(null, (existing) => {
      const settings = Object.assign({}, DEFAULT_SETTINGS, existing);
      chrome.storage.local.set(settings);
    });
  }
  // Set default badge style
  chrome.action.setBadgeBackgroundColor({ color: '#e94560' });
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'updateBadge') {
    const tabId = sender.tab ? sender.tab.id : null;
    if (tabId) {
      const text = message.count > 0 ? String(message.count) : '';
      chrome.action.setBadgeText({ text, tabId });
    }
    sendResponse({ ok: true });
  }

  if (message.type === 'getSettings') {
    chrome.storage.local.get(null, (settings) => {
      sendResponse(Object.assign({}, DEFAULT_SETTINGS, settings));
    });
    return true; // async response
  }

  if (message.type === 'isEnabled') {
    chrome.storage.local.get(['enabled'], (result) => {
      sendResponse({ enabled: result.enabled !== false });
    });
    return true;
  }
});

// Clear badge when switching tabs
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.action.setBadgeText({ text: '', tabId: activeInfo.tabId });
});

// Clear badge on navigation
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === 'loading') {
    chrome.action.setBadgeText({ text: '', tabId });
  }
});
