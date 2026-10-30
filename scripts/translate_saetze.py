#!/usr/bin/env python3
"""
translate_saetze.py — Batch translates example sentences in 03_Saetze.html
across A1, A2, B1, B2, C1, C2.

Pattern:
<li><strong>German sentence</strong> — English translation</li>
Becomes:
<li><strong>German sentence</strong> — English translation<div class="vi-trans small text-secondary">Tiếng Việt: Vietnamese translation</div></li>
"""

import os
import sys
import re
import time
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import translators as ts
except ImportError:
    print("Error: translators package not installed.")
    sys.exit(1)

def translate_batch(texts, engine='bing'):
    if not texts:
        return []
    cleaned = [t.replace('\r', '').replace('\n', ' ').strip() for t in texts]
    joined = "\n".join(cleaned)
    for eng in [engine, 'alibaba', 'caiyun']:
        try:
            res = ts.translate_text(joined, translator=eng, from_language='en', to_language='vi', timeout=10)
            lines = [l.strip() for l in res.split('\n')]
            if len(lines) == len(texts):
                return lines
        except Exception:
            time.sleep(0.4)
            continue
    # Single fallback
    res = []
    for t in cleaned:
        done = False
        for eng in [engine, 'alibaba', 'caiyun']:
            try:
                r = ts.translate_text(t, translator=eng, from_language='en', to_language='vi', timeout=10)
                if r:
                    res.append(r.strip())
                    done = True
                    break
            except Exception:
                time.sleep(0.3)
        if not done:
            res.append("")
    return res

def process_saetze_file(level, batch_size=40):
    path = os.path.join(REPO, level, '03_Saetze.html')
    if not os.path.exists(path):
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if already translated
    pattern = re.compile(r'<li><strong>(.*?)</strong>\s*([—–])\s*(.*?)(?:<div class="vi-trans.*?>.*?</div>)?</li>', re.S)
    matches = list(pattern.finditer(content))
    
    needed = []
    for m in matches:
        de = m.group(1).strip()
        dash = m.group(2)
        en = m.group(3).strip()
        full_match = m.group(0)
        if '<div class="vi-trans' not in full_match:
            needed.append((m, de, dash, en))
            
    print(f"[{level}/03_Saetze.html] Total: {len(matches)} | Needing translation: {len(needed)}", flush=True)
    if not needed:
        return

    # Ensure CSS style exists in head
    if '.vi-trans' not in content:
        css_inject = '\n        .vi-trans{font-size:.85rem;color:var(--muted-text);margin-top:.15rem;line-height:1.4;display:block;}\n    </style>'
        content = content.replace('</style>', css_inject, 1)

    # Process in batches
    # We will build replacement mappings
    replacements = {}
    
    for b_start in range(0, len(needed), batch_size):
        chunk = needed[b_start : b_start + batch_size]
        en_list = [item[3] for item in chunk]
        vi_list = translate_batch(en_list)
        
        for (m, de, dash, en), vi in zip(chunk, vi_list):
            if vi:
                old_html = m.group(0)
                new_html = f'<li><strong>{de}</strong> {dash} {en}<div class="vi-trans small text-secondary">Tiếng Việt: {vi}</div></li>'
                replacements[old_html] = new_html
                
        print(f"  [{level}] Progress: {min(b_start + batch_size, len(needed))}/{len(needed)}", flush=True)
        time.sleep(0.3)

    # Apply all replacements
    for old_html, new_html in replacements.items():
        content = content.replace(old_html, new_html)

    bak = path + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    shutil.move(tmp, path)
    print(f"  ✅ Saved {level}/03_Saetze.html ({len(replacements)} translations added)", flush=True)

if __name__ == '__main__':
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        process_saetze_file(lvl)
