import re

js_code = """
  // ==========================================================================
  // Hybrid TTS (Thorsten Kokoro via LAN Server & Android Native Fallback)
  // ==========================================================================
  let SERVER_BASE_URL = localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080';

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
        state.isTtsOnline = true;
        if (el.serverStatusPill) {
          el.serverStatusPill.className = 'server-status-pill';
          el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Thorsten TTS';
        }
        return;
      }
    } catch {
      // Server not reachable
    }

    state.isTtsOnline = false;
    if (el.serverStatusPill) {
      el.serverStatusPill.className = 'server-status-pill offline';
      el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Giọng máy';
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

    // 2. If Thorsten server is reachable, generate high-quality neural voice
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
      // Failover to local speech
    }

    // 3. Fallback seamlessly to Android Native TTS (offline)
    playWebSpeech(cleanText, buttonEl);
  }
"""

def update_file(p):
    with open(p, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find the start of checkTtsServer and end of playAudioUrl definition
    start = text.find('async function checkTtsServer()')
    end = text.find('function playAudioUrl(url, buttonEl)')
    if start != -1 and end != -1:
        text = text[:start] + js_code.strip() + '\n\n  ' + text[end:]
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print('Updated hybrid TTS in', p)
    else:
        print('Could not find anchor in', p)

update_file('mobile/app.js')
update_file('android-apk-project/app/src/main/assets/app.js')
