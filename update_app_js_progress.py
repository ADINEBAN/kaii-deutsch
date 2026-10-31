import re

update_logic_script = """
  // ==========================================================================
  // Auto-Update Checker with Native Download Progress & Auto-Install
  // ==========================================================================
  const CURRENT_APP_VERSION = '1.0.0';
  const GITHUB_REPO = 'ADINEBAN/kaii-deutsch';

  window.onAppDownloadProgress = function(percent, downloaded, total, status) {
    const progressBox = document.getElementById('update-progress-box');
    const fillEl = document.getElementById('update-progress-fill');
    const percentEl = document.getElementById('update-progress-percent');
    const statusEl = document.getElementById('update-progress-status');

    if (!progressBox || !fillEl || !percentEl || !statusEl) return;

    progressBox.style.display = 'block';
    fillEl.style.width = percent + '%';
    percentEl.textContent = percent + '%';

    if (total > 0) {
      const mbDown = (downloaded / (1024 * 1024)).toFixed(1);
      const mbTotal = (total / (1024 * 1024)).toFixed(1);
      statusEl.textContent = `Đang tải: ${mbDown}MB / ${mbTotal}MB`;
    }

    if (percent >= 100 || status === 8) { // 8 = STATUS_SUCCESSFUL
      statusEl.textContent = 'Tải xong! Đang mở cài đặt...';
      setTimeout(() => {
        const backdrop = document.getElementById('update-modal-backdrop');
        if (backdrop) backdrop.classList.add('hidden');
      }, 1500);
    }
  };

  async function checkForAppUpdates() {
    try {
      const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`, {
        headers: { 'Accept': 'application/vnd.github.v3+json' }
      });

      if (!res.ok) return;

      const release = await res.json();
      const latestTag = (release.tag_name || '').replace(/^v/i, '').trim();

      if (isNewerVersion(latestTag, CURRENT_APP_VERSION)) {
        showUpdateModal(release, latestTag);
      }
    } catch (err) {
      console.log('Update check skipped:', err);
    }
  }

  function isNewerVersion(latest, current) {
    if (!latest) return false;
    const lParts = latest.split('.').map(n => parseInt(n, 10) || 0);
    const cParts = current.split('.').map(n => parseInt(n, 10) || 0);
    for (let i = 0; i < Math.max(lParts.length, cParts.length); i++) {
      const l = lParts[i] || 0;
      const c = cParts[i] || 0;
      if (l > c) return true;
      if (l < c) return false;
    }
    return false;
  }

  function showUpdateModal(release, versionStr) {
    const backdrop = document.getElementById('update-modal-backdrop');
    const titleEl = document.getElementById('update-version-title');
    const notesEl = document.getElementById('update-notes');
    const btnConfirm = document.getElementById('btn-update-now');
    const btnDismiss = document.getElementById('btn-update-dismiss');
    const progressBox = document.getElementById('update-progress-box');
    const actionsBar = document.getElementById('update-actions-bar');

    if (!backdrop || !titleEl || !btnConfirm) return;

    titleEl.textContent = `KAII Deutsch v${versionStr}`;
    if (release.body && release.body.trim()) {
      notesEl.textContent = release.body.trim();
    } else {
      notesEl.textContent = 'Đã có phiên bản mới nhất với nhiều tối ưu mượt mà và sửa lỗi.';
    }

    // Direct APK asset link
    let apkUrl = release.html_url;
    if (release.assets && release.assets.length > 0) {
      const apkAsset = release.assets.find(a => a.name && a.name.endsWith('.apk'));
      if (apkAsset && apkAsset.browser_download_url) {
        apkUrl = apkAsset.browser_download_url;
      }
    }

    btnConfirm.onclick = function(e) {
      e.preventDefault();
      
      // If running inside Android Native App with DownloadManager
      if (window.AndroidUpdater && typeof window.AndroidUpdater.startDownload === 'function') {
        if (actionsBar) actionsBar.style.display = 'none';
        if (progressBox) progressBox.style.display = 'block';
        window.AndroidUpdater.startDownload(apkUrl);
      } else {
        // Browser fallback
        window.open(apkUrl, '_blank');
        backdrop.classList.add('hidden');
      }
    };

    if (btnDismiss) {
      btnDismiss.onclick = function() {
        backdrop.classList.add('hidden');
      };
    }

    backdrop.classList.remove('hidden');
  }
"""

def update_js(p):
    with open(p, 'r', encoding='utf-8') as f:
        js = f.read()

    start = js.find('// ==========================================================================\n  // Auto-Update Checker')
    end = js.find('if (document.readyState === \'loading\') {')
    if start != -1 and end != -1:
        js = js[:start] + update_logic_script.strip() + '\n\n  ' + js[end:]
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        print('Updated update logic in', p)

update_js('mobile/app.js')
update_js('android-apk-project/app/src/main/assets/app.js')

