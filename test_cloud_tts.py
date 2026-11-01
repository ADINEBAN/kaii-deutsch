import urllib.request
import urllib.parse
import ssl

ctx = ssl._create_unverified_context()

def test_url(name, url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            data = resp.read()
            print(f"[{name}] SUCCESS: Status {resp.status}, Content-Type: {resp.headers.get('Content-Type')}, Size: {len(data)} bytes")
            return True
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        return False

if __name__ == '__main__':
    text = urllib.parse.quote('Hallo! Willkommen bei KAII.')
    
    # Endpoint 1: Google High Quality German Voice (24/7 free, zero config, mp3 audio)
    test_url("Google German TTS", f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=de-DE&client=tw-ob")
    
    # Endpoint 2: Voice RSS German
    test_url("VoiceRSS German", f"https://api.voicerss.org/?key=e74d1a58c03541ce8f15d9a9ef1c911e&hl=de-de&src={text}")

    # Endpoint 3: ResponsiveVoice German
    test_url("ResponsiveVoice", f"https://code.responsivevoice.org/getvoice.php?t={text}&tl=de&sv=g1&vn=&pitch=0.5&rate=0.5&vol=1")

