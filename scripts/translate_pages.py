#!/usr/bin/env python3
"""
translate_pages.py — Translates English educational content in static HTML pages
across A1, A2, B1, B2, C1, C2.

Translates:
- 02_Grammatik.html
- 04_Lesen.html
- 05_Hoeren.html
- 06_Sprechen.html
- 07_Schreiben.html
- 08_Musterpruefung.html
- 09_telc_Pruefungsformat.html
- 10_notes.html, 11_cheat_sheet.html (where applicable)

Pattern:
<em>English translation/instruction</em>
Becomes:
<em>English translation/instruction</em><span class="vi-trans d-block text-secondary small">Tiếng Việt: Vietnamese translation</span>
"""

import os
import sys
import re
import time
import shutil
import glob

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

def process_html_file(file_path, batch_size=35):
    rel = os.path.relpath(file_path, REPO)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find <em> tags not followed by vi-trans
    # Exclude tags containing HTML tags like <span> or <br>
    pattern = re.compile(r'<em>([^<>\n]{3,250})</em>(?!\s*<span class="vi-trans)', re.S)
    matches = list(pattern.finditer(content))
    
    needed = []
    for m in matches:
        raw = m.group(1).strip()
        # Filter out German-only or punctuation
        if not raw or raw in ['—', '-', '–'] or re.match(r'^\d+[\.\)]?$', raw):
            continue
        needed.append((m, raw))

    if not needed:
        return 0

    print(f"[{rel}] Found {len(needed)} English tags needing Vietnamese...", flush=True)

    # Ensure CSS exists
    if '.vi-trans' not in content:
        css = '\n        .vi-trans{font-size:.85rem;color:var(--muted-text);margin-top:.15rem;line-height:1.4;display:block;}\n        [data-bs-theme="dark"] .vi-trans{color:#94a3b8;}\n    </style>'
        content = content.replace('</style>', css, 1)

    replacements = {}
    for b_start in range(0, len(needed), batch_size):
        chunk = needed[b_start : b_start + batch_size]
        texts_to_trans = []
        is_paren_list = []
        for m, raw in chunk:
            is_paren = raw.startswith('(') and raw.endswith(')')
            clean_text = raw[1:-1].strip() if is_paren else raw
            texts_to_trans.append(clean_text)
            is_paren_list.append(is_paren)

        vi_list = translate_batch(texts_to_trans)
        for (m, raw), vi, is_paren in zip(chunk, vi_list, is_paren_list):
            if vi:
                vi_formatted = f"({vi})" if is_paren else vi
                old_str = m.group(0)
                new_str = f'<em>{raw}</em><span class="vi-trans d-block text-secondary small">Tiếng Việt: {vi_formatted}</span>'
                replacements[old_str] = new_str

        print(f"  [{rel}] Progress: {min(b_start + batch_size, len(needed))}/{len(needed)}", flush=True)
        time.sleep(0.2)

    for old_str, new_str in replacements.items():
        content = content.replace(old_str, new_str)

    bak = file_path + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(file_path, bak)

    tmp = file_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    shutil.move(tmp, file_path)
    print(f"  ✅ Saved {rel} ({len(replacements)} translations added)", flush=True)
    return len(replacements)

def process_all_pages():
    total_added = 0
    target_files = []
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        for f in sorted(glob.glob(os.path.join(REPO, lvl, '*.html'))):
            bname = os.path.basename(f)
            if bname in ['01_Wortschatz.html', '03_Saetze.html', 'index.html', 'README.html']:
                continue
            target_files.append(f)

    print(f"Processing {len(target_files)} static educational pages...")
    for f in target_files:
        count = process_html_file(f)
        total_added += count

    print(f"\n🎉 Finished translating static educational pages: {total_added} translations added across {len(target_files)} files!")

if __name__ == '__main__':
    process_all_pages()
