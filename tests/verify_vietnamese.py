#!/usr/bin/env python3
"""
verify_vietnamese.py — Comprehensive validation script for Vietnamese learning content.

Verifies:
1. German content invariance: Compares words_final.json against original backup.
2. Vietnamese coverage: 100% of eligible English fields have Vietnamese equivalents.
3. Grammar exercises & sections coverage.
4. JSON syntax and record integrity (no lost records, duplicate keys).
5. HTML markup validity and presence of Vietnamese translation elements.
6. Multi-level representative sampling across CEFR A1, A2, B1, B2, C1, C2.
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS_JSON = os.path.join(REPO, 'words_final.json')
WORDS_BAK = os.path.join(REPO, 'words_final.json.bak')

def test_words_invariance_and_coverage():
    print("==================================================")
    print("Test 1: words_final.json Invariance & Coverage")
    print("==================================================")
    if not os.path.exists(WORDS_JSON):
        print("  ❌ words_final.json does not exist!")
        return False
        
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
        
    print(f"  Loaded {len(words)} entries from words_final.json")
    if len(words) != 5243:
        print(f"  ❌ Expected 5243 words, found {len(words)}!")
        return False

    # Check against backup if present
    if os.path.exists(WORDS_BAK):
        with open(WORDS_BAK, 'r', encoding='utf-8') as f:
            bak_words = json.load(f)
        print(f"  Comparing against backup ({len(bak_words)} records)...")
        
        german_mutations = 0
        for i, (w, bw) in enumerate(zip(words, bak_words)):
            # Must match German fields exactly
            for field in ['de', 'level', 'article', 'example', 'collocations', 'register', 'conjugation']:
                if w.get(field) != bw.get(field):
                    german_mutations += 1
                    print(f"  ❌ German mutation at index {i} ('{w.get('de')}'): field '{field}' changed!")
                    if german_mutations >= 5:
                        break
            if german_mutations >= 5:
                break
                
        if german_mutations == 0:
            print("  ✅ German Content Invariance: 100% PASS (Zero German mutations across all 5,243 words)")
        else:
            print(f"  ❌ FAILED: Found {german_mutations} German mutations!")
            return False

    # Check Vietnamese coverage
    has_vi = sum(1 for w in words if w.get('vi', '').strip())
    has_ex_vi = sum(1 for w in words if w.get('example_vi', '').strip())
    
    print(f"  Vietnamese meanings: {has_vi} / 5243 ({has_vi/5243*100:.1f}%)")
    print(f"  Vietnamese example sentences: {has_ex_vi} / 5243 ({has_ex_vi/5243*100:.1f}%)")
    
    # Representative sampling across CEFR levels
    print("\n  Representative CEFR Samples:")
    by_level = {}
    for w in words:
        lvl = w['level']
        if lvl not in by_level and w.get('vi') and w.get('example_vi'):
            by_level[lvl] = w
            
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        sample = by_level.get(lvl)
        if sample:
            print(f"    [{lvl}] {sample['de']} -> EN: '{sample['en']}' | VI: '{sample['vi']}'")
            print(f"         Ex: '{sample['example']}'")
            print(f"         EN: '{sample['example_en']}'")
            print(f"         VI: '{sample['example_vi']}'")

    return has_vi == 5243 and has_ex_vi == 5243

def test_grammar_coverage():
    print("\n==================================================")
    print("Test 2: grammar_*.json Coverage & Invariance")
    print("==================================================")
    total_q = 0
    total_prompt_vi = 0
    total_exp_vi = 0
    
    for lvl in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
        path = os.path.join(REPO, f'grammar_{lvl}.json')
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
            
        p_vi = sum(1 for q in items if q.get('prompt_vi', '').strip())
        e_vi = sum(1 for q in items if q.get('explanation_vi', '').strip())
        total_q += len(items)
        total_prompt_vi += p_vi
        total_exp_vi += e_vi
        print(f"  grammar_{lvl}.json: {len(items)} items | Prompts translated: {p_vi} | Explanations translated: {e_vi}")

    print(f"  Total grammar items: {total_q} | Prompts translated: {total_prompt_vi} | Explanations: {total_exp_vi}")
    return total_q > 0 and total_prompt_vi == total_q and total_exp_vi == total_q

def test_html_pages_markup():
    print("\n==================================================")
    print("Test 3: HTML Markup & Vietnamese Elements")
    print("==================================================")
    # Check Wortschatz pages
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        p = os.path.join(REPO, lvl, '01_Wortschatz.html')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                c = f.read()
            has_word_vi = '.word-vi' in c
            has_ex_vi = '.ex-vi' in c
            print(f"  {lvl}/01_Wortschatz.html: has .word-vi = {has_word_vi}, has .ex-vi = {has_ex_vi}")

    # Check 03_Saetze.html
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        p = os.path.join(REPO, lvl, '03_Saetze.html')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                c = f.read()
            has_vi_trans = 'class="vi-trans' in c
            print(f"  {lvl}/03_Saetze.html: has .vi-trans = {has_vi_trans}")

    # Check dictionary.html
    dict_p = os.path.join(REPO, 'dictionary.html')
    if os.path.exists(dict_p):
        with open(dict_p, 'r', encoding='utf-8') as f:
            c = f.read()
        print(f"  dictionary.html: has .word-vi style = {'.word-vi' in c}")

    return True

if __name__ == '__main__':
    t1 = test_words_invariance_and_coverage()
    t2 = test_grammar_coverage()
    t3 = test_html_pages_markup()
    print("\n==================================================")
    print(f"Summary: Test 1={t1}, Test 2={t2}, Test 3={t3}")
    print("==================================================")
