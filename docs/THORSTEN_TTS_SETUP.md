# 🪶 Thorsten-Voice Kokoro TTS Integration Guide

This guide documents the local setup, verification, configuration, troubleshooting, and production deployment options for the **Thorsten-Voice Kokoro Text-to-Speech (TTS)** integration in WordFeather.

---

## 1. Overview & Architecture

WordFeather uses a dual-engine speech system:
- **German (`de-DE`)**: Rendered using the natural, high-quality **Thorsten-Voice Kokoro TTS** neural model running locally via Docker or a remote HTTPS backend, with graceful fallback to browser speech.
- **English (`en-US`)**: Rendered using high-quality natural TTS through the local proxy `/api/tts` (with automatic offline fallback to `espeak-ng` or browser Web Speech API), ensuring crystal-clear pronunciation across all browsers including Brave, Chromium on Linux, and Firefox.
- **Graceful Fallback**: If backends are offline or in restricted environments, WordFeather automatically and seamlessly falls back to local synthesis engines, ensuring audio is always available.

### Architecture Diagram

```
                                  +------------------------------------+
                                  |   Browser (WordFeather Frontend)   |
                                  | - tts.js (window.WordFeatherTTS)   |
                                  +-----------------+------------------+
                                                    |
                       +----------------------------+----------------------------+
                       |                                                         |
               German (de-DE)                                            English (en-US)
                       |                                                         |
         +-------------v-------------+                             +-------------v-------------+
         | Local Dev Proxy (/api/tts)|                             |  Web Speech API (Native)  |
         |  dev_server.py / .js      |                             +---------------------------+
         +-------------+-------------+
                       |
         +-------------v-------------+
         | Thorsten-Voice Kokoro     |
         | Docker (127.0.0.1:8000)   |
         |  POST /tts  |  GET /health|
         +---------------------------+
```

---

## 2. One-Click Quick Start (Recommended for Windows)

### To Start Learning:
Double-click:
```
RUN_LOCAL.bat
```
This automated launcher:
1. Verifies that Docker is installed and starts Docker Desktop if it was stopped.
2. Checks for the `thorsten-kokoro-tts` container and starts it if it was stopped (does not recreate it).
3. Polls the TTS health endpoint (`http://127.0.0.1:8000/health`) until the model is ready.
4. Starts the WordFeather local development server and safe TTS proxy on port `8080` (avoids duplicate processes if already running).
5. Automatically opens `http://localhost:8080/` in your default browser.

### To Stop the Local Server:
Double-click:
```
STOP_LOCAL.bat
```
This stops **only** the WordFeather development server:
- Docker Desktop and your `thorsten-kokoro-tts` container remain untouched and running.
- No unrelated Python, Node.js, or Docker processes are terminated.

---

## 3. First-Time Setup & Manual Startup

### Prerequisites
- Windows 10/11 with [Docker Desktop](https://www.docker.com/products/docker-desktop) installed.
- Python 3.8+ (recommended) or Node.js 18+.

### Step 1: Create the Thorsten-Voice Docker Container (One-Time Setup)
If the container does not exist yet, create and run it with persistent model caching and automatic restart:
```bash
docker run -d --name thorsten-kokoro-tts -p 8000:8000 -v kokoro_cache:/data/hf-cache --restart unless-stopped thorstenvoice/kokoro-tts:latest
```

Verify the container is healthy:
```bash
curl -i http://127.0.0.1:8000/health
```
Expected output:
```json
{"status":"ok","repo_id":"Thorsten-Voice/Kokoro","epoch":"5","device":"cpu"}
```

### Step 2: Start the WordFeather Development Server & TTS Proxy
Because browsers block direct cross-origin requests to `http://127.0.0.1:8000/tts` when CORS preflight is not handled by the Docker container, WordFeather includes a lightweight, safe development server with built-in proxy endpoints:
- `GET  /api/tts/health` -> forwards to `http://127.0.0.1:8000/health`
- `POST /api/tts`        -> forwards to `http://127.0.0.1:8000/tts`
- `OPTIONS /api/tts`     -> handles CORS preflight with safe development headers

#### Option A: Using Python (Canonical, Zero dependencies)
```bash
python dev_server.py
```
*Optional flags:*
- `--port 8080`: Set local server port (default: `8080`).
- `--bind 127.0.0.1`: Set bind address (default: `127.0.0.1`).
- `--tts http://127.0.0.1:8000`: Set target Thorsten-Voice backend URL.

#### Option B: Using Node.js (Alternative, Zero dependencies)
```bash
node dev_server.js
```

### Step 3: Open WordFeather
Open your browser to the canonical website URL:
```
http://localhost:8080/
```
Or navigate directly to specific learning features:
- Wortschatz table: `http://localhost:8080/A1/01_Wortschatz.html`
- Dictionary: `http://localhost:8080/dictionary.html`
- Listening Quiz: `http://localhost:8080/quiz.html`

---

## 3. Testing & Verification

### 1. Terminal / API Testing
Test the local dev proxy health:
```bash
curl -i http://localhost:8080/api/tts/health
```

Test generating a sample audio file:
```bash
curl -i -X POST http://localhost:8080/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Guten Morgen! Ich lerne Deutsch.","speed":0.9}' \
  --output test_audio.wav
```
Verify that `test_audio.wav` is non-empty (~110-120 KB) and playable.

### 2. Browser UI Verification
1. **German Pronunciation Button**:
   - Click any German speaker button (e.g. next to *der Vater* or in the dictionary).
   - **Loading State**: The button immediately displays an animated loading spinner (`.loading` class).
   - **Playing State**: Once audio is ready, the button displays active blue/indigo accent styling (`.playing` class) and audio plays through the speaker.
   - **Completion**: Once playback ends, the button resets to its normal idle state.
2. **Repeated Click (Stop Playback)**:
   - Click a button while audio is playing (or while it is still loading).
   - Playback stops immediately and the button returns to idle state.
3. **Switching Between Audio Clips**:
   - Click button A, then immediately click button B.
   - Button A's audio stops and its pending request is aborted. Button B begins playback cleanly.
4. **English Pronunciation Button**:
   - Click an English pronunciation button (e.g. next to *father*).
   - It plays using the browser-native `en-US` speech synthesis voice without making HTTP requests.
5. **Testing Offline Fallback**:
   - Stop your Docker container: `docker stop thorsten-tts`
   - Click a German pronunciation button in the browser.
   - Notice the button falls back to browser-native `de-DE` speech synthesis seamlessly without UI errors or freezing.
   - Restart your container: `docker start thorsten-tts`

### 3. JavaScript Console Checks
In the browser DevTools Console (F12):
```javascript
// Check TTS integration status
WordFeatherTTS.getEndpoint();
// -> "/api/tts"

// Check backend health
await WordFeatherTTS.checkHealth();
// -> { ok: true, data: { status: "ok", repo_id: "Thorsten-Voice/Kokoro", ... } }

// Programmatically speak a sentence
WordFeatherTTS.speak('Herzlich willkommen bei WordFeather!', 'de-DE');

// Stop speech
WordFeatherTTS.stop();
```

---

## 4. Configuration Options

### Runtime Endpoint Configuration
`WordFeatherTTS` evaluates endpoints in the following priority:
1. `window.WF_TTS_ENDPOINT`: Global runtime JavaScript variable.
2. `localStorage.getItem('wf_tts_endpoint')`: Saved browser preference.
3. Auto-detected local environment:
   - If on `localhost` or `127.0.0.1`: Defaults to `/api/tts` (via `dev_server.py`).
   - If opened via `file://`: Defaults to `http://127.0.0.1:8000/tts`.
4. Public website visitor on GitHub Pages or custom domain:
   - Defaults to native browser speech synthesis directly unless an explicit HTTPS endpoint is configured.

To point your browser to a custom remote TTS server without changing code:
```javascript
// In DevTools console:
WordFeatherTTS.setEndpoint('https://tts.your-custom-domain.com/tts');

// Or directly in localStorage:
localStorage.setItem('wf_tts_endpoint', 'https://tts.your-custom-domain.com/tts');
```

To reset back to default:
```javascript
WordFeatherTTS.setEndpoint(null);
```

### Speed Configuration
To customize speech rate (default `0.9` for language learners):
```javascript
WordFeatherTTS.setSpeed(0.85); // slightly slower
// Or in localStorage:
localStorage.setItem('wf_tts_speed', '0.85');
```

---

## 5. Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| `503 Service Unavailable` on `/api/tts` | Docker container not running or not listening on port 8000 | Run `docker ps` to verify container is running. Start with `docker start <container_id>`. |
| CORS error in console | Opening HTML files via static server without proxy (e.g. `python -m http.server`) | Use `python dev_server.py` or `node dev_server.js`, which proxy `/api/tts` on the same origin. |
| Button stays in loading state | Backend network timeout | Timeout is set to 10 seconds. Check CPU utilization on the Docker host; Kokoro CPU inference on long sentences may take 1-2 seconds. |
| No sound heard | Browser autoplay policy blocked audio, or system volume muted | Click anywhere on the webpage first to satisfy the browser's user-gesture autoplay policy. |
| Falls back to robotic voice | Docker container stopped or endpoint unreachable | Check `await WordFeatherTTS.checkHealth()` in DevTools console to see the exact connection error. |

---

## 6. Independent Website Deployment Guide

> **Important**: GitHub Pages is a purely static host and **cannot execute Docker containers or server-side Python processes**. Never attempt to deploy backend services directly to GitHub Pages, and never modify or deploy to the original author's repository or domain.

When deploying your independent fork of WordFeather to production, choose one of the following approaches:

### Option A: Separately Hosted HTTPS Backend (Recommended for Live Dynamic TTS)

Host the Thorsten-Voice Kokoro Docker container on a container-friendly cloud provider or VPS with an HTTPS reverse proxy:

1. **Hosting Providers**:
   - **Hetzner Cloud / DigitalOcean VPS**: Deploy Docker container on a small 2-core CPU droplet or VPS (€4–€10/month).
   - **Fly.io**: Deploy container with auto-stop/auto-start on traffic (`fly launch --image ...`).
   - **AWS ECS / GCP Cloud Run / Render**: Deploy as a managed container service.

2. **CORS & SSL Configuration (Caddy or Nginx)**:
   The browser requires HTTPS when calling an external API from an HTTPS website (Mixed Content protection). Use Caddy for automatic free Let's Encrypt certificates:

   **Sample `Caddyfile`**:
   ```caddy
   tts.yourdomain.com {
       # Handle CORS headers
       @cors_preflight method OPTIONS
       handle @cors_preflight {
           header Access-Control-Allow-Origin "https://your-wordfeather-site.com"
           header Access-Control-Allow-Methods "GET, POST, OPTIONS"
           header Access-Control-Allow-Headers "Content-Type, Accept"
           header Access-Control-Max-Age "86400"
           respond "" 204
       }

       header Access-Control-Allow-Origin "https://your-wordfeather-site.com"
       reverse_proxy 127.0.0.1:8000
   }
   ```

3. **Frontend Connection**:
   In your deployed site's HTML header or settings:
   ```html
   <script>
     window.WF_TTS_ENDPOINT = "https://tts.yourdomain.com/tts";
   </script>
   ```

---

### Option B: Pre-Generated Static Audio Files (100% Serverless & Zero Ongoing Cost)

Since the WordFeather dataset consists of a fixed, high-value vocabulary list (5,243 words and their example sentences), you can pre-generate all audio clips offline using your local Thorsten-Voice Docker container and serve them as static files!

1. **How it works**:
   - A batch script iterates through `words_final.json`, generates `.wav` or compressed `.mp3`/`.opus` audio for each word and example sentence, and saves them to an `audio/` directory.
   - The files are uploaded to **Cloudflare R2**, **AWS S3**, or **GitHub Pages** (split across releases or a CDN).
   - `tts.js` checks for `/audio/{word_slug}.mp3` first; if present, it plays statically with zero server compute required!
2. **Advantages**:
   - **Zero server costs**: Free static hosting via Cloudflare or GitHub Pages.
   - **Instant playback**: Zero synthesis latency for learners.
   - **100% offline support**: The service worker (`sw.js`) can cache audio clips for offline learning.

---

### Option C: Default Browser-Native Speech (Zero Configuration)

If no custom backend or pre-generated audio files are configured:
- `WordFeatherTTS` automatically falls back to browser-native `de-DE` Web Speech API on production hosts.
- The website remains 100% functional, responsive, and accessible on any static host (GitHub Pages, Vercel, Netlify) with no server setup required.
