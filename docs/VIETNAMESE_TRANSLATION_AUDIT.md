# Vietnamese Translation Audit & Implementation Specification

**Date:** 2026-10-17  
**Project:** WordFeather (`E:\DEUTSCH\wordfeather`)  
**Objective:** Add comprehensive, accurate Vietnamese translations beneath all existing English translations, glosses, example sentences, and learning content across the entire WordFeather platform while preserving all original German content strictly unchanged.

---

## 1. Executive Summary & Non-Negotiable Rules

### Rule A: German Content Invariance
The original German educational text is strictly immutable. No German headwords, articles, plurals, collocations, grammatical markers, example sentences, reading passages, exercise prompts, or answer keys may be altered, corrected, simplified, or normalized.

### Rule B: English-Gated Vietnamese Content
Vietnamese is **only** added where a corresponding English translation, gloss, equivalent, or explanation currently exists in educational learning content.
- German with English -> Add Vietnamese directly beneath English.
- German without English -> Leave unchanged (no Vietnamese inserted).
- Technical values, URLs, identifiers, programming code -> Leave untouched.

### Rule C: Platform-Wide Scope
The audit and migration cover:
1. Complete Vocabulary Dictionary (`words_final.json`, 5,243 headwords across CEFR A1–C2).
2. Vocabulary Example Sentences (5,243 example translations).
3. 6-Person Verb Sentence Drills (`person-sentences.json`, 4,775 words, ~28,650 drill pairs).
4. Grammar Exercises and Explanations (`grammar_a1.json` through `grammar_c2.json`, 881 quiz items).
5. Grammar Category Sections (`grammar_sections.json`).
6. Core Interactive Learning Modules (`quiz.html`, `grammar-quiz.html`, `placement-test.html`).
7. CEFR Static Educational Pages (`A1` through `C2`: `02_Grammatik.html`, `03_Saetze.html`, `04_Lesen.html`, `05_Hoeren.html`, `06_Sprechen.html`, `07_Schreiben.html`, `08_Musterpruefung.html`, `09_telc_Pruefungsformat.html`).

---

## 2. Source Data vs. Generated Artefacts Audit

| Path / File | Role | Type | Eligible English Fields | Existing Vietnamese Coverage | Migration Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `words_final.json` | Single source of truth for dictionary & vocabulary | Source Data | `en`, `example_en`, `person_sentences` (index 1 of pairs) | **0%** (0 / 5,243) | Add structured fields `vi` and `example_vi` to every entry. |
| `grammar_a1.json` | A1 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 293) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_a2.json` | A2 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 393) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_b1.json` | B1 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 33) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_b2.json` | B2 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 43) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_c1.json` | C1 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 52) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_c2.json` | C2 Grammar exercises | Source Data | `prompt_en`, `explanation_en` | **0%** (0 / 67) | Add `prompt_vi`, `explanation_vi`. |
| `grammar_sections.json`| Grammar topic navigation | Source Data | `en` (topic titles) | **0%** (0 / 46) | Add `vi` field. |
| `templates/dictionary.template.html` | Dictionary shell template | Source Template | UI markup & CSS | N/A | Add CSS for `.word-vi`, `.ex-vi`, update search logic. |
| `build.py` | Build pipeline orchestrator | Pipeline Script | `make_word_card()`, `build_wortschatz_page()` | N/A | Update card generator & Wortschatz table rows to render Vietnamese under English. |
| `split_dictionary.py` | Dictionary splitter & hub search builder | Pipeline Script | Search index extraction & `HUB_JS` | N/A | Support Vietnamese search indexing and dynamic search card rendering. |
| `A1..C2/01_Wortschatz.html` | Per-level vocabulary tables | Generated Output | N/A | Overwritten by `build.py` | Regenerate via `python build.py --all`. |
| `dictionary.html` & `dictionary-*.html` | Dictionary hub & 27 letter pages | Generated Output | N/A | Overwritten by `split_dictionary.py` | Regenerate via `python build.py --all`. |
| `dictionary-index.json` | Search index for hub | Generated Output | N/A | Overwritten by `split_dictionary.py` | Regenerate via `python build.py --all`. |
| `person-sentences.json` | 6-person drill database | Generated Output | N/A | Overwritten by `build.py` | Support Vietnamese translation in 3-tuples or companion field. |
| `quiz.html`, `grammar-quiz.html`, `placement-test.html` | Interactive test modules | Web Application | Prompts, hints, review cards | 0% | Update UI display functions to show Vietnamese directly under English. |
| `A1..C2/02_Grammatik.html` etc. | Educational study pages | Static HTML | Inline English translations in `<em>` and tables | 0% | Systematically add Vietnamese translation lines directly under English. |

---

## 3. Data Schema Extensions

### 3.1 `words_final.json`
```json
{
  "de": "backen",
  "en": "to bake",
  "vi": "nướng; làm bánh",
  "article": null,
  "level": "A1",
  "example": "Luisa kann gut Kuchen backen.",
  "example_en": "Luisa can bake cakes well.",
  "example_vi": "Luisa có thể làm bánh rất ngon.",
  "category": "Essen & Trinken"
}
```

### 3.2 `grammar_*.json`
```json
{
  "id": "a1-verb-sein-001",
  "prompt_de": "Guten Tag! Ich ____ Sabine Klein.",
  "prompt_en": "I am Sabine Klein.",
  "prompt_vi": "Tôi là Sabine Klein.",
  "explanation_de": "Das Verb 'sein' wird in der 1. Person Singular zu 'ich bin' konjugiert.",
  "explanation_en": "The verb 'sein' (to be) conjugates as 'ich bin' in the first person singular.",
  "explanation_vi": "Động từ 'sein' (thì, là, ở) được chia thành 'ich bin' ở ngôi thứ nhất số ít."
}
```

---

## 4. UI/UX Hierarchy & Styling

### 4.1 Dictionary Layout
```
[German Headword] [Article] [CEFR Badge] [Audio Button]
[English Meaning]
Tiếng Việt: [Vietnamese Meaning]
  [German Example Sentence] [Audio Button]
  [English Translation]
  Tiếng Việt: [Vietnamese Translation]
```

### 4.2 Styling Rules
- **CSS classes:** `.word-vi`, `.ex-vi`, `.gq-vi-hint`, `.vi-trans`.
- **Typography:** Modest sizing (`font-size: 0.88em` for glosses, `0.82em` for examples).
- **Color Scheme:** Visually subordinate neutral secondary (`color: var(--muted-text, #64748b)` in light mode, `#94a3b8` in dark mode).
- **Badge/Prefix:** Clear `Tiếng Việt: ` prefix or subtle indicator so learners immediately distinguish English and Vietnamese.
- **Audio Protection:** Strict separation ensuring only German triggers Thorsten-Voice TTS and only English triggers Web Speech API. Vietnamese text is never passed to TTS.

---

## 5. Verification & Quality Assurance Strategy

1. **Invariance Validation:** Automated diff confirming exact match of `de`, `example`, and grammatical metadata across all records.
2. **Coverage Verification:** 100% of eligible `en` entries must have non-empty `vi`. 100% of eligible `example_en` entries must have non-empty `example_vi`.
3. **Build Pipeline Test:** Full clean rebuild using `python build.py --all` and `python build.py --audit`.
4. **TTS Integrity Test:** Verify that clicking audio buttons on German reads German, and English buttons read English without reading Vietnamese.
5. **Interactive UI Verification:** Live browser testing across Dictionary, Wortschatz, and Quiz modules in both light and dark modes.
