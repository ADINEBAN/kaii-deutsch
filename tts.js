/**
 * WordFeather - Text-to-Speech (tts.js)
 * Adds pronunciation buttons to vocabulary tables, example sentences, and sentence lists.
 * - German (de-DE): High-quality Thorsten-Voice Kokoro TTS via local development proxy
 *   or custom backend, with automatic graceful fallback to the browser Web Speech API.
 * - English (en-US): Browser built-in Web Speech API.
 */
(function (global) {
  'use strict';

  // Prevent double-initialization
  if (global.WordFeatherTTS && global.WordFeatherTTS._initialized) return;

  var synth = ('speechSynthesis' in global) ? global.speechSynthesis : null;
  var activeBtn = null;
  var activeAudio = null;
  var activeAbortController = null;
  var activeBlobUrl = null;

  // In-memory cache for generated audio blobs: "text|speed" -> Blob
  var audioBlobCache = new Map();
  var MAX_CACHE_ITEMS = 150;

  // Default configuration
  var config = {
    endpoint: null,
    speed: 0.9,
    timeoutMs: 15000,
    fallbackToNative: false, // Do not silently mask Thorsten TTS failures with browser voice
    devProxyEndpoint: '/api/tts',
    localBackendEndpoint: 'http://127.0.0.1:8000/tts'
  };

  // Merge any predefined global configuration
  if (global.WF_TTS_CONFIG && typeof global.WF_TTS_CONFIG === 'object') {
    for (var key in global.WF_TTS_CONFIG) {
      if (Object.prototype.hasOwnProperty.call(global.WF_TTS_CONFIG, key)) {
        config[key] = global.WF_TTS_CONFIG[key];
      }
    }
  }

  function getEffectiveEndpoint() {
    if (global.WF_TTS_ENDPOINT) return global.WF_TTS_ENDPOINT;
    if (config.endpoint) return config.endpoint;

    try {
      var custom = localStorage.getItem('wf_tts_endpoint');
      if (custom && custom.trim()) return custom.trim();
    } catch (e) {}

    var hostname = global.location ? global.location.hostname : '';
    var protocol = global.location ? global.location.protocol : '';
    var isLocal = hostname === 'localhost' ||
                  hostname === '127.0.0.1' ||
                  hostname === '[::1]' ||
                  hostname.endsWith('.local') ||
                  protocol === 'file:';

    if (isLocal) {
      if (protocol === 'file:') {
        return config.localBackendEndpoint;
      }
      return config.devProxyEndpoint;
    }

    // Public deployments without custom backend setting fall back to native speech
    return null;
  }

  function getEffectiveSpeed() {
    try {
      var customSpeed = localStorage.getItem('wf_tts_speed');
      if (customSpeed && !isNaN(parseFloat(customSpeed))) {
        return parseFloat(customSpeed);
      }
    } catch (e) {}
    if (typeof global.WF_TTS_SPEED === 'number') {
      return global.WF_TTS_SPEED;
    }
    return config.speed;
  }

  // Inject styles for speaker buttons, loading spinners, error states, and dark mode
  var style = document.createElement('style');
  style.id = 'wf-tts-styles';
  style.textContent =
    '.tts-btn, .d-tts{' +
      'display:inline-flex;align-items:center;justify-content:center;' +
      'width:24px;height:24px;border:none;background:none;' +
      'cursor:pointer;opacity:0.4;transition:opacity 0.2s, background-color 0.2s, color 0.2s;' +
      'padding:0;margin-left:4px;vertical-align:middle;flex-shrink:0;' +
      'border-radius:50%;font-size:14px;line-height:1;position:relative;' +
    '}' +
    '.d-tts{width:22px;height:22px;margin-left:3px;font-size:13px;opacity:0.35;}' +
    '@media (hover:none){.d-tts{opacity:.7;width:28px;height:28px;}}' +
    '.tts-btn:hover, .d-tts:hover{opacity:0.85;background:rgba(29,78,216,0.1);}' +
    '.tts-btn.playing, .d-tts.playing{opacity:1;color:#1d4ed8;background:rgba(29,78,216,0.15);}' +
    '.tts-btn.loading, .d-tts.loading{opacity:0.9;color:#1d4ed8;background:rgba(29,78,216,0.1);cursor:wait;}' +
    '.tts-btn.error, .d-tts.error{opacity:1;color:#dc2626 !important;background:rgba(220,38,38,0.15) !important;}' +
    '.tts-btn svg{width:14px;height:14px;fill:currentColor;}' +
    '.d-tts svg{width:13px;height:13px;fill:currentColor;}' +
    '.tts-btn svg.tts-spin-icon, .d-tts svg.tts-spin-icon{animation:wf-tts-spin 0.75s linear infinite;fill:none;stroke:currentColor;}' +
    '@keyframes wf-tts-spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}' +
    '@keyframes wf-tts-fade-in{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}' +
    'td .tts-wrap{display:flex;align-items:center;gap:2px;}' +
    'td .tts-wrap span{flex:1;}' +
    '[data-bs-theme="dark"] .tts-btn:hover, [data-bs-theme="dark"] .d-tts:hover{background:rgba(99,102,241,0.2);}' +
    '[data-bs-theme="dark"] .tts-btn.playing, [data-bs-theme="dark"] .d-tts.playing{color:#818cf8;background:rgba(99,102,241,0.25);}' +
    '[data-bs-theme="dark"] .tts-btn.loading, [data-bs-theme="dark"] .d-tts.loading{color:#818cf8;background:rgba(99,102,241,0.2);}' +
    '[data-bs-theme="dark"] .tts-btn.error, [data-bs-theme="dark"] .d-tts.error{color:#f87171 !important;background:rgba(239,68,68,0.25) !important;}';

  if (!document.getElementById('wf-tts-styles') && document.head) {
    document.head.appendChild(style);
  }

  // Speaker SVG icon
  var speakerSVG = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>' +
    '</svg>';

  // Subtle spinner SVG icon during Thorsten TTS generation
  var spinnerSVG = '<svg viewBox="0 0 24 24" class="tts-spin-icon" xmlns="http://www.w3.org/2000/svg" stroke-width="2.5" stroke-linecap="round">' +
    '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-opacity="0.25"/>' +
    '<path d="M12 3a9 9 0 0 1 9 9" stroke="currentColor"/>' +
    '</svg>';

  function cleanText(text) {
    if (!text) return '';
    return text
      .replace(/\s*[,]\s*-[^\s,()]+/g, '')  // Remove plural forms like ", -e", ", -¨er"
      .replace(/[—–]/g, ' ')                 // Replace dashes with spaces
      .replace(/\(.*?\)/g, '')               // Remove parenthetical notes
      .replace(/\s+/g, ' ')
      .trim();
  }

  function setButtonState(btn, state) {
    if (!btn) return;
    btn.classList.remove('playing', 'loading', 'error');
    if (state === 'loading') {
      btn.classList.add('loading');
      if (!btn._originalSvg) btn._originalSvg = btn.innerHTML;
      btn.innerHTML = spinnerSVG;
      btn.setAttribute('aria-busy', 'true');
    } else if (state === 'playing') {
      btn.classList.add('playing');
      if (btn._originalSvg) btn.innerHTML = btn._originalSvg;
      btn.removeAttribute('aria-busy');
    } else if (state === 'error') {
      btn.classList.add('error');
      if (btn._originalSvg) btn.innerHTML = btn._originalSvg;
      btn.removeAttribute('aria-busy');
    } else {
      // idle / reset
      if (btn._originalSvg) btn.innerHTML = btn._originalSvg;
      btn.removeAttribute('aria-busy');
    }
  }

  function showTtsErrorNotice(message, endpoint) {
    var existing = document.getElementById('wf-tts-error-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.id = 'wf-tts-error-toast';
    toast.setAttribute('role', 'alert');
    toast.innerHTML =
      '<div style="display:flex;align-items:flex-start;gap:10px;">' +
        '<span style="font-size:16px;line-height:1;margin-top:2px;">⚠️</span>' +
        '<div style="flex:1;">' +
          '<div style="font-weight:600;font-size:13px;margin-bottom:2px;">Thorsten-Voice TTS Fehler</div>' +
          '<div style="font-size:12px;opacity:0.9;line-height:1.4;">' + (message || 'Unbekannter Fehler') + '</div>' +
          (endpoint ? '<div style="font-size:11px;opacity:0.75;margin-top:4px;font-family:monospace;">Endpoint: ' + endpoint + '</div>' : '') +
        '</div>' +
        '<button type="button" aria-label="Schließen" style="border:none;background:none;color:inherit;cursor:pointer;padding:0;font-size:16px;line-height:1;opacity:0.7;">&times;</button>' +
      '</div>';

    toast.style.cssText =
      'position:fixed;bottom:20px;right:20px;z-index:99999;max-width:380px;' +
      'padding:12px 14px;border-radius:8px;' +
      'background:#fef2f2;color:#991b1b;border:1px solid #f87171;' +
      'box-shadow:0 10px 25px -5px rgba(0,0,0,0.2);' +
      'font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;' +
      'transition:opacity 0.25s ease;animation:wf-tts-fade-in 0.2s ease;';

    if (document.documentElement.getAttribute('data-bs-theme') === 'dark' ||
        document.body.getAttribute('data-bs-theme') === 'dark') {
      toast.style.background = '#450a0a';
      toast.style.color = '#fca5a5';
      toast.style.borderColor = '#991b1b';
    }

    var closeBtn = toast.querySelector('button');
    if (closeBtn) {
      closeBtn.onclick = function() { toast.remove(); };
    }

    document.body.appendChild(toast);
    setTimeout(function () {
      if (toast.parentNode) {
        toast.style.opacity = '0';
        setTimeout(function () { if (toast.parentNode) toast.remove(); }, 300);
      }
    }, 6000);
  }

  function stopAll() {
    if (activeAbortController) {
      try { activeAbortController.abort(); } catch (e) {}
      activeAbortController = null;
    }
    if (activeAudio) {
      try {
        activeAudio.pause();
        activeAudio.currentTime = 0;
        activeAudio.src = '';
      } catch (e) {}
      activeAudio = null;
    }
    if (activeBlobUrl) {
      try { URL.revokeObjectURL(activeBlobUrl); } catch (e) {}
      activeBlobUrl = null;
    }
    if (synth) {
      try { synth.cancel(); } catch (e) {}
    }
    if (activeBtn) {
      setButtonState(activeBtn, 'idle');
      activeBtn = null;
    }
  }

  function speakNative(text, lang, btn, callbacks) {
    if (!synth) {
      if (btn) setButtonState(btn, 'idle');
      if (callbacks && callbacks.onError) callbacks.onError(new Error('SpeechSynthesis not available'));
      return;
    }

    try { synth.cancel(); } catch (e) {}

    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = (lang === 'de-DE') ? 0.9 : 0.95;

    var voices = synth.getVoices();
    var langPrefix = lang.split('-')[0];
    var bestVoice = null;
    for (var i = 0; i < voices.length; i++) {
      if (voices[i].lang.indexOf(langPrefix) === 0) {
        bestVoice = voices[i];
        if (voices[i].name.indexOf('Enhanced') > -1 ||
            voices[i].name.indexOf('Premium') > -1 ||
            voices[i].name.indexOf('Natural') > -1) {
          break;
        }
      }
    }
    if (bestVoice) utterance.voice = bestVoice;

    // If browser has no voices at all (e.g. Brave or Linux Chromium without speech-dispatcher),
    // immediately fall back to direct audio stream for English
    if (!bestVoice && (!voices || voices.length === 0) && lang && lang.indexOf('en') === 0) {
      playDirectAudio(text, 'en', btn, callbacks);
      return;
    }

    if (btn) {
      setButtonState(btn, 'playing');
      activeBtn = btn;
    }

    if (callbacks && callbacks.onStart) callbacks.onStart();

    utterance.onend = function () {
      if (btn && activeBtn === btn) {
        setButtonState(btn, 'idle');
        activeBtn = null;
      }
      if (callbacks && callbacks.onEnd) callbacks.onEnd();
    };

    utterance.onerror = function (e) {
      if (btn && activeBtn === btn) {
        setButtonState(btn, 'idle');
        activeBtn = null;
      }
      if (lang && lang.indexOf('en') === 0) {
        console.warn('[WordFeather TTS] speakNative failed, falling back to direct audio stream');
        playDirectAudio(text, 'en', btn, callbacks);
        return;
      }
      if (callbacks && callbacks.onError) callbacks.onError(e);
    };

    synth.speak(utterance);
  }

  function playAudioBlob(blob, btn, callbacks) {
    if (activeBlobUrl) {
      try { URL.revokeObjectURL(activeBlobUrl); } catch (e) {}
      activeBlobUrl = null;
    }

    var blobUrl = URL.createObjectURL(blob);
    activeBlobUrl = blobUrl;
    var audio = new Audio(blobUrl);
    audio.src = blobUrl;
    audio.preload = 'auto';
    activeAudio = audio;

    console.log('[WordFeather TTS] Audio blob ready for playback:', {
      size: blob.size,
      type: blob.type,
      blobUrl: blobUrl
    });

    if (btn) {
      setButtonState(btn, 'playing');
      activeBtn = btn;
    }

    if (callbacks && callbacks.onStart) callbacks.onStart();

    function cleanup() {
      if (activeAudio === audio) activeAudio = null;
      if (activeBlobUrl === blobUrl) {
        try { URL.revokeObjectURL(blobUrl); } catch (e) {}
        activeBlobUrl = null;
      }
      if (btn && activeBtn === btn) {
        setButtonState(btn, 'idle');
        activeBtn = null;
      }
    }

    audio.onended = function () {
      console.log('[WordFeather TTS] Audio playback ended successfully');
      cleanup();
      if (callbacks && callbacks.onEnd) callbacks.onEnd();
    };

    audio.onerror = function (err) {
      var mediaErr = audio.error ? ('code ' + audio.error.code + ': ' + (audio.error.message || 'unknown')) : 'unknown';
      console.error('[WordFeather TTS] Audio playback error:', mediaErr, err);
      cleanup();
      if (callbacks && callbacks.onError) callbacks.onError(err || audio.error);
    };

    var playPromise = audio.play();
    if (playPromise && typeof playPromise.catch === 'function') {
      playPromise.catch(function (err) {
        console.error('[WordFeather TTS] audio.play() rejected:', err.name, err.message);
        cleanup();
        if (callbacks && callbacks.onError) callbacks.onError(err);
      });
    }
  }

  function fetchServerAudio(text, speed, lang, endpoint, signal) {
    var isGerman = (!lang || lang === 'de-DE' || lang.indexOf('de') === 0);
    console.log('[WordFeather TTS] Requesting ' + (isGerman ? 'German' : 'English') + ' TTS:', {
      endpoint: endpoint,
      lang: lang || (isGerman ? 'de-DE' : 'en-US'),
      textPreview: text.length > 40 ? text.substring(0, 40) + '...' : text,
      textLength: text.length,
      speed: speed
    });
    return fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'audio/wav, audio/mpeg, audio/*;q=0.9, */*;q=0.8'
      },
      body: JSON.stringify({
        text: text,
        speed: speed,
        lang: lang || (isGerman ? 'de-DE' : 'en-US')
      }),
      signal: signal
    }).then(function (res) {
      var contentType = res.headers.get('Content-Type') || '';
      console.log('[WordFeather TTS] Response received:', {
        endpoint: endpoint,
        status: res.status,
        statusText: res.statusText,
        contentType: contentType
      });
      if (!res.ok) {
        throw new Error('TTS service returned HTTP ' + res.status + ' (' + res.statusText + ')');
      }
      if (!contentType.toLowerCase().includes('audio/')) {
        throw new Error('TTS service returned non-audio Content-Type: ' + contentType);
      }
      return res.blob();
    });
  }

  // Alias for backward compatibility
  var fetchThorstenAudio = function(text, speed, endpoint, signal) {
    return fetchServerAudio(text, speed, 'de-DE', endpoint, signal);
  };

  function speakGermanThorsten(text, btn, callbacks) {
    var endpoint = getEffectiveEndpoint();
    var speed = getEffectiveSpeed();

    // If no endpoint is configured (e.g. public static deployment), fall back to native speech
    if (!endpoint) {
      console.log('[WordFeather TTS] No TTS endpoint configured; using native browser speech.');
      speakNative(text, 'de-DE', btn, callbacks);
      return;
    }

    // Stop native speech so it never overlaps with Thorsten playback
    if (synth) {
      try { synth.cancel(); } catch (e) {}
    }

    // Check in-memory cache first
    var cacheKey = text + '|' + speed;
    if (audioBlobCache.has(cacheKey)) {
      console.log('[WordFeather TTS] Using cached audio for:', text.substring(0, 30));
      var cachedBlob = audioBlobCache.get(cacheKey);
      playAudioBlob(cachedBlob, btn, callbacks);
      return;
    }

    if (btn) {
      setButtonState(btn, 'loading');
      activeBtn = btn;
    }

    var controller = new AbortController();
    activeAbortController = controller;

    var timeoutId = setTimeout(function () {
      controller.abort();
    }, config.timeoutMs);

    function attemptFetch(urlToTry, allowFallbackToDirect) {
      return fetchThorstenAudio(text, speed, urlToTry, controller.signal)
        .catch(function (err) {
          // If the relative dev-proxy failed (e.g. 404 because user ran plain python -m http.server),
          // try direct backend once if allowed and not aborted
          if (allowFallbackToDirect &&
              urlToTry === config.devProxyEndpoint &&
              err.name !== 'AbortError' &&
              config.localBackendEndpoint) {
            console.warn('[WordFeather TTS] Dev proxy at ' + urlToTry + ' failed (' + err.message + '). Attempting direct backend at ' + config.localBackendEndpoint);
            return attemptFetch(config.localBackendEndpoint, false);
          }
          throw err;
        });
    }

    attemptFetch(endpoint, endpoint === config.devProxyEndpoint)
      .then(function (blob) {
        clearTimeout(timeoutId);
        if (activeAbortController !== controller) return; // User stopped or switched
        activeAbortController = null;

        // Cache blob (bounded FIFO eviction)
        if (audioBlobCache.size >= MAX_CACHE_ITEMS) {
          var firstKey = audioBlobCache.keys().next().value;
          audioBlobCache.delete(firstKey);
        }
        audioBlobCache.set(cacheKey, blob);

        playAudioBlob(blob, btn, callbacks);
      })
      .catch(function (err) {
        clearTimeout(timeoutId);
        if (activeAbortController === controller) {
          activeAbortController = null;
        }

        // If cancelled by user clicking the button again or another button, do nothing
        if (err.name === 'AbortError') {
          if (btn && activeBtn === btn) {
            setButtonState(btn, 'idle');
            activeBtn = null;
          }
          return;
        }

        console.error('[WordFeather TTS] Thorsten-Voice failed at ' + endpoint + ' (' + err.message + ').');

        if (btn && activeBtn === btn) {
          setButtonState(btn, 'error');
          btn.setAttribute('title', 'TTS-Fehler: ' + err.message);
          activeBtn = null;
          setTimeout(function () {
            if (btn && !btn.classList.contains('playing')) {
              setButtonState(btn, 'idle');
              btn.setAttribute('title', 'Anhören');
            }
          }, 4000);
        }

        showTtsErrorNotice(err.message, endpoint);

        if (config.fallbackToNative) {
          console.warn('[WordFeather TTS] Explicit fallbackToNative enabled: using browser native speech.');
          speakNative(text, 'de-DE', btn, callbacks);
        } else {
          if (callbacks && callbacks.onError) callbacks.onError(err);
        }
      });
  }

  function speakEnglish(text, btn, callbacks) {
    var endpoint = getEffectiveEndpoint();
    var speed = getEffectiveSpeed();

    // Stop native speech if any
    if (synth) {
      try { synth.cancel(); } catch (e) {}
    }

    // Check in-memory cache first: "en|text|speed" -> Blob
    var cacheKey = 'en|' + text + '|' + speed;
    if (audioBlobCache.has(cacheKey)) {
      console.log('[WordFeather TTS] Using cached English audio for:', text.substring(0, 30));
      var cachedBlob = audioBlobCache.get(cacheKey);
      playAudioBlob(cachedBlob, btn, callbacks);
      return;
    }

    if (btn) {
      setButtonState(btn, 'loading');
      activeBtn = btn;
    }

    // If dev server endpoint is available, try fetching audio from /api/tts
    if (endpoint) {
      var controller = new AbortController();
      activeAbortController = controller;

      var timeoutId = setTimeout(function () {
        controller.abort();
      }, config.timeoutMs);

      fetchServerAudio(text, speed, 'en-US', endpoint, controller.signal)
        .then(function (blob) {
          clearTimeout(timeoutId);
          if (activeAbortController !== controller) return;
          activeAbortController = null;

          if (audioBlobCache.size >= MAX_CACHE_ITEMS) {
            var firstKey = audioBlobCache.keys().next().value;
            audioBlobCache.delete(firstKey);
          }
          audioBlobCache.set(cacheKey, blob);

          playAudioBlob(blob, btn, callbacks);
        })
        .catch(function (err) {
          clearTimeout(timeoutId);
          if (activeAbortController === controller) {
            activeAbortController = null;
          }
          if (err.name === 'AbortError') {
            if (btn && activeBtn === btn) {
              setButtonState(btn, 'idle');
              activeBtn = null;
            }
            return;
          }
          console.warn('[WordFeather TTS] Server English TTS failed (' + err.message + '). Trying browser speech / direct audio fallback.');
          speakEnglishFallback(text, btn, callbacks);
        });
      return;
    }

    // No dev server endpoint -> use browser speech or direct audio stream
    speakEnglishFallback(text, btn, callbacks);
  }

  function speakEnglishFallback(text, btn, callbacks) {
    // Check if browser native speech actually has English voices available
    var hasNativeEnglishVoice = false;
    if (synth && synth.getVoices) {
      try {
        var voices = synth.getVoices();
        for (var i = 0; i < voices.length; i++) {
          if (voices[i].lang && voices[i].lang.indexOf('en') === 0) {
            hasNativeEnglishVoice = true;
            break;
          }
        }
      } catch (e) {}
    }

    if (hasNativeEnglishVoice) {
      speakNative(text, 'en-US', btn, {
        onStart: callbacks ? callbacks.onStart : null,
        onEnd: callbacks ? callbacks.onEnd : null,
        onError: function (err) {
          console.warn('[WordFeather TTS] Native speech failed, falling back to direct audio stream:', err);
          playDirectAudio(text, 'en', btn, callbacks);
        }
      });
    } else {
      // Browser has no English voices (e.g. Brave, Chromium on Linux)
      playDirectAudio(text, 'en', btn, callbacks);
    }
  }

  function playDirectAudio(text, lang, btn, callbacks) {
    if (activeAudio) {
      try { activeAudio.pause(); activeAudio.currentTime = 0; } catch (e) {}
      activeAudio = null;
    }

    var directUrl = 'https://translate.google.com/translate_tts?ie=UTF-8&tl=' + encodeURIComponent(lang || 'en') + '&client=tw-ob&q=' + encodeURIComponent(text);
    var audio = new Audio(directUrl);
    activeAudio = audio;

    if (btn) {
      setButtonState(btn, 'playing');
      activeBtn = btn;
    }

    if (callbacks && callbacks.onStart) callbacks.onStart();

    function cleanup() {
      if (activeAudio === audio) activeAudio = null;
      if (btn && activeBtn === btn) {
        setButtonState(btn, 'idle');
        activeBtn = null;
      }
    }

    audio.onended = function () {
      cleanup();
      if (callbacks && callbacks.onEnd) callbacks.onEnd();
    };

    audio.onerror = function (err) {
      cleanup();
      if (btn) {
        setButtonState(btn, 'error');
        setTimeout(function () {
          if (btn) setButtonState(btn, 'idle');
        }, 3000);
      }
      if (callbacks && callbacks.onError) callbacks.onError(err);
    };

    var p = audio.play();
    if (p && typeof p.catch === 'function') {
      p.catch(function (err) {
        cleanup();
        if (btn) {
          setButtonState(btn, 'error');
          setTimeout(function () {
            if (btn) setButtonState(btn, 'idle');
          }, 3000);
        }
        if (callbacks && callbacks.onError) callbacks.onError(err);
      });
    }
  }

  function speak(rawText, lang, btn, callbacks) {
    var text = cleanText(rawText);
    if (!text) return;

    // If clicking the currently playing or loading button, stop it immediately
    if (activeBtn && activeBtn === btn) {
      stopAll();
      return;
    }

    // Stop previous audio/speech cleanly
    stopAll();

    var langStr = String(lang || '').toLowerCase();
    if (langStr.indexOf('de') === 0) {
      speakGermanThorsten(text, btn, callbacks);
    } else if (langStr.indexOf('en') === 0) {
      speakEnglish(text, btn, callbacks);
    } else {
      speakNative(text, lang || 'en-US', btn, callbacks);
    }
  }

  function createBtn(text, lang) {
    var btn = document.createElement('button');
    btn.className = 'tts-btn';
    btn.innerHTML = speakerSVG;
    btn._originalSvg = speakerSVG;
    btn.setAttribute('aria-label', lang === 'de-DE' ? 'Aussprache anhören' : 'Listen to pronunciation');
    btn.setAttribute('title', lang === 'de-DE' ? 'Anhören' : 'Listen');
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      speak(text, lang, btn);
    });
    return btn;
  }

  function addButtonsToExampleSentences() {
    document.querySelectorAll('.ex-de').forEach(function (el) { wrapInlineText(el, 'de-DE'); });
    document.querySelectorAll('.ex-en').forEach(function (el) { wrapInlineText(el, 'en-US'); });
  }

  function wrapInlineText(el, lang) {
    if (el.querySelector('.d-tts') || el.querySelector('.tts-btn')) return;
    if (el.nextElementSibling && (el.nextElementSibling.classList.contains('tts-btn') || el.nextElementSibling.classList.contains('d-tts'))) return;
    var text = el.textContent.trim();
    if (!text || text === '—' || text === '-') return;
    el.parentNode.insertBefore(createBtn(text, lang), el.nextSibling);
  }

  function addButtonsToPersonDrills() {
    document.querySelectorAll('.word-person-drill tbody tr').forEach(function (row) {
      var cells = row.querySelectorAll('td');
      if (cells.length < 2) return;
      if (cells[0].querySelector('.d-tts') || cells[0].querySelector('.tts-btn')) return;
      wrapCell(cells[0], 'de-DE');
      wrapCell(cells[1], 'en-US');
    });
  }

  function addButtonsToTables() {
    var tables = document.querySelectorAll('table');

    tables.forEach(function (table) {
      if (table.closest('.word-person-drill')) return;

      var headers = table.querySelectorAll('thead th');
      
      // Dictionary page: no thead, uses de-col/en-col classes
      if (headers.length === 0) {
        var deColCells = table.querySelectorAll('td.de-col');
        var enColCells = table.querySelectorAll('td.en-col');
        if (deColCells.length > 0) {
          deColCells.forEach(function (cell) { wrapCell(cell, 'de-DE'); });
          enColCells.forEach(function (cell) { wrapCell(cell, 'en-US'); });
          return;
        }
        return;
      }

      // Build column map (supports duplicate headers like Deutsch, Englisch, Deutsch, Englisch)
      var colMap = { de: [], en: [] };
      headers.forEach(function (th, i) {
        var text = th.textContent.trim().toLowerCase();
        if (text === 'deutsch' || text === 'kollokation' || text === 'wendung' ||
            text === 'einfaches verb' || text === 'bedeutung' ||
            text === 'neutral') {
          colMap.de.push(i);
        } else if (text === 'englisch') {
          colMap.en.push(i);
        }
      });

      if (colMap.de.length === 0 && colMap.en.length === 0) return;

      var rows = table.querySelectorAll('tbody tr');
      rows.forEach(function (row) {
        var cells = row.querySelectorAll('td');
        if (cells.length === 0) return;

        colMap.de.forEach(function (idx) {
          if (cells[idx]) wrapCell(cells[idx], 'de-DE');
        });

        colMap.en.forEach(function (idx) {
          if (cells[idx]) wrapCell(cells[idx], 'en-US');
        });
      });
    });

    addButtonsToExampleSentences();
    addButtonsToPersonDrills();

    var path = global.location ? global.location.pathname : '';
    if (path.indexOf('Saetze') > -1) {
      addButtonsToSaetze();
    } else {
      addButtonsToSprechen();
    }
  }

  function addButtonsToSprechen() {
    var items = document.querySelectorAll('.markdown-content ul li, .markdown-content ol li');

    items.forEach(function (li) {
      if (li.querySelector('.tts-btn') || li.querySelector('.d-tts')) return;

      var strongs = li.querySelectorAll('strong');
      var ems = li.querySelectorAll('em');

      if (strongs.length === 0) return;

      strongs.forEach(function (el) {
        var text = el.textContent.trim();
        if (text && text !== '—' && text.length > 1) {
          el.parentNode.insertBefore(createBtn(text, 'de-DE'), el.nextSibling);
        }
      });

      ems.forEach(function (el) {
        var text = el.textContent.trim();
        if (text && text !== '—' && text.length > 1) {
          el.parentNode.insertBefore(createBtn(text, 'en-US'), el.nextSibling);
        }
      });
    });
  }

  function addButtonsToSaetze() {
    var items = document.querySelectorAll('.markdown-content ol li');

    items.forEach(function (li) {
      if (li.querySelector('.tts-btn') || li.querySelector('.d-tts')) return;
      var strong = li.querySelector('strong');
      if (!strong) return;

      var viEl = li.querySelector('.vi-trans, .word-vi, .ex-vi');
      var viClone = viEl ? viEl.cloneNode(true) : null;
      if (viEl) viEl.remove();

      var germanText = strong.textContent.trim();
      var fullText = li.textContent.trim();

      var parts = fullText.split(/\s*[—–]\s*/);
      var englishText = parts.length > 1 ? parts.slice(1).join(' — ').trim() : '';

      var wrapper = document.createElement('span');

      var deSpan = document.createElement('strong');
      deSpan.textContent = germanText;
      wrapper.appendChild(deSpan);
      wrapper.appendChild(createBtn(germanText, 'de-DE'));

      if (englishText) {
        var dash = document.createTextNode(' — ');
        wrapper.appendChild(dash);

        var enSpan = document.createElement('span');
        enSpan.textContent = englishText;
        wrapper.appendChild(enSpan);
        wrapper.appendChild(createBtn(englishText, 'en-US'));
      }

      li.innerHTML = '';
      li.appendChild(wrapper);
      if (viClone) {
        li.appendChild(viClone);
      }
    });
  }

  function wrapCell(cell, lang) {
    if (cell.querySelector('.tts-wrap') || cell.querySelector('.d-tts') || cell.querySelector('.tts-btn')) return;

    var viEl = cell.querySelector('.word-vi, .ex-vi, .vi-trans');
    var viClone = viEl ? viEl.cloneNode(true) : null;
    if (viEl) viEl.remove();

    var text = cell.textContent.trim();
    if (!text || text === '—' || text === '-') {
      if (viClone) cell.appendChild(viClone);
      return;
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'tts-wrap';
    var span = document.createElement('span');
    span.innerHTML = cell.innerHTML;
    wrapper.appendChild(span);
    wrapper.appendChild(createBtn(text, lang));
    cell.innerHTML = '';
    cell.appendChild(wrapper);
    if (viClone) {
      cell.appendChild(viClone);
    }
  }

  // Initialization
  var initialized = false;
  function init() {
    if (initialized) return;
    initialized = true;
    addButtonsToTables();
  }

  // Public API
  global.WordFeatherTTS = {
    _initialized: true,
    speak: speak,
    speakGerman: speakGermanThorsten,
    speakEnglish: speakEnglish,
    speakNative: speakNative,
    playDirectAudio: playDirectAudio,
    stop: stopAll,
    createBtn: createBtn,
    cleanText: cleanText,
    getEndpoint: getEffectiveEndpoint,
    setEndpoint: function (url) {
      config.endpoint = url;
      try {
        if (url) localStorage.setItem('wf_tts_endpoint', url);
        else localStorage.removeItem('wf_tts_endpoint');
      } catch (e) {}
    },
    getSpeed: getEffectiveSpeed,
    setSpeed: function (s) {
      config.speed = s;
      try {
        if (s) localStorage.setItem('wf_tts_speed', String(s));
        else localStorage.removeItem('wf_tts_speed');
      } catch (e) {}
    },
    checkHealth: function () {
      var ep = getEffectiveEndpoint();
      if (!ep) return Promise.resolve({ ok: false, reason: 'No endpoint configured (using native speech)' });
      var healthUrl = ep.replace(/\/tts$/, '/health').replace(/\/api\/tts$/, '/api/tts/health');
      return fetch(healthUrl)
        .then(function (r) { return r.json(); })
        .then(function (data) { return { ok: true, data: data, url: healthUrl }; })
        .catch(function (err) { return { ok: false, error: err.message, url: healthUrl }; });
    },
    config: config,
    init: init
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // If voices list is updated later, refresh voices
  if (synth && synth.addEventListener) {
    synth.addEventListener('voiceschanged', function () {
      // Warm up voices for English
      try { synth.getVoices(); } catch (e) {}
    });
  }

})(typeof window !== 'undefined' ? window : this);
