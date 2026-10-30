#!/usr/bin/env python3
"""
translate_vietnamese.py — Deterministic, resumable Vietnamese translation pipeline
for WordFeather educational content.

Translates:
1. words_final.json (en -> vi, example_en -> example_vi)
2. grammar_*.json (prompt_en -> prompt_vi, explanation_en -> explanation_vi)
3. grammar_sections.json (en -> vi)

Strict rules:
- Original German content is NEVER modified.
- Additive fields only: vi, example_vi, prompt_vi, explanation_vi.
- Resumable: Skips already translated items.
- Atomic file saves after every batch to prevent corruption.
"""

import os
import sys
import json
import time
import shutil
import argparse
from typing import List, Dict, Any

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS_JSON = os.path.join(REPO, 'words_final.json')

try:
    import translators as ts
except ImportError:
    print("Error: 'translators' package not installed. Run: pip install translators", flush=True)
    sys.exit(1)

ENGINES = ['bing', 'alibaba', 'caiyun']

def log(msg: str):
    print(msg, flush=True)

def translate_single(text: str) -> str:
    if not text or not text.strip():
        return ""
    text_clean = text.strip()
    for engine in ENGINES:
        try:
            res = ts.translate_text(text_clean, translator=engine, from_language='en', to_language='vi', timeout=10)
            if res and isinstance(res, str):
                return res.strip()
        except Exception:
            time.sleep(0.4)
            continue
    return ""

def translate_batch(texts: List[str], engine: str = 'bing') -> List[str]:
    if not texts:
        return []
    cleaned = [t.replace('\r', '').replace('\n', ' ').strip() for t in texts]
    joined = "\n".join(cleaned)
    for eng in [engine] + [e for e in ENGINES if e != engine]:
        try:
            res = ts.translate_text(joined, translator=eng, from_language='en', to_language='vi', timeout=10)
            lines = [l.strip() for l in res.split('\n')]
            if len(lines) == len(texts):
                return lines
        except Exception:
            time.sleep(0.5)
            continue
    
    # Fallback to single translations if batch fails or splits incorrectly
    results = []
    for t in cleaned:
        results.append(translate_single(t))
    return results

def process_words(batch_size: int = 40, max_items: int = None):
    log("\n==========================================")
    log("1. Processing words_final.json")
    log("==========================================")
    
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    bak = WORDS_JSON + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(WORDS_JSON, bak)
        log(f"  Created backup at {bak}")
        
    total_words = len(words)
    missing_indices = [i for i, w in enumerate(words) if not w.get('vi') or not w.get('example_vi')]
    log(f"  Total records: {total_words}")
    log(f"  Records needing translation: {len(missing_indices)}")
    
    if not missing_indices:
        log("  All vocabulary entries already have Vietnamese translations!")
        return

    to_process = missing_indices if max_items is None else missing_indices[:max_items]
    log(f"  Processing {len(to_process)} records in batches of {batch_size}...")

    start_time = time.time()
    processed_count = 0
    
    for b_start in range(0, len(to_process), batch_size):
        batch_indices = to_process[b_start : b_start + batch_size]
        
        en_glosses = []
        en_examples = []
        gloss_map = []
        ex_map = []
        
        for idx in batch_indices:
            w = words[idx]
            if not w.get('vi') and w.get('en'):
                en_glosses.append(w.get('en'))
                gloss_map.append(idx)
            if not w.get('example_vi') and w.get('example_en'):
                en_examples.append(w.get('example_en'))
                ex_map.append(idx)
                
        # Translate glosses
        if en_glosses:
            vi_glosses = translate_batch(en_glosses)
            for idx, vi_text in zip(gloss_map, vi_glosses):
                if vi_text:
                    words[idx]['vi'] = vi_text
                    
        # Translate examples
        if en_examples:
            vi_examples = translate_batch(en_examples)
            for idx, vi_text in zip(ex_map, vi_examples):
                if vi_text:
                    words[idx]['example_vi'] = vi_text

        processed_count += len(batch_indices)
        elapsed = time.time() - start_time
        rate = processed_count / elapsed if elapsed > 0 else 0
        rem = (len(to_process) - processed_count) / rate if rate > 0 else 0
        log(f"  [words_final.json] {processed_count}/{len(to_process)} ({processed_count/len(to_process)*100:.1f}%) | "
            f"Rate: {rate:.1f} w/s | Est. remaining: {rem:.0f}s")
        
        # Save atomically
        tmp = WORDS_JSON + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        shutil.move(tmp, WORDS_JSON)
        time.sleep(0.2)

    log(f"  ✅ Completed words_final.json migration in {time.time()-start_time:.1f}s")

def process_grammar(batch_size: int = 30):
    log("\n==========================================")
    log("2. Processing grammar_*.json")
    log("==========================================")
    for lvl in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
        path = os.path.join(REPO, f'grammar_{lvl}.json')
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
            
        bak = path + '.bak'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
            log(f"  Created backup at {bak}")

        needed_idx = [i for i, q in enumerate(items) if not q.get('prompt_vi') or not q.get('explanation_vi')]
        log(f"  grammar_{lvl}.json: {len(needed_idx)} / {len(items)} need translation")
        if not needed_idx:
            continue
            
        for b_start in range(0, len(needed_idx), batch_size):
            chunk_indices = needed_idx[b_start : b_start + batch_size]
            prompts = [items[i].get('prompt_en', '') for i in chunk_indices]
            explanations = [items[i].get('explanation_en', '') for i in chunk_indices]
            
            p_vi = translate_batch(prompts)
            e_vi = translate_batch(explanations)
            
            for i, p_trans, e_trans in zip(chunk_indices, p_vi, e_vi):
                if p_trans:
                    items[i]['prompt_vi'] = p_trans
                if e_trans:
                    items[i]['explanation_vi'] = e_trans
                    
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            shutil.move(tmp, path)
            log(f"    grammar_{lvl}.json progress: {min(b_start + batch_size, len(needed_idx))}/{len(needed_idx)}")
            time.sleep(0.2)
            
        log(f"  ✅ Finished grammar_{lvl}.json")

def process_grammar_sections():
    log("\n==========================================")
    log("3. Processing grammar_sections.json")
    log("==========================================")
    path = os.path.join(REPO, 'grammar_sections.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    bak = path + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        log(f"  Created backup at {bak}")

    updated = False
    for lvl, sec_list in data.items():
        for s in sec_list:
            if s.get('en') and not s.get('vi'):
                vi = translate_single(s['en'])
                if vi:
                    s['vi'] = vi
                    updated = True
                    log(f"  [{lvl}] {s['en']} -> {vi}")
                    
    if updated:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmp, path)
        log("  ✅ Saved grammar_sections.json")
    else:
        log("  No missing translations in grammar_sections.json")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--words-only', action='store_true', help='Only process words_final.json')
    parser.add_argument('--grammar-only', action='store_true', help='Only process grammar_*.json')
    parser.add_argument('--sections-only', action='store_true', help='Only process grammar_sections.json')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of words to process')
    parser.add_argument('--batch-size', type=int, default=40, help='Batch size for translations')
    args = parser.parse_args()
    
    if args.words_only:
        process_words(batch_size=args.batch_size, max_items=args.limit)
    elif args.grammar_only:
        process_grammar(batch_size=args.batch_size)
    elif args.sections_only:
        process_grammar_sections()
    else:
        process_words(batch_size=args.batch_size, max_items=args.limit)
        process_grammar(batch_size=args.batch_size)
        process_grammar_sections()
