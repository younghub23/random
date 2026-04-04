(function () {
  'use strict';

  var cache = {
    serialized: null,
    regex: null
  };

  function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function compilePatterns(keywords) {
    if (!keywords || keywords.length === 0) {
      return null;
    }

    var serialized = JSON.stringify(keywords);
    if (cache.serialized === serialized && cache.regex) {
      return cache.regex;
    }

    var escaped = keywords.map(escapeRegExp);
    var pattern = '\\b(' + escaped.join('|') + ')\\b';
    var compiled = new RegExp(pattern, 'gi');

    cache.serialized = serialized;
    cache.regex = compiled;

    return compiled;
  }

  function findMatches(textContent, compiledRegex) {
    var results = [];
    if (!compiledRegex || !textContent) {
      return results;
    }

    compiledRegex.lastIndex = 0;
    var match;
    while ((match = compiledRegex.exec(textContent)) !== null) {
      results.push({
        match: match[0],
        index: match.index,
        length: match[0].length
      });
    }

    return results;
  }

  function matchesUrlPattern(url, patterns) {
    if (!url || !patterns || patterns.length === 0) {
      return false;
    }

    for (var i = 0; i < patterns.length; i++) {
      var escaped = patterns[i].replace(/[.+?^${}()|[\]\\]/g, '\\$&');
      var regexStr = '^' + escaped.replace(/\*/g, '.*') + '$';
      var regex = new RegExp(regexStr, 'i');
      if (regex.test(url)) {
        return true;
      }
    }

    return false;
  }

  window.CensureMatching = {
    compilePatterns: compilePatterns,
    findMatches: findMatches,
    matchesUrlPattern: matchesUrlPattern
  };
})();
