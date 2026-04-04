(function () {
  'use strict';

  var compiledRegex = null;
  var filterMode = 'redact';
  var totalBlockedCount = 0;
  var observer = null;
  var debounceTimer = null;
  var isActive = false;

  var SKIP_TAGS = {
    SCRIPT: true,
    STYLE: true,
    NOSCRIPT: true,
    CODE: true,
    PRE: true
  };

  function isEditable(node) {
    var el = node.parentElement;
    while (el) {
      if (el.isContentEditable) {
        return true;
      }
      el = el.parentElement;
    }
    return false;
  }

  function shouldSkipNode(node) {
    if (!node.parentElement) {
      return true;
    }
    var parent = node.parentElement;
    if (parent.classList && parent.classList.contains('censure-redacted')) {
      return true;
    }
    if (parent.classList && parent.classList.contains('censure-hidden-pill')) {
      return true;
    }
    if (parent.classList && parent.classList.contains('censure-image-overlay')) {
      return true;
    }
    var tag = parent.tagName;
    if (SKIP_TAGS[tag]) {
      return true;
    }
    if (isEditable(node)) {
      return true;
    }
    return false;
  }

  function redactTextNode(textNode) {
    if (!compiledRegex || !textNode.textContent) {
      return 0;
    }

    var text = textNode.textContent;
    compiledRegex.lastIndex = 0;

    if (!compiledRegex.test(text)) {
      return 0;
    }

    compiledRegex.lastIndex = 0;
    var fragment = document.createDocumentFragment();
    var lastIndex = 0;
    var matchCount = 0;
    var match;

    while ((match = compiledRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        fragment.appendChild(document.createTextNode(text.substring(lastIndex, match.index)));
      }

      var span = document.createElement('span');
      span.className = 'censure-redacted';
      span.textContent = match[0];
      fragment.appendChild(span);

      lastIndex = compiledRegex.lastIndex;
      matchCount++;
    }

    if (lastIndex < text.length) {
      fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
    }

    if (matchCount > 0) {
      textNode.parentNode.replaceChild(fragment, textNode);
    }

    return matchCount;
  }

  function hideTextNode(textNode) {
    if (!compiledRegex || !textNode.textContent) {
      return 0;
    }

    var text = textNode.textContent;
    compiledRegex.lastIndex = 0;

    if (!compiledRegex.test(text)) {
      return 0;
    }

    compiledRegex.lastIndex = 0;
    var matches = window.CensureMatching.findMatches(text, compiledRegex);

    if (matches.length === 0) {
      return 0;
    }

    var container = window.CensureContainer.findContainer(textNode);
    if (container && !window.CensureContainer.isInsideContainer(textNode)) {
      window.CensureContainer.hideContainer(container, matches.length);
      return matches.length;
    }

    return 0;
  }

  function scanNode(rootNode) {
    if (!compiledRegex || !rootNode) {
      return;
    }

    var walker = document.createTreeWalker(
      rootNode,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          if (shouldSkipNode(node)) {
            return NodeFilter.FILTER_REJECT;
          }
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    var textNodes = [];
    var current;
    while ((current = walker.nextNode())) {
      textNodes.push(current);
    }

    for (var i = 0; i < textNodes.length; i++) {
      var count;
      if (filterMode === 'hide') {
        count = hideTextNode(textNodes[i]);
      } else {
        count = redactTextNode(textNodes[i]);
      }
      totalBlockedCount += count;
    }
  }

  function scanDocument() {
    scanNode(document.body);
    updateBadge();
  }

  function updateBadge() {
    try {
      chrome.runtime.sendMessage({
        type: 'updateBadge',
        count: totalBlockedCount
      });
    } catch (e) {
      // Extension context may be invalidated
    }
  }

  function handleRedactedClick(e) {
    var target = e.target;
    if (!target.classList || !target.classList.contains('censure-redacted')) {
      return;
    }

    target.classList.add('censure-revealed');

    setTimeout(function () {
      if (target.isConnected) {
        target.classList.remove('censure-revealed');
      }
    }, 3000);
  }

  function setupObserver() {
    if (observer) {
      observer.disconnect();
    }

    observer = new MutationObserver(function (mutations) {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      debounceTimer = setTimeout(function () {
        for (var i = 0; i < mutations.length; i++) {
          var addedNodes = mutations[i].addedNodes;
          for (var j = 0; j < addedNodes.length; j++) {
            var node = addedNodes[j];
            if (node.nodeType === Node.ELEMENT_NODE) {
              scanNode(node);
            } else if (node.nodeType === Node.TEXT_NODE && !shouldSkipNode(node)) {
              var count;
              if (filterMode === 'hide') {
                count = hideTextNode(node);
              } else {
                count = redactTextNode(node);
              }
              totalBlockedCount += count;
            }
          }

          if (mutations[i].type === 'characterData') {
            var target = mutations[i].target;
            if (target.nodeType === Node.TEXT_NODE && !shouldSkipNode(target)) {
              var charCount;
              if (filterMode === 'hide') {
                charCount = hideTextNode(target);
              } else {
                charCount = redactTextNode(target);
              }
              totalBlockedCount += charCount;
            }
          }
        }

        if (totalBlockedCount > 0) {
          updateBadge();
        }
      }, 100);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  function teardown() {
    if (observer) {
      observer.disconnect();
      observer = null;
    }

    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }

    // Unwrap all redacted spans
    var redacted = document.querySelectorAll('.censure-redacted');
    for (var i = 0; i < redacted.length; i++) {
      var span = redacted[i];
      var textNode = document.createTextNode(span.textContent);
      span.parentNode.replaceChild(textNode, span);
    }

    // Show all hidden containers
    var hiddenContainers = document.querySelectorAll('.censure-hidden-container');
    for (var j = 0; j < hiddenContainers.length; j++) {
      hiddenContainers[j].classList.remove('censure-hidden-container');
    }

    // Remove all pills
    var pills = document.querySelectorAll('[data-censure-pill]');
    for (var k = 0; k < pills.length; k++) {
      pills[k].remove();
    }

    totalBlockedCount = 0;
    isActive = false;
    compiledRegex = null;
  }

  function init() {
    if (isActive) {
      teardown();
    }

    window.CensureStorage.getSettings().then(function (settings) {
      if (!settings.enabled) {
        return;
      }

      return window.CensureStorage.isCurrentSiteAllowed().then(function (allowed) {
        if (!allowed) {
          return;
        }

        filterMode = settings.filterMode || 'redact';
        compiledRegex = window.CensureMatching.compilePatterns(settings.keywords);

        if (!compiledRegex) {
          return;
        }

        isActive = true;
        totalBlockedCount = 0;

        scanDocument();
        setupObserver();
        document.addEventListener('click', handleRedactedClick);
      });
    }).catch(function (err) {
      console.error('Censure: text-filter init failed', err);
    });
  }

  chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.type === 'toggle') {
      if (message.enabled === false) {
        teardown();
        document.removeEventListener('click', handleRedactedClick);
      } else if (message.enabled === true) {
        init();
      }
    } else if (message.type === 'settingsUpdated') {
      init();
    } else if (message.type === 'getCount') {
      sendResponse({ count: totalBlockedCount });
    }
  });

  window.CensureTextFilter = {
    init: init,
    scanDocument: scanDocument
  };

  init();
})();
