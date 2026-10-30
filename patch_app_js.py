import sys

def update():
    with open('android-apk-project/app/src/main/assets/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    target = "  async function checkTtsServer() {"
    replacement = """  async function checkTtsServer() {
    if (window.AndroidTTS && typeof window.AndroidTTS.isSupported === 'function') {
      state.isTtsOnline = true;
      if (el.serverStatusPill) {
        el.serverStatusPill.className = 'server-status-pill';
        el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Giọng máy';
      }
      return;
    }"""
    
    if target in js:
        js = js.replace(target, replacement, 1)
        with open('android-apk-project/app/src/main/assets/app.js', 'w', encoding='utf-8') as f:
            f.write(js)
        print("checkTtsServer updated successfully.")
    else:
        print("Target not found.")

if __name__ == '__main__':
    update()

