(function () {
  'use strict';

  var CONTAINER_SELECTORS = [
    'article',
    '[role="article"]',
    '[data-testid="tweet"]',
    '[data-testid="cellInnerDiv"]',
    '.Post',
    '.comment',
    '.story-card',
    '.card',
    '.feed-item'
  ];

  var MAX_LEVELS = 10;

  function matchesContainerSelector(element) {
    for (var i = 0; i < CONTAINER_SELECTORS.length; i++) {
      try {
        if (element.matches(CONTAINER_SELECTORS[i])) {
          return true;
        }
      } catch (e) {
        // Ignore invalid selector errors
      }
    }
    return false;
  }

  function findContainer(element) {
    if (!element || !element.parentElement) {
      return null;
    }

    var current = element.parentElement;
    var levels = 0;

    while (current && current !== document.body && levels < MAX_LEVELS) {
      if (current.tagName === 'ARTICLE' || matchesContainerSelector(current)) {
        return current;
      }
      current = current.parentElement;
      levels++;
    }

    return null;
  }

  function hideContainer(container, count) {
    if (!container) {
      return;
    }

    container.classList.add('censure-hidden-container');

    var pill = document.createElement('div');
    pill.className = 'censure-hidden-pill';
    pill.textContent = '[Censure: ' + count + ' item(s) hidden \u2014 click to reveal]';
    pill.setAttribute('data-censure-pill', 'true');

    pill.addEventListener('click', function () {
      container.classList.remove('censure-hidden-container');
      pill.remove();

      setTimeout(function () {
        if (container.isConnected) {
          container.classList.add('censure-hidden-container');
          var newPill = document.createElement('div');
          newPill.className = 'censure-hidden-pill';
          newPill.textContent = '[Censure: ' + count + ' item(s) hidden \u2014 click to reveal]';
          newPill.setAttribute('data-censure-pill', 'true');
          container.parentNode.insertBefore(newPill, container);

          newPill.addEventListener('click', function () {
            hideContainer(container, count);
            newPill.remove();
          });
        }
      }, 3000);
    });

    container.parentNode.insertBefore(pill, container);
  }

  function isInsideContainer(element) {
    var current = element;
    while (current && current !== document.body) {
      if (current.classList && current.classList.contains('censure-hidden-container')) {
        return true;
      }
      current = current.parentElement;
    }
    return false;
  }

  window.CensureContainer = {
    findContainer: findContainer,
    hideContainer: hideContainer,
    isInsideContainer: isInsideContainer
  };
})();
