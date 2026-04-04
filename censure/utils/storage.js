(function () {
  'use strict';

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

  function saveSettings(settings) {
    return new Promise(function (resolve, reject) {
      chrome.storage.local.set(settings, function () {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve();
        }
      });
    });
  }

  function addKeyword(keyword, category) {
    return getSettings().then(function (settings) {
      if (settings.keywords.indexOf(keyword) === -1) {
        settings.keywords.push(keyword);
      }
      if (category) {
        if (!settings.categories[category]) {
          settings.categories[category] = [];
        }
        if (settings.categories[category].indexOf(keyword) === -1) {
          settings.categories[category].push(keyword);
        }
      }
      return saveSettings({
        keywords: settings.keywords,
        categories: settings.categories
      });
    });
  }

  function removeKeyword(keyword) {
    return getSettings().then(function (settings) {
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
      return saveSettings({
        keywords: settings.keywords,
        categories: cats
      });
    });
  }

  function exportSettings() {
    return getSettings().then(function (settings) {
      return JSON.stringify(settings, null, 2);
    });
  }

  function importSettings(jsonString) {
    var parsed = JSON.parse(jsonString);
    return saveSettings(parsed);
  }

  function isCurrentSiteAllowed() {
    var hostname = window.location.hostname;
    return getSettings().then(function (settings) {
      // Whitelisted sites have filtering DISABLED
      if (settings.siteWhitelist.length > 0 && settings.siteWhitelist.indexOf(hostname) !== -1) {
        return false;
      }
      // Blacklisted sites are explicitly filtered
      if (settings.siteBlacklist.length > 0) {
        return settings.siteBlacklist.indexOf(hostname) !== -1;
      }
      // Default: filtering is active on all sites
      return true;
    });
  }

  function incrementBlockedCount(count) {
    return getSettings().then(function (settings) {
      var newCount = settings.blockedCount + (count || 1);
      return saveSettings({ blockedCount: newCount });
    });
  }

  window.CensureStorage = {
    getSettings: getSettings,
    saveSettings: saveSettings,
    addKeyword: addKeyword,
    removeKeyword: removeKeyword,
    exportSettings: exportSettings,
    importSettings: importSettings,
    isCurrentSiteAllowed: isCurrentSiteAllowed,
    incrementBlockedCount: incrementBlockedCount
  };
})();
