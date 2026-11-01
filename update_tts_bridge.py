import os

new_code = """  // ==========================================================================
  // Smart 3-Tier Speech Engine (Local LAN Thorsten -> Android Native Cloud/Offline -> Web Speech)
  // ==========================================================================
  let SERVER_BASE_URL = (localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080').replace(/\\/m\\/?$/, '').replace(/\\/+$/, '');
  let isLocalServerLive = false;
  let currentTtsButton = null;

  window.onNativeTtsStateChange = function(isSpeaking) {
    if (!isSpeaking && currentTtsButton) {
      currentTtsButton.classList.remove('playing');
      currentTtsButton = null;
    }
  };

  async function checkTtsServer() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const res = await fetch(`${SERVER_BASE_URL}/api/tts/health`, {
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        isLocalServerLive = true;
        state.isTtsOnline = true;
        if (el.serverStatusPill) {
          el.serverStatusPill.className = 'server-status-pill';
          el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Thorsten (LAN)';
        }
        return;
      }
    } catch {
      // Local server offline
    }

    isLocalServerLive = false;
    state.isTtsOnline = true;
    if (el.serverStatusPill) {
      el.serverStatusPill.className = 'server-status-pill';
      el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Giọng Cloud 24/7';
    }
  }

  async function playTTS(text, buttonEl) {
    if (!text) return;
    const cleanText = text.trim();

    if (currentTtsButton && currentTtsButton !== buttonEl) {
      currentTtsButton.classList.remove('playing');
    }
    currentTtsButton = buttonEl;
    if (buttonEl) buttonEl.classList.add('playing');

    // 1. Check in-memory audio blob cache (for local Thorsten)
    if (state.audioCache.has(cleanText)) {
      const audioUrl = state.audioCache.get(cleanText);
      playAudioUrl(audioUrl, buttonEl);
      return;
    }

    // 2. Priority 1: If Local Laptop Server is running, use local Thorsten Kokoro TTS
    if (isLocalServerLive) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        const res = await fetch(`${SERVER_BASE_URL}/api/tts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: cleanText, speed: 0.95 }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          const blob = await res.blob();
          const audioUrl = URL.createObjectURL(blob);
          state.audioCache.set(cleanText, audioUrl);
          playAudioUrl(audioUrl, buttonEl);
          return;
        }
      } catch (err) {
        console.warn('Local TTS failed, switching to Native/Cloud:', err);
      }
    }

    // 3. Priority 2: Android Native Bridge (Android APK: Plays Cloud Neural Voice + Caches to disk + Native MediaPlayer)
    if (window.AndroidTTS && typeof window.AndroidTTS.speak === 'function') {
      try {
        const ok = window.AndroidTTS.speak(cleanText);
        if (ok) return;
      } catch (err) {
        console.warn('AndroidTTS error:', err);
      }
    }

    // 4. Priority 3: Fallback for Desktop Browsers (Outside APK)
    playWebSpeech(cleanText, buttonEl);
  }

  function playAudioUrl(url, buttonEl) {
    if (state.currentAudio) {
      state.currentAudio.pause();
      state.currentAudio = null;
    }

    const audio = new Audio(url);
    state.currentAudio = audio;

    audio.onended = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
      state.currentAudio = null;
    };

    audio.onerror = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
      state.currentAudio = null;
    };

    audio.play().catch(e => {
      console.warn('Playback error:', e);
      if (buttonEl) buttonEl.classList.remove('playing');
    });
  }

  function playWebSpeech(text, buttonEl) {
    if (!('speechSynthesis' in window)) {
      if (buttonEl) buttonEl.classList.remove('playing');
      showToast('Thiết bị không hỗ trợ giọng đọc');
      return;
    }

    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'de-DE';
    u.rate = 0.92;

    u.onend = u.onerror = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
      currentTtsButton = null;
    };

    try {
      window.speechSynthesis.speak(u);
    } catch (e) {
      if (buttonEl) buttonEl.classList.remove('playing');
      currentTtsButton = null;
    }
  }"""

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        t = f.read()

    idx1 = t.find('  // ==========================================================================\n  // Smart 3-Tier')
    if idx1 == -1:
        idx1 = t.find('  // Smart 3-Tier')
    if idx1 == -1:
        idx1 = t.find('let SERVER_BASE_URL')
    
    idx2 = t.find('  // ==========================================================================\n  // Helpers & PWA Service Worker')
    if idx2 == -1:
        idx2 = t.find('  function showToast')

    if idx1 != -1 and idx2 != -1:
        t = t[:idx1] + new_code + '\n\n  ' + t[idx2:]
        # Bump version to 1.0.4
        t = t.replace("const CURRENT_APP_VERSION = '1.0.3';", "const CURRENT_APP_VERSION = '1.0.4';")
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(t)
        print('Updated successfully:', path)
    else:
        print('Could not find markers in:', path, 'idx1:', idx1, 'idx2:', idx2)

update_file('mobile/app.js')
update_file('android-apk-project/app/src/main/assets/app.js')

