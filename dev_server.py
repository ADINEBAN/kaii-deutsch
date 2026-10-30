#!/usr/bin/env python3
"""
WordFeather Local Development Server & Safe TTS Proxy
=====================================================
Serves the WordFeather static study platform and provides safe,
same-origin proxy endpoints to the local Thorsten-Voice Kokoro TTS Docker container.

Endpoints:
  GET  /api/tts/health  -> Proxies http://127.0.0.1:8000/health
  POST /api/tts         -> Proxies http://127.0.0.1:8000/tts (WAV audio generation)
  OPTIONS /api/tts      -> CORS preflight handler for local dev
  *                     -> Static file server (HTML, CSS, JS, JSON, images)

Usage:
  python dev_server.py
  python dev_server.py --port 8080 --tts http://127.0.0.1:8000
"""

import os
import sys
import json
import socket
import argparse
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(REPO_ROOT, "dev_server.pid")
LOG_FILE = os.path.join(REPO_ROOT, "dev_server.log")
DEFAULT_PORT = 8080
DEFAULT_BIND = "0.0.0.0"
DEFAULT_TTS_BACKEND = "http://127.0.0.1:8000"

if sys.platform == "win32":
    if sys.stdout is None:
        try:
            sys.stdout = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        except Exception:
            sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        try:
            sys.stderr = sys.stdout
        except Exception:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class WordFeatherDevHandler(SimpleHTTPRequestHandler):
    """Static file handler with safe reverse proxy for Thorsten-Voice TTS."""

    tts_backend = DEFAULT_TTS_BACKEND

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=REPO_ROOT, **kwargs)

    def log_diag(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [TTS Proxy] {msg}", flush=True)

    def end_headers(self):
        # Allow cross-origin requests from local test harnesses if needed
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")

        # Disable caching for static dev assets so code updates appear instantly
        clean_path = self.path.split("?")[0]
        if not (clean_path.startswith("/api/tts") and clean_path != "/api/tts/health"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests cleanly."""
        clean_path = self.path.split("?")[0]
        if clean_path in ("/api/tts", "/api/tts/health"):
            self.send_response(204)
            self.send_header("Access-Control-Max-Age", "86400")
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def serve_server_info(self):
        """Return server connection info and status for mobile devices."""
        lan_ip = get_lan_ip()
        healthy, info = check_backend_health(self.tts_backend)
        data = {
            "server": "WordFeather Local Server",
            "lan_ip": lan_ip,
            "port": DEFAULT_PORT,
            "tts_healthy": healthy,
            "tts_info": info if healthy else str(info),
            "mobile_url": f"http://{lan_ip}:{DEFAULT_PORT}/m"
        }
        encoded = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        """Serve static files or proxy health check."""
        # Normalize path (strip query params)
        clean_path = self.path.split("?")[0]

        if clean_path in ("/m", "/m/", "/mobile", "/mobile/"):
            self.path = "/mobile/index.html"
            return super().do_GET()

        if clean_path == "/api/server-info":
            self.serve_server_info()
            return

        if clean_path == "/api/tts/health":
            self.proxy_health_check()
            return

        super().do_GET()

    def do_POST(self):
        """Proxy audio generation to Thorsten-Voice backend."""
        clean_path = self.path.split("?")[0]

        if clean_path == "/api/tts":
            self.proxy_tts_generation()
            return

        self.send_error(404, "Endpoint not found")

    def proxy_health_check(self):
        target_url = f"{self.tts_backend.rstrip('/')}/health"
        self.log_diag(f"GET /api/tts/health -> Forwarding to {target_url}")
        try:
            req = urllib.request.Request(
                target_url,
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read()
                status_code = response.getcode()
                content_type = response.headers.get("Content-Type", "application/json")

                self.log_diag(f"Health response from {target_url}: status={status_code}, content-type={content_type}")
                self.send_response(status_code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.log_diag(f"Health check HTTPError from {target_url}: status={e.code}")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self.log_diag(f"Health check failed to connect to {target_url}: {e}")
            err_json = json.dumps({
                "status": "error",
                "message": f"Cannot connect to Thorsten-Voice TTS at {target_url}: {e}"
            }).encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_json)))
            self.end_headers()
            self.wfile.write(err_json)

    def synthesize_english(self, text, speed=0.9):
        """Synthesize English audio: Google Translate TTS (online) with offline fallback to espeak/espeak-ng/Windows SAPI."""
        # 1. Try Google Translate TTS (online high-quality natural audio)
        try:
            encoded_text = urllib.parse.quote(text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={encoded_text}"
            req = urllib.request.Request(
                tts_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "audio/mpeg")
                if content and len(content) > 100:
                    return content, content_type
        except Exception as e:
            self.log_diag(f"Google TTS online request failed ({e}). Attempting offline fallback...")

        # 2. Offline fallback: espeak-ng / espeak on Linux
        espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
        if espeak_bin:
            tmp_wav = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    tmp_wav = tf.name
                subprocess.run(
                    [espeak_bin, "-v", "en-us", "-w", tmp_wav, text],
                    check=True,
                    timeout=5,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                with open(tmp_wav, "rb") as f:
                    content = f.read()
                return content, "audio/wav"
            except Exception as ex:
                self.log_diag(f"espeak fallback failed: {ex}")
            finally:
                if tmp_wav and os.path.exists(tmp_wav):
                    try:
                        os.remove(tmp_wav)
                    except Exception:
                        pass

        # 3. Offline fallback: Windows PowerShell SAPI
        if sys.platform == "win32":
            tmp_wav = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    tmp_wav = tf.name
                safe_text = text.replace("'", "''").replace('"', '`"')
                ps_script = (
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$synth.SetOutputToWaveFile('{tmp_wav}'); "
                    f"$synth.Speak('{safe_text}'); "
                    f"$synth.Dispose()"
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    check=True,
                    timeout=8,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                with open(tmp_wav, "rb") as f:
                    content = f.read()
                return content, "audio/wav"
            except Exception as ex:
                self.log_diag(f"Windows SAPI fallback failed: {ex}")
            finally:
                if tmp_wav and os.path.exists(tmp_wav):
                    try:
                        os.remove(tmp_wav)
                    except Exception:
                        pass

        raise RuntimeError("No available English TTS engine (online Google TTS failed and no offline synthesizer found)")

    def proxy_tts_generation(self):
        target_url = f"{self.tts_backend.rstrip('/')}/tts"

        # Validate Content-Length to avoid denial of service
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self.log_diag("POST /api/tts - Invalid Content-Length header")
            self.send_error(400, "Invalid Content-Length header")
            return

        if content_length <= 0 or content_length > 65536:
            self.log_diag(f"POST /api/tts - Payload length out of range: {content_length} bytes")
            self.send_error(400, "Payload must be between 1 and 65,536 bytes")
            return

        # Read and validate JSON body
        raw_body = self.rfile.read(content_length)
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self.log_diag(f"POST /api/tts - Invalid JSON body: {e}")
            self.send_error(400, "Payload must be valid JSON")
            return

        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            self.log_diag("POST /api/tts - Missing or empty 'text' field")
            self.send_error(400, "Missing or empty 'text' field in JSON request")
            return

        speed = data.get("speed", 0.9)
        try:
            speed = float(speed)
            if speed < 0.2 or speed > 3.0:
                speed = 0.9
        except (ValueError, TypeError):
            speed = 0.9

        lang = str(data.get("lang", "de-DE")).strip()
        is_english = lang.lower().startswith("en")

        preview = text.strip()[:40] + ('...' if len(text.strip()) > 40 else '')

        # 1. Handle English synthesis via Google TTS or local offline engines
        if is_english:
            self.log_diag(f"POST /api/tts [English] -> Synthesizing: '{preview}' (speed={speed})")
            try:
                content, content_type = self.synthesize_english(text.strip(), speed)
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(content)
                self.log_diag(f"POST /api/tts [English] -> Generated {len(content)} bytes ({content_type})")
                return
            except Exception as e:
                self.log_diag(f"POST /api/tts [English] error: {e}")
                err_json = json.dumps({
                    "status": "error",
                    "message": f"English TTS error: {e}"
                }).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_json)))
                self.end_headers()
                self.wfile.write(err_json)
                return

        # 2. Handle German synthesis via Thorsten-Voice Docker container
        sanitized_payload = json.dumps({"text": text.strip(), "speed": speed}).encode("utf-8")
        self.log_diag(f"POST /api/tts [German] -> Forwarding to {target_url} (text='{preview}', speed={speed})")

        # Forward request to local Thorsten-Voice Docker container
        try:
            req = urllib.request.Request(
                target_url,
                data=sanitized_payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "audio/wav, audio/*;q=0.9, */*;q=0.8"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
                status_code = response.getcode()
                content_type = response.headers.get("Content-Type", "audio/wav")

                self.log_diag(f"TTS response from {target_url}: status={status_code}, content-type={content_type}, bytes={len(content)}")
                self.send_response(status_code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.log_diag(f"TTS HTTPError from {target_url}: status={e.code}, body={err_body[:200]}")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self.log_diag(f"TTS backend connection error at {target_url}: {e}")
            err_json = json.dumps({
                "status": "error",
                "message": f"Thorsten-Voice backend error at {target_url}: {e}"
            }).encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_json)))
            self.end_headers()
            self.wfile.write(err_json)


def check_backend_health(url):
    health_url = f"{url.rstrip('/')}/health"
    try:
        req = urllib.request.Request(health_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data
    except Exception as e:
        return False, str(e)


def get_lan_ip():
    """Detect local LAN IP address of laptop."""
    # Method 1: dummy UDP connect
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    # Method 2: ip route get 1.1.1.1
    try:
        out = subprocess.check_output(["ip", "route", "get", "1.1.1.1"], stderr=subprocess.DEVNULL).decode("utf-8")
        import re
        m = re.search(r"src\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass

    # Method 3: ip -4 addr
    try:
        out = subprocess.check_output(["ip", "-4", "addr"], stderr=subprocess.DEVNULL).decode("utf-8")
        import re
        ips = re.findall(r"inet\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", out)
        for candidate in ips:
            if not candidate.startswith("127.") and not candidate.startswith("172.17."):
                return candidate
    except Exception:
        pass

    return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="WordFeather Local Dev Server with Thorsten-Voice TTS Proxy")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to listen on (default: {DEFAULT_PORT})")
    parser.add_argument("--bind", default=DEFAULT_BIND, help=f"Address to bind to (default: {DEFAULT_BIND})")
    parser.add_argument("--tts", default=DEFAULT_TTS_BACKEND, help=f"Thorsten-Voice backend URL (default: {DEFAULT_TTS_BACKEND})")
    args = parser.parse_args()

    WordFeatherDevHandler.tts_backend = args.tts
    lan_ip = get_lan_ip()
    mobile_url = f"http://{lan_ip}:{args.port}/m"

    print("=" * 68)
    print("  🪶 WordFeather Local Development Server & TTS Proxy")
    print("=" * 68)
    print(f"  Web root:     {REPO_ROOT}")
    print(f"  Laptop URL:   http://127.0.0.1:{args.port}/")
    print(f"  Network LAN:  http://{lan_ip}:{args.port}/")
    print(f"  TTS Backend:  {args.tts}")

    healthy, info = check_backend_health(args.tts)
    if healthy:
        model = info.get("repo_id", "Kokoro")
        print(f"  TTS Health:   ✅ Connected to Thorsten-Voice ({model})")
    else:
        print(f"  TTS Health:   ⚠️  Backend not reachable ({info})")
        print("                Start container: docker run -d -p 8000:8000 ...")
        print("                (WordFeather will automatically fall back to native speech)")
    
    print("-" * 68)
    print("  📱 DÀNH CHO ĐIỆN THOẠI REALME GT NEO 2T:")
    print(f"     1. Đảm bảo điện thoại và laptop đang kết nối chung 1 mạng Wi-Fi.")
    print(f"     2. Mở trình duyệt Chrome trên điện thoại Realme và nhập:")
    print(f"        👉  {mobile_url}")
    print(f"     3. Nhấn vào menu (⋮) -> chọn 'Cài đặt ứng dụng' hoặc")
    print(f"        'Thêm vào màn hình chính' để dùng như App Android độc lập!")
    print("=" * 68)
    print(f"  Press Ctrl+C to stop server.\n")

    server_address = (args.bind, args.port)
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, WordFeatherDevHandler)
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping WordFeather dev server...")
    finally:
        httpd.server_close()
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except Exception:
            pass


if __name__ == "__main__":
    main()
