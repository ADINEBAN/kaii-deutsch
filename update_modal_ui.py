import re

modal_html = """    <!-- Update Notification Modal (Liquid Glass) -->
    <div id="update-modal-backdrop" class="update-backdrop hidden">
      <div class="update-card">
        <div class="update-badge"><iconify-icon icon="lucide:sparkles" width="18" height="18"></iconify-icon> CẬP NHẬT MỚI</div>
        <h3 id="update-version-title" class="update-title">KAII Deutsch</h3>
        <p id="update-notes" class="update-notes">Đã có phiên bản mới với nhiều cải tiến từ vựng và bài tập.</p>
        
        <!-- Interactive Download Progress Bar -->
        <div id="update-progress-box" class="update-progress-box" style="display:none;">
          <div class="update-progress-meta">
            <span id="update-progress-status">Đang tải bản cập nhật...</span>
            <span id="update-progress-percent">0%</span>
          </div>
          <div class="update-progress-track">
            <div id="update-progress-fill" class="update-progress-fill" style="width:0%;"></div>
          </div>
        </div>

        <div class="update-actions" id="update-actions-bar">
          <button id="btn-update-dismiss" class="btn-update-cancel">Để sau</button>
          <button id="btn-update-now" class="btn-update-confirm"><iconify-icon icon="lucide:arrow-down-circle" width="18" height="18"></iconify-icon> Tải cập nhật</button>
        </div>
      </div>
    </div>"""

def update_index(p):
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = r'<!-- Update Notification Modal \(Liquid Glass\) -->[\s\S]*?</div>\s*</div>'
    if re.search(pattern, html):
        html = re.sub(pattern, modal_html, html)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print('Updated modal HTML in', p)

update_index('mobile/index.html')
update_index('android-apk-project/app/src/main/assets/index.html')

