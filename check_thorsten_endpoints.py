import urllib.request, urllib.parse, ssl
ctx = ssl._create_unverified_context()

def check(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
            print("Status:", r.status, "type:", r.headers.get('Content-Type'), "len:", len(r.read()))
    except Exception as e:
        print("Fail:", e)

# Let's test German TTS endpoints
text = urllib.parse.quote('Guten Morgen, wie geht es dir?')
print("Testing Google Translate TTS Audio:")
check(f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=de&client=tw-ob")
