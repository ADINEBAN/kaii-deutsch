import os

def update_html(p):
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add stamps to flashcard-front
    target_front = '<div style="display:flex;width:100%;justify-content:space-between;align-items:center;">'
    replacement_front = """<div id="stamp-fail" class="swipe-stamp swipe-stamp-fail">Chưa thuộc</div>
                <div id="stamp-pass" class="swipe-stamp swipe-stamp-pass">Đã nhớ từ</div>
                <div style="display:flex;width:100%;justify-content:space-between;align-items:center;">"""

    if 'id="stamp-fail"' not in html:
        html = html.replace(target_front, replacement_front, 1)

    # 2. Replace action buttons with gesture guide
    old_action_bar = """          <!-- Flashcard Action Buttons -->
          <div class="flashcard-action-bar">
            <button id="btn-card-fail" class="btn-card-action btn-card-fail">
              <iconify-icon icon="lucide:x" width="18" height="18"></iconify-icon> Chưa thuộc
            </button>
            <button id="btn-card-pass" class="btn-card-action btn-card-pass">
              <iconify-icon icon="lucide:check" width="18" height="18"></iconify-icon> Đã nhớ từ
            </button>
          </div>"""

    new_guide = """          <!-- Flashcard Swipe Gesture Guide -->
          <div class="flashcard-gesture-guide">
            <span class="gesture-guide-item gesture-guide-fail">
              <iconify-icon icon="lucide:chevron-left" width="16" height="16"></iconify-icon> Vuốt trái: Chưa thuộc
            </span>
            <span class="gesture-guide-item" style="color:var(--text-dim);font-size:0.75rem;">
              Chạm thẻ để lật
            </span>
            <span class="gesture-guide-item gesture-guide-pass">
              Vuốt phải: Đã nhớ <iconify-icon icon="lucide:chevron-right" width="16" height="16"></iconify-icon>
            </span>
          </div>"""

    if old_action_bar in html:
        html = html.replace(old_action_bar, new_guide)
    elif 'class="flashcard-action-bar"' in html:
        # Fallback regex/string replacement
        import re
        html = re.sub(r'<div class="flashcard-action-bar">[\s\S]*?<\/div>', new_guide, html)

    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('Updated HTML in', p)

def append_css(p):
    with open('swipe_flashcard.css', 'r', encoding='utf-8') as f:
        swipe_css = f.read()
    with open(p, 'r', encoding='utf-8') as f:
        css = f.read()
    if '.swipe-stamp' not in css:
        css = css + '\n\n' + swipe_css
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(css)
        print('Appended swipe CSS to', p)

for path in ['mobile/index.html', 'android-apk-project/app/src/main/assets/index.html']:
    update_html(path)

for path in ['mobile/app.css', 'android-apk-project/app/src/main/assets/app.css']:
    append_css(path)
