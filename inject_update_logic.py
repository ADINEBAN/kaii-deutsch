import os

update_checker_js = """
  // ==========================================================================
  // Auto-Update Checker via GitHub Releases (ADINEBAN/kaii-deutsch)
  // ==========================================================================
  const CURRENT_APP_VERSION = '1.0.0';
  const GITHUB_REPO = 'ADINEBAN/kaii-deutsch';

  async function checkForAppUpdates() {
    try {
      // Check GitHub Releases API for the latest version tag
      const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`, {
        headers: { 'Accept': 'application/vnd.github.v3+json' }
      });

      if (!res.ok) return; // No release published yet or offline

      const release = await res.json();
      const latestTag = (release.tag_name || '').replace(/^v/i, '').trim();

      if (isNewerVersion(latestTag, CURRENT_APP_VERSION)) {
        showUpdateModal(release, latestTag);
      }
    } catch (err) {
      console.log('Update check skipped (offline or not reachable):', err);
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

    if (!backdrop || !titleEl || !btnConfirm) return;

    titleEl.textContent = `KAII Deutsch v${versionStr}`;
    if (release.body && release.body.trim()) {
      notesEl.textContent = release.body.trim();
    } else {
      notesEl.textContent = 'Đã có bản cập nhật mới nhất với nhiều tối ưu mượt mà và sửa lỗi.';
    }

    // Find direct APK asset if available, otherwise open the release page
    let apkUrl = release.html_url;
    if (release.assets && release.assets.length > 0) {
      const apkAsset = release.assets.find(a => a.name && a.name.endsWith('.apk'));
      if (apkAsset && apkAsset.browser_download_url) {
        apkUrl = apkAsset.browser_download_url;
      }
    }

    btnConfirm.href = apkUrl;
    btnConfirm.onclick = function(e) {
      backdrop.classList.add('hidden');
    };

    if (btnDismiss) {
      btnDismiss.onclick = function() {
        backdrop.classList.add('hidden');
      };
    }

    backdrop.classList.remove('hidden');
  }
"""

def inject_update_checker(path):
    with open(path, 'r', encoding='utf-8') as f:
        js = f.read()
    
    if 'checkForAppUpdates' not in js:
        # inject before init function
        init_call = 'await loadInitialData();'
        replacement = 'await loadInitialData();\n    checkForAppUpdates();'
        js = js.replace(init_call, replacement, 1)

        # append update functions before closing
        closing = '  if (document.readyState === \'loading\') {'
        js = js.replace(closing, update_checker_js + '\n' + closing, 1)

        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        print('Injected update checker into', path)
    else:
        print('Update checker already present in', path)

inject_update_checker('mobile/app.js')
inject_update_checker('android-apk-project/app/src/main/assets/app.js')

