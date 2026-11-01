import os

smart_tts_code = """
  // ==========================================================================
  // Smart 3-Tier Speech Engine (Local LAN Thorsten -> Cloud TTS -> Native Offline)
  // ==========================================================================
  let SERVER_BASE_URL = (localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080').replace(/\\/m\\/?$/, '').replace(/\\/+$/, '');
  let isLocalServerLive = false;

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

    if (buttonEl) buttonEl.classList.add('playing');

    // 1. Check in-memory audio blob cache
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
        console.warn('Local TTS failed, switching to Cloud:', err);
      }
    }

    // 3. Priority 2: Cloud Neural German Voice 24/7 (No laptop, no server needed)
    try {
      const encodedText = encodeURIComponent(cleanText);
      const cloudUrl = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodedText}&tl=de-DE&client=tw-ob`;
      
      const audio = new Audio();
      let hasHandledEnd = false;

      const cleanup = () => {
        if (!hasHandledEnd) {
          hasHandledEnd = true;
          if (buttonEl) buttonEl.classList.remove('playing');
          state.currentAudio = null;
        }
      };

      audio.onended = cleanup;
      audio.onerror = () => {
        cleanup();
        // Fallback to Native TTS if offline
        playWebSpeech(cleanText, buttonEl);
      };

      if (state.currentAudio) {
        state.currentAudio.pause();
        state.currentAudio = null;
      }

      state.currentAudio = audio;
      audio.src = cloudUrl;
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          cleanup();
          playWebSpeech(cleanText, buttonEl);
        });
      }
      return;
    } catch (e) {
      console.warn('Cloud audio failed, falling back to native:', e);
    }

    // 4. Priority 3: Fallback seamlessly to Android Native TTS (100% offline)
    playWebSpeech(cleanText, buttonEl);
  }
"""

def update_smart_tts(p):
    with open(p, 'r', encoding='utf-8') as f:
        t = f.read()

    start = t.find('// ==========================================================================\n  // Hybrid TTS')
    if start == -1:
        start = t.find('let SERVER_BASE_URL')
    
    end = t.find('function playAudioUrl(url, buttonEl)')
    if start != -1 and end != -1:
        t = t[:start] + smart_tts_code.strip() + '\n\n  ' + t[end:]
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(t)
        print('Updated 3-tier Smart TTS in', p)
    else:
        print('Could not find anchors in', p)

update_smart_tts('mobile/app.js')
update_smart_tts('android-apk-project/app/src/main/assets/app.js')

