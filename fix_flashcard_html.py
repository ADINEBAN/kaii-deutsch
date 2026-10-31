import re

def update_html(p):
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace the flashcard-3d-scene content with the clean wrapped structure
    old_scene_pattern = r'<div class="flashcard-3d-scene">[\s\S]*?</div>\s*</div>\s*<div id="card-counter"'
    
    new_scene = """<div class="flashcard-3d-scene">
            <div id="flashcard-swipe-wrap" class="flashcard-swipe-wrap">
              <!-- Visual Swipe Stamp Badges -->
              <div id="stamp-fail" class="swipe-stamp swipe-stamp-fail">Chưa thuộc</div>
              <div id="stamp-pass" class="swipe-stamp swipe-stamp-pass">Đã nhớ từ</div>

              <div id="flashcard-inner" class="flashcard-inner">
                <!-- Front Face (German) -->
                <div class="flashcard-face flashcard-front">
                  <div style="display:flex;width:100%;justify-content:space-between;align-items:center;">
                    <span id="card-art" class="art-badge"></span>
                    <span id="card-level" class="badge-level">A1</span>
                  </div>
                  
                  <div>
                    <div id="card-de" class="flashcard-center-word">Wort</div>
                    <div id="card-ex-de" style="font-size:0.9rem;color:#cbd5e1;font-weight:500;margin-top:8px;"></div>
                  </div>

                  <div style="display:flex;width:100%;justify-content:space-between;align-items:center;">
                    <button id="card-speaker-btn" class="btn-speaker" style="width:34px;height:34px;" aria-label="Nghe">
                      <iconify-icon icon="lucide:volume-2" width="18" height="18"></iconify-icon>
                    </button>
                    <span class="flashcard-hint">Chạm để xem nghĩa tiếng Việt ↺</span>
                  </div>
                </div>

                <!-- Back Face (Vietnamese) -->
                <div class="flashcard-face flashcard-back">
                  <div style="display:flex;width:100%;justify-content:flex-end;">
                    <span style="font-size:0.75rem;color:var(--text-dim);">Tiếng Việt</span>
                  </div>

                  <div>
                    <div id="card-vi" class="flashcard-center-meaning">Ý nghĩa</div>
                    <div id="card-ex-vi" style="font-size:0.86rem;color:var(--text-muted);margin-top:8px;"></div>
                  </div>

                  <span class="flashcard-hint">Chạm để lật lại tiếng Đức ↻</span>
                </div>
              </div>
            </div>
          </div>

          <div id="card-counter" """

    if '<div id="flashcard-swipe-wrap"' not in html:
        html = re.sub(old_scene_pattern, new_scene, html)

    # Make sure gesture guide is present and action buttons are removed
    guide_html = """          <!-- Flashcard Swipe Gesture Guide -->
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

    html = re.sub(r'<div class="flashcard-action-bar">[\s\S]*?</div>', guide_html, html)

    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('Updated HTML structure in', p)

update_html('mobile/index.html')
update_html('android-apk-project/app/src/main/assets/index.html')

