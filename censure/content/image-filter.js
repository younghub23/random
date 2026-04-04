(function () {
  'use strict';

  var settings = null;
  var intersectionObserver = null;
  var mutationObserver = null;
  var mutationDebounceTimer = null;
  var isActive = false;
  var processingCount = 0;
  var MAX_CONCURRENT = 5;
  var imageQueue = [];

  var MIN_SIZE = 50;

  function isIconOrFavicon(img) {
    var src = img.src || '';
    if (src.indexOf('data:image/svg') === 0) {
      return true;
    }
    if (src.indexOf('favicon') !== -1) {
      return true;
    }
    if (img.width > 0 && img.width < MIN_SIZE && img.height > 0 && img.height < MIN_SIZE) {
      return true;
    }
    return false;
  }

  function shouldSkipImage(img) {
    if (img.getAttribute('data-censure-scanned') === 'true') {
      return true;
    }
    if (isIconOrFavicon(img)) {
      return true;
    }
    var src = img.src || '';
    if (!src || src.indexOf('data:image/svg') === 0) {
      return true;
    }
    if (img.naturalWidth > 0 && img.naturalWidth < MIN_SIZE) {
      return true;
    }
    if (img.naturalHeight > 0 && img.naturalHeight < MIN_SIZE) {
      return true;
    }
    return false;
  }

  function blurImage(img) {
    var wrapper = document.createElement('div');
    wrapper.className = 'censure-image-wrapper';

    var parent = img.parentNode;
    parent.insertBefore(wrapper, img);
    wrapper.appendChild(img);

    img.classList.add('censure-image-blurred');

    var overlay = document.createElement('div');
    overlay.className = 'censure-image-overlay';
    overlay.textContent = 'Image hidden by Censure';
    overlay.addEventListener('click', function () {
      img.classList.remove('censure-image-blurred');
      overlay.remove();

      setTimeout(function () {
        if (img.isConnected) {
          img.classList.add('censure-image-blurred');
          wrapper.appendChild(overlay);
        }
      }, 3000);
    });

    wrapper.appendChild(overlay);
  }

  function processImage(img) {
    if (shouldSkipImage(img)) {
      return;
    }

    img.setAttribute('data-censure-scanned', 'true');

    var src = img.src || '';

    // Check against URL patterns
    if (settings.imageUrlPatterns && settings.imageUrlPatterns.length > 0) {
      if (window.CensureMatching.matchesUrlPattern(src, settings.imageUrlPatterns)) {
        blurImage(img);
        return;
      }
    }

    // TODO: Future ML integration for face embedding matching
    // If no URL match and faceEmbeddings exist, run face detection
    // and compare embeddings using cosine similarity against
    // settings.faceEmbeddings with settings.similarityThreshold
  }

  function processQueue() {
    while (processingCount < MAX_CONCURRENT && imageQueue.length > 0) {
      var img = imageQueue.shift();
      processingCount++;
      try {
        processImage(img);
      } finally {
        processingCount--;
      }
    }

    if (imageQueue.length > 0) {
      if (typeof requestIdleCallback === 'function') {
        requestIdleCallback(processQueue);
      } else {
        setTimeout(processQueue, 50);
      }
    }
  }

  function enqueueImage(img) {
    imageQueue.push(img);
  }

  function scheduleProcessing() {
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(processQueue);
    } else {
      setTimeout(processQueue, 50);
    }
  }

  function batchEnqueueImages(images) {
    var arr = Array.prototype.slice.call(images);

    if (arr.length <= 50) {
      for (var i = 0; i < arr.length; i++) {
        enqueueImage(arr[i]);
      }
      scheduleProcessing();
      return;
    }

    // Process in groups of 10 with 200ms delays
    var idx = 0;
    function nextBatch() {
      var end = Math.min(idx + 10, arr.length);
      for (var j = idx; j < end; j++) {
        enqueueImage(arr[j]);
      }
      scheduleProcessing();
      idx = end;
      if (idx < arr.length) {
        setTimeout(nextBatch, 200);
      }
    }
    nextBatch();
  }

  function setupIntersectionObserver() {
    if (intersectionObserver) {
      intersectionObserver.disconnect();
    }

    intersectionObserver = new IntersectionObserver(function (entries) {
      var visibleImages = [];
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          visibleImages.push(entries[i].target);
          intersectionObserver.unobserve(entries[i].target);
        }
      }
      if (visibleImages.length > 0) {
        batchEnqueueImages(visibleImages);
      }
    }, {
      rootMargin: '200px'
    });
  }

  function observeImages(root) {
    var images = (root || document).querySelectorAll('img');
    for (var i = 0; i < images.length; i++) {
      if (!shouldSkipImage(images[i])) {
        intersectionObserver.observe(images[i]);
      }
    }
  }

  function setupMutationObserver() {
    if (mutationObserver) {
      mutationObserver.disconnect();
    }

    mutationObserver = new MutationObserver(function (mutations) {
      if (mutationDebounceTimer) {
        clearTimeout(mutationDebounceTimer);
      }
      mutationDebounceTimer = setTimeout(function () {
        for (var i = 0; i < mutations.length; i++) {
          var addedNodes = mutations[i].addedNodes;
          for (var j = 0; j < addedNodes.length; j++) {
            var node = addedNodes[j];
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.tagName === 'IMG') {
                intersectionObserver.observe(node);
              } else if (node.querySelectorAll) {
                var imgs = node.querySelectorAll('img');
                for (var k = 0; k < imgs.length; k++) {
                  intersectionObserver.observe(imgs[k]);
                }
              }
            }
          }
        }
      }, 100);
    });

    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  function teardown() {
    if (intersectionObserver) {
      intersectionObserver.disconnect();
      intersectionObserver = null;
    }
    if (mutationObserver) {
      mutationObserver.disconnect();
      mutationObserver = null;
    }
    if (mutationDebounceTimer) {
      clearTimeout(mutationDebounceTimer);
      mutationDebounceTimer = null;
    }

    imageQueue = [];
    processingCount = 0;

    // Remove all blur classes and overlays
    var blurred = document.querySelectorAll('.censure-image-blurred');
    for (var i = 0; i < blurred.length; i++) {
      blurred[i].classList.remove('censure-image-blurred');
    }

    var overlays = document.querySelectorAll('.censure-image-overlay');
    for (var j = 0; j < overlays.length; j++) {
      overlays[j].remove();
    }

    // Unwrap image wrappers
    var wrappers = document.querySelectorAll('.censure-image-wrapper');
    for (var k = 0; k < wrappers.length; k++) {
      var wrapper = wrappers[k];
      var img = wrapper.querySelector('img');
      if (img && wrapper.parentNode) {
        wrapper.parentNode.insertBefore(img, wrapper);
        wrapper.remove();
      }
    }

    // Clear scanned flags
    var scanned = document.querySelectorAll('[data-censure-scanned]');
    for (var l = 0; l < scanned.length; l++) {
      scanned[l].removeAttribute('data-censure-scanned');
    }

    isActive = false;
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

      var hasUrlPatterns = settings.imageUrlPatterns && settings.imageUrlPatterns.length > 0;
      var hasFaceEmbeddings = settings.faceEmbeddings && settings.faceEmbeddings.length > 0;

      if (!hasUrlPatterns && !hasFaceEmbeddings) {
        return;
      }

      isActive = true;

      setupIntersectionObserver();
      observeImages(document);
      setupMutationObserver();
    }).catch(function (err) {
      console.error('Censure: image-filter init failed', err);
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

  window.CensureImageFilter = {
    init: init
  };

  init();
})();
