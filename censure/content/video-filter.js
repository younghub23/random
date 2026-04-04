(function () {
  'use strict';

  var settings = null;
  var compiledRegex = null;
  var observer = null;
  var debounceTimer = null;
  var isActive = false;

  var VIDEO_TITLE_SELECTORS = [
    '#video-title',
    'ytd-video-renderer #video-title',
    'ytd-rich-item-renderer #video-title',
    'ytd-compact-video-renderer #video-title',
    '.ytd-video-renderer #video-title'
  ];

  var VIDEO_CONTAINER_SELECTORS = [
    'ytd-rich-item-renderer',
    'ytd-video-renderer',
    'ytd-compact-video-renderer',
    'ytd-reel-item-renderer'
  ];

  function scanVideoPoster(video) {
    if (!video || video.getAttribute('data-censure-video-scanned') === 'true') {
      return;
    }

    video.setAttribute('data-censure-video-scanned', 'true');

    var poster = video.getAttribute('poster');
    if (poster && settings.imageUrlPatterns && settings.imageUrlPatterns.length > 0) {
      if (window.CensureMatching.matchesUrlPattern(poster, settings.imageUrlPatterns)) {
        var container = window.CensureContainer.findContainer(video);
        if (container && !window.CensureContainer.isInsideContainer(video)) {
          window.CensureContainer.hideContainer(container, 1);
        }
      }
    }
  }

  function scanVideoTitles(root) {
    if (!compiledRegex) {
      return;
    }

    for (var s = 0; s < VIDEO_TITLE_SELECTORS.length; s++) {
      var titles = (root || document).querySelectorAll(VIDEO_TITLE_SELECTORS[s]);
      for (var i = 0; i < titles.length; i++) {
        var titleEl = titles[i];
        if (titleEl.getAttribute('data-censure-title-scanned') === 'true') {
          continue;
        }

        titleEl.setAttribute('data-censure-title-scanned', 'true');

        var text = titleEl.textContent || '';
        compiledRegex.lastIndex = 0;

        if (compiledRegex.test(text)) {
          var container = window.CensureContainer.findContainer(titleEl);
          if (container && !window.CensureContainer.isInsideContainer(titleEl)) {
            window.CensureContainer.hideContainer(container, 1);
          }
        }
      }
    }
  }

  function scanChannelNames(root) {
    if (!compiledRegex) {
      return;
    }

    var channelSelectors = [
      'ytd-channel-name',
      '#channel-name',
      '.ytd-channel-name'
    ];

    for (var s = 0; s < channelSelectors.length; s++) {
      var channels = (root || document).querySelectorAll(channelSelectors[s]);
      for (var i = 0; i < channels.length; i++) {
        var channelEl = channels[i];
        if (channelEl.getAttribute('data-censure-channel-scanned') === 'true') {
          continue;
        }

        channelEl.setAttribute('data-censure-channel-scanned', 'true');

        var text = channelEl.textContent || '';
        compiledRegex.lastIndex = 0;

        if (compiledRegex.test(text)) {
          var container = window.CensureContainer.findContainer(channelEl);
          if (container && !window.CensureContainer.isInsideContainer(channelEl)) {
            window.CensureContainer.hideContainer(container, 1);
          }
        }
      }
    }
  }

  function scanSurroundingText(root) {
    if (!compiledRegex) {
      return;
    }

    for (var s = 0; s < VIDEO_CONTAINER_SELECTORS.length; s++) {
      var containers = (root || document).querySelectorAll(VIDEO_CONTAINER_SELECTORS[s]);
      for (var i = 0; i < containers.length; i++) {
        var container = containers[i];
        if (container.getAttribute('data-censure-surrounding-scanned') === 'true') {
          continue;
        }

        container.setAttribute('data-censure-surrounding-scanned', 'true');

        var text = container.textContent || '';
        compiledRegex.lastIndex = 0;

        if (compiledRegex.test(text)) {
          if (!window.CensureContainer.isInsideContainer(container)) {
            window.CensureContainer.hideContainer(container, 1);
          }
        }
      }
    }
  }

  function scanAll(root) {
    // Scan video elements with poster attributes
    var videos = (root || document).querySelectorAll('video[poster]');
    for (var i = 0; i < videos.length; i++) {
      scanVideoPoster(videos[i]);
    }

    // Scan YouTube-specific elements
    scanVideoTitles(root);
    scanChannelNames(root);
    scanSurroundingText(root);
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
              scanAll(node);
            }
          }
        }
      }, 100);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
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

    // Show all hidden containers
    var hiddenContainers = document.querySelectorAll('.censure-hidden-container');
    for (var i = 0; i < hiddenContainers.length; i++) {
      hiddenContainers[i].classList.remove('censure-hidden-container');
    }

    // Remove pills
    var pills = document.querySelectorAll('[data-censure-pill]');
    for (var j = 0; j < pills.length; j++) {
      pills[j].remove();
    }

    // Clear scanned flags
    var scannedVideos = document.querySelectorAll('[data-censure-video-scanned]');
    for (var k = 0; k < scannedVideos.length; k++) {
      scannedVideos[k].removeAttribute('data-censure-video-scanned');
    }

    var scannedTitles = document.querySelectorAll('[data-censure-title-scanned]');
    for (var l = 0; l < scannedTitles.length; l++) {
      scannedTitles[l].removeAttribute('data-censure-title-scanned');
    }

    var scannedChannels = document.querySelectorAll('[data-censure-channel-scanned]');
    for (var m = 0; m < scannedChannels.length; m++) {
      scannedChannels[m].removeAttribute('data-censure-channel-scanned');
    }

    var scannedSurrounding = document.querySelectorAll('[data-censure-surrounding-scanned]');
    for (var n = 0; n < scannedSurrounding.length; n++) {
      scannedSurrounding[n].removeAttribute('data-censure-surrounding-scanned');
    }

    isActive = false;
    compiledRegex = null;
  }

  function init() {
    if (isActive) {
      teardown();
    }

    window.CensureStorage.getSettings().then(function (s) {
      settings = s;

      if (!settings.enabled) {
        return;
      }

      compiledRegex = window.CensureMatching.compilePatterns(settings.keywords);

      isActive = true;

      scanAll(null);
      setupObserver();
    }).catch(function (err) {
      console.error('Censure: video-filter init failed', err);
    });
  }

  chrome.runtime.onMessage.addListener(function (message) {
    if (message.type === 'toggle') {
      if (message.enabled === false) {
        teardown();
      } else if (message.enabled === true) {
        init();
      }
    } else if (message.type === 'settingsUpdated') {
      init();
    }
  });

  window.CensureVideoFilter = {
    init: init
  };

  init();
})();
