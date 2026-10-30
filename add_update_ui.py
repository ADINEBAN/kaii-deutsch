import os

modal_html = """
    <!-- Update Notification Modal (Liquid Glass) -->
    <div id="update-modal-backdrop" class="update-backdrop hidden">
      <div class="update-card">
        <div class="update-badge"><iconify-icon icon="lucide:sparkles" width="18" height="18"></iconify-icon> CẬP NHẬT MỚI</div>
        <h3 id="update-version-title" class="update-title">KAII Deutsch</h3>
        <p id="update-notes" class="update-notes">Đã có phiên bản mới với nhiều cải tiến từ vựng và bài tập.</p>
        <div class="update-actions">
          <button id="btn-update-dismiss" class="btn-update-cancel">Để sau</button>
          <a id="btn-update-now" href="#" class="btn-update-confirm"><iconify-icon icon="lucide:arrow-right" width="18" height="18"></iconify-icon> Tải cập nhật</a>
        </div>
      </div>
    </div>
"""

def add_modal(path):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'update-modal-backdrop' not in c:
        target = '<div id="glass-toast" class="glass-toast"></div>'
        c = c.replace(target, target + modal_html)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print('Added update modal to', path)
    else:
        print('Already present in', path)

add_modal('mobile/index.html')
add_modal('android-apk-project/app/src/main/assets/index.html')

