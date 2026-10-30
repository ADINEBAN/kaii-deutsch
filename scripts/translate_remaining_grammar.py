#!/usr/bin/env python3
"""
scripts/translate_remaining_grammar.py
Complete all remaining English translations in Grammatik HTML files and grammar_summary.json.
Translates all English titles, table headers, descriptions, and inline example translations to natural Vietnamese.
"""

import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. Update A1/02_Grammatik.html ──
a1_path = os.path.join(REPO, 'A1', '02_Grammatik.html')
with open(a1_path, 'r', encoding='utf-8') as f:
    a1_content = f.read()

a1_replacements = [
    # Headers
    ("Pluralbildung — Beispiele / Plural Formation — Examples", "Pluralbildung — Beispiele / Tạo dạng số nhiều — Ví dụ"),
    ("Volle Deklination mit echten Nomen / Full Declension with Real Nouns", "Volle Deklination mit echten Nomen / Biến cách đầy đủ với danh từ thực tế"),
    ("Possessivpronomen — volle Tabelle / Full Table (Nominativ &amp; Akkusativ)", "Possessivpronomen — volle Tabelle / Bảng đại từ sở hữu đầy đủ (Nominativ &amp; Akkusativ)"),
    ("Regelmäßige Verben / Regular Verbs", "Regelmäßige Verben / Động từ theo quy tắc"),
    ("Unregelmäßige Verben / Irregular Verbs", "Unregelmäßige Verben / Động từ bất quy tắc"),
    ("Beispielverben, komplett konjugiert / Example Verbs, Fully Conjugated", "Beispielverben, komplett konjugiert / Các động từ ví dụ, chia đầy đủ"),
    ("Freizeitverben / Hobby Verbs", "Freizeitverben / Động từ chủ đề giải trí &amp; sở thích"),
    ("Vorstellung / Introducing Yourself", "Vorstellung / Giới thiệu bản thân"),
    ("einladen &amp; anfangen — voll konjugiert / Fully Conjugated", "einladen &amp; anfangen — voll konjugiert / Chia động từ đầy đủ"),
    ('Perfekt mit "haben" / Perfect with "haben" (die meisten Verben / most verbs):', 'Perfekt mit "haben" / Thì Perfekt với "haben" (hầu hết các động từ):'),
    ('Perfekt mit "sein" / Perfect with "sein" (Bewegung + Zustandsänderung / movement + change of state):', 'Perfekt mit "sein" / Thì Perfekt với "sein" (di chuyển + biến đổi trạng thái):'),
    ("Heute (Präsens) — Gestern (Perfekt) / Today — Yesterday", "Heute (Präsens) — Gestern (Perfekt) / Hôm nay — Hôm qua"),
    ("Präpositionen mit Dativ / Prepositions with Dative", "Präpositionen mit Dativ / Giới từ đi với Dativ"),
    ("Wo ist ...? — Lokale Präpositionen im Alltag / Where is ...? — Everyday Location Prepositions", "Wo ist ...? — Lokale Präpositionen im Alltag / Ở đâu? — Giới từ chỉ vị trí thông dụng"),
    ("Wegbeschreibung / Giving Directions", "Wegbeschreibung / Chỉ đường"),
    ("nicht <em>(không)</em> — für Verben, Adjektive, Adverbien / for verbs, adjectives, adverbs", "nicht <em>(không)</em> — für Verben, Adjektive, Adverbien / dùng cho động từ, tính từ, trạng từ"),
    ("kein <em>(không, không có cái nào)</em> — für Nomen / for nouns", "kein <em>(không, không có cái nào)</em> — für Nomen / dùng cho danh từ"),
    ("Uhrzeiten / Telling Time", "Uhrzeiten / Cách nói giờ"),
    ("Temporale Präpositionen / Temporal Prepositions", "Temporale Präpositionen / Giới từ chỉ thời gian"),
    ("Tageszeiten / Parts of the Day", "Tageszeiten / Các buổi trong ngày"),
    ("Zeiteinheiten / Units of Time", "Zeiteinheiten / Đơn vị thời gian"),
    ("Jahreszeiten / Seasons", "Jahreszeiten / Các mùa trong năm"),
    ("15. Demonstrativpronomen und Frageartikel / Demonstrative Pronouns and Question Article", "15. Demonstrativpronomen und Frageartikel / Đại từ chỉ định và từ để hỏi"),
    ("16. Komparation: gut, gern, viel / Comparison (Irregular)", "16. Komparation: gut, gern, viel / So sánh (Bất quy tắc: gut, gern, viel)"),
    ("17. Verben mit Dativ / Verbs with Dative", "17. Verben mit Dativ / Động từ đi với Dativ"),
    ("18. Höfliche Aufforderung: Konjunktiv II / Polite Requests", "18. Höfliche Aufforderung: Konjunktiv II / Yêu cầu lịch sự (Konjunktiv II)"),
    ("19. Zahlwörter: Ordinalzahlen und Datum / Ordinal Numbers and Dates", "19. Zahlwörter: Ordinalzahlen und Datum / Số thứ tự và ngày tháng"),
    ("20. Wortbildung: Nomen / Word Formation: Nouns", "20. Wortbildung: Nomen / Cấu tạo từ: Danh từ ghép"),
    ("21. Verben mit Akkusativ + Dativ / Verbs with Two Objects", "21. Verben mit Akkusativ + Dativ / Động từ với hai tân ngữ (Akkusativ + Dativ)"),
    ("22. Einkaufsdeklination / Shopping — Accusative in Practice", "22. Einkaufsdeklination / Mua sắm — Biến cách Akkusativ trong thực tế"),
    ("23. Preise / Prices &amp; Einkaufsdialog / Shopping Dialogue", "23. Preise / Giá cả &amp; Hội thoại mua sắm"),
    ("Übung 1: Artikel einsetzen / Fill in the article", "Übung 1: Artikel einsetzen / Điền mạo từ thích hợp"),
    ("Übung 2: Verben konjugieren / Conjugate the verbs", "Übung 2: Verben konjugieren / Chia động từ"),
    ("Übung 3: Perfekt bilden / Form the present perfect", "Übung 3: Perfekt bilden / Chia thì hiện tại hoàn thành (Perfekt)"),
    ("Übung 4: Wechselpräpositionen — Wo? oder Wohin? / Fill in the correct preposition", "Übung 4: Wechselpräpositionen — Wo? hoặc Wohin? / Điền giới từ thích hợp"),

    # Inline phrases
    ('<td><span style="color:#FFC000;font-weight:bold;">ihn</span> <em>(him)</em></td>', '<td><span style="color:#FFC000;font-weight:bold;">ihn</span> <em>(anh ấy)</em></td>'),
    ('<td>sie <em>(she)</em></td>', '<td>sie <em>(cô ấy)</em></td>'),
    ('<em>(plural)</em>', '<em>(số nhiều)</em>'),
    ('<td>unser <em>(our)</em></td>', '<td>unser <em>(của chúng tôi)</em></td>'),
    ('<em>(<span class="urdu">میں</span>)</em>', '<em>(tôi)</em>'),
    ('<em>(<span class="urdu">تم</span>)</em>', '<em>(bạn)</em>'),
    ('<em>(<span class="urdu">آپ</span>)</em>', '<em>(ngài / các ngài)</em>'),
    ('<em>(<span class="urdu">وہ</span>)</em>', '<em>(anh ấy / cô ấy)</em>'),
    ('— <span class="urdu">اس کے لیئے</span> <em>(Der Orangensaft ist für den Mann.)</em>', '<em>(Nước cam dành cho người đàn ông.)</em>'),
    ('<li><strong>Ich</strong> lerne Deutsch. <em>(I learn German.)</em></li>', '<li><strong>Ich</strong> lerne Deutsch. <em>(Tôi học tiếng Đức.)</em></li>'),
    ('- <strong>Geh</strong> nach Hause! <em>(Go home!)</em>', '- <strong>Geh</strong> nach Hause! <em>(Hãy về nhà đi!)</em>'),
    ('- <strong>Sprechen Sie</strong> bitte langsam! <em>(Please speak slowly!)</em>', '- <strong>Sprechen Sie</strong> bitte langsam! <em>(Xin ngài nói chậm lại một chút!)</em>'),
    ('- machen → <strong>gemacht</strong> <em>(made/done)</em>', '- machen → <strong>gemacht</strong> <em>(đã làm)</em>'),
    ('- lernen → <strong>gelernt</strong> <em>(learned)</em>', '- lernen → <strong>gelernt</strong> <em>(đã học)</em>'),
    ('- kaufen → <strong>gekauft</strong> <em>(bought)</em>', '- kaufen → <strong>gekauft</strong> <em>(đã mua)</em>'),
    ('<strong>Unregelmäßige Verben / Irregular verbs:</strong>', '<strong>Unregelmäßige Verben / Động từ bất quy tắc:</strong>'),
    ('- essen → <strong>gegessen</strong> <em>(eaten)</em>', '- essen → <strong>gegessen</strong> <em>(đã ăn)</em>'),
    ('- trinken → <strong>getrunken</strong> <em>(drunk)</em>', '- trinken → <strong>getrunken</strong> <em>(đã uống)</em>'),
    ('- schreiben → <strong>geschrieben</strong> <em>(written)</em>', '- schreiben → <strong>geschrieben</strong> <em>(đã viết)</em>'),
    ('- gehen → <strong>gegangen</strong> <em>(gone)</em>', '- gehen → <strong>gegangen</strong> <em>(đã đi)</em>'),
    ('- kommen → <strong>gekommen</strong> <em>(come)</em>', '- kommen → <strong>gekommen</strong> <em>(đã đến)</em>'),
    ('- fahren → <strong>gefahren</strong> <em>(driven)</em>', '- fahren → <strong>gefahren</strong> <em>(đã lái xe / đã đi)</em>'),
    ('<strong>Verben mit untrennbarem Präfix (kein ge-) / Inseparable verbs:</strong>', '<strong>Verben mit untrennbarem Präfix (kein ge-) / Động từ tiền tố không tách:</strong>'),
    ('- verstehen → <strong>verstanden</strong> <em>(understood)</em>', '- verstehen → <strong>verstanden</strong> <em>(đã hiểu)</em>'),
    ('- bezahlen → <strong>bezahlt</strong> <em>(paid)</em>', '- bezahlen → <strong>bezahlt</strong> <em>(đã thanh toán)</em>'),
    ('<strong>Trennbare Verben / Separable verbs:</strong>', '<strong>Trennbare Verben / Động từ tách:</strong>'),
    ('- einkaufen → <strong>eingekauft</strong> <em>(shopped)</em>', '- einkaufen → <strong>eingekauft</strong> <em>(đã mua sắm)</em>'),
    ('- anrufen → <strong>angerufen</strong> <em>(called)</em>', '- anrufen → <strong>angerufen</strong> <em>(đã gọi điện)</em>'),
    ('<li>Sie ist nach Hause <strong style="color:#00B050;">gegangen</strong>. <em>(She went home.)</em></li>', '<li>Sie ist nach Hause <strong style="color:#00B050;">gegangen</strong>. <em>(Cô ấy đã về nhà.)</em></li>'),
    ('<strong>durch</strong> <em>(through)</em>', '<strong>durch</strong> <em>(xuyên qua, qua)</em>'),
    ('<strong>gegen</strong> <em>(against/around)</em>', '<strong>gegen</strong> <em>(khoảng [thời gian], chống lại)</em>'),
    ('<strong>ohne</strong> <em>(without)</em>', '<strong>ohne</strong> <em>(không có, thiếu)</em>'),
    ('<strong>Weitere Akkusativ-Präpositionen / More Accusative Prepositions:</strong>', '<strong>Weitere Akkusativ-Präpositionen / Các giới từ Akkusativ khác:</strong>'),
    ('<strong>aus</strong> <em>(from)</em>', '<strong>aus</strong> <em>(từ, đến từ)</em>'),
    ('<strong>seit</strong> <em>(since)</em>', '<strong>seit</strong> <em>(từ khi, đã được [khoảng thời gian])</em>'),
    ('<strong>von</strong> <em>(from/of)</em>', '<strong>von</strong> <em>(từ, của)</em>'),
    ('<li>Ich komme <strong>aus der</strong> Türkei. <em>(I come from Turkey.)</em></li>', '<li>Ich komme <strong>aus der</strong> Türkei. <em>(Tôi đến từ Thổ Nhĩ Kỳ.)</em></li>'),
    ('<li>Ich fahre <strong>mit dem</strong> Bus. <em>(I go by bus.)</em></li>', '<li>Ich fahre <strong>mit dem</strong> Bus. <em>(Tôi đi bằng xe buýt.)</em></li>'),
    ("<li>Ich komme <strong>nicht</strong> aus Deutschland. <em>(I don't come from Germany.)</em></li>", "<li>Ich komme <strong>nicht</strong> aus Deutschland. <em>(Tôi không đến từ Đức.)</em></li>"),
    ("<li>Er arbeitet <strong>nicht</strong>. <em>(He doesn't work.)</em></li>", "<li>Er arbeitet <strong>nicht</strong>. <em>(Anh ấy không làm việc.)</em></li>"),
    ('<strong>und</strong> <em>(and)</em>', '<strong>und</strong> <em>(và)</em>'),
    ('<strong>aber</strong> <em>(but)</em>', '<strong>aber</strong> <em>(nhưng)</em>'),
    ('<strong>denn</strong> <em>(because)</em>', '<strong>denn</strong> <em>(vì, bởi vì)</em>'),
    ('<strong>weil</strong> <em>(because)</em>', '<strong>weil</strong> <em>(bởi vì, do)</em>'),
    ('<strong>wenn</strong> <em>(when/if)</em>', '<strong>wenn</strong> <em>(nếu, khi)</em>'),
    ('<strong>dass</strong> <em>(that)</em>', '<strong>dass</strong> <em>(rằng, là)</em>'),
    ("<li>8:00 — Es ist acht Uhr. <em>(It's eight o'clock.)</em></li>", "<li>8:00 — Es ist acht Uhr. <em>(Bây giờ là 8 giờ.)</em></li>"),
    ('<li>Ich schreibe <strong>ihm</strong> einen Brief. <em>(I write him a letter.)</em></li>', '<li>Ich schreibe <strong>ihm</strong> einen Brief. <em>(Tôi viết cho anh ấy một lá thư.)</em></li>'),
    ('<td>to come back</td>', '<td>trở về, quay lại</td>')
]

for old, new in a1_replacements:
    a1_content = a1_content.replace(old, new)

with open(a1_path, 'w', encoding='utf-8') as f:
    f.write(a1_content)
print("Updated A1/02_Grammatik.html")


# ── 2. Update A2/02_Grammatik.html and A2/02_Grammatik_neu.html ──
a2_reps = [
    ("(I'm staying home because it's raining.)", "(Tôi ở nhà vì trời đang mưa.)"),
    ("(I work because I need money.)", "(Tôi đi làm vì tôi cần tiền.)"),
    ("(I couldn't work yesterday.)", "(Hôm qua tôi không thể đi làm được.)"),
    ("Wenn ich Geld hätte, würde ich ein Fahrrad kaufen.</strong>", "Wenn ich Geld hätte, würde ich ein Fahrrad kaufen.</strong> <em>(Nếu tôi có tiền, tôi sẽ mua một chiếc xe đạp.)</em>"),
    ("Wenn ich ein Arzt wäre, würde ich den Kranken helfen.</strong>", "Wenn ich ein Arzt wäre, würde ich den Kranken helfen.</strong> <em>(Nếu tôi là bác sĩ, tôi sẽ giúp đỡ người bệnh.)</em>")
]

for fname in ['A2/02_Grammatik.html', 'A2/02_Grammatik_neu.html']:
    fp = os.path.join(REPO, fname)
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            c = f.read()
        for old, new in a2_reps:
            c = c.replace(old, new)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Updated {fname}")


# ── 3. Update C1/02_Grammatik.html ──
c1_path = os.path.join(REPO, 'C1', '02_Grammatik.html')
with open(c1_path, 'r', encoding='utf-8') as f:
    c1_content = f.read()

c1_replacements = [
    ('content="Grammatik C1 — Grammar | WordFeather"', 'content="Grammatik C1 — Ngữ pháp C1 | WordFeather"'),
    ('content="C1 Advanced grammar topics for the Goethe-Zertifikat and telc exam with clear explanations and examples."', 'content="Tổng hợp ngữ pháp tiếng Đức C1 nâng cao cho kỳ thi Goethe và telc với giải thích chi tiết và ví dụ thực tế."'),
    ('<h1 id="c1-grammatik-grammar">C1 Grammatik / Grammar</h1>', '<h1 id="c1-grammatik-grammar">C1 Grammatik / Ngữ pháp</h1>'),
    ('<h2 id="3-modalpartikeln-modal-particles">3. Modalpartikeln / Modal Particles</h2>', '<h2 id="3-modalpartikeln-modal-particles">3. Modalpartikeln / Hư từ tình thái (Modalpartikeln)</h2>'),
    ('<h2 id="7-irreale-vergleiche-unreal-comparisons">7. Irreale Vergleiche / Unreal Comparisons</h2>', '<h2 id="7-irreale-vergleiche-unreal-comparisons">7. Irreale Vergleiche / So sánh không có thật (als ob / als wenn)</h2>')
]

for old, new in c1_replacements:
    c1_content = c1_content.replace(old, new)

with open(c1_path, 'w', encoding='utf-8') as f:
    f.write(c1_content)
print("Updated C1/02_Grammatik.html")


# ── 4. Update C2/02_Grammatik.html ──
c2_path = os.path.join(REPO, 'C2', '02_Grammatik.html')
with open(c2_path, 'r', encoding='utf-8') as f:
    c2_content = f.read()

c2_replacements = [
    ('content="Grammatik C2 — Grammar | WordFeather"', 'content="Grammatik C2 — Ngữ pháp C2 | WordFeather"'),
    ('content="C2 Mastery grammar topics for the Goethe-Zertifikat and telc exam with clear explanations and examples."', 'content="Tổng hợp ngữ pháp tiếng Đức C2 chuyên sâu cho kỳ thi Goethe và telc với giải thích chi tiết và ví dụ thực tế."'),
    ('<h1 id="c2-grammatik-grammar">C2 Grammatik / Grammar</h1>', '<h1 id="c2-grammatik-grammar">C2 Grammatik / Ngữ pháp</h1>'),
    ('<h2 id="1-komplexe-satzgefuge-complex-sentence-structures">1. Komplexe Satzgefüge / Complex Sentence Structures</h2>', '<h2 id="1-komplexe-satzgefuge-complex-sentence-structures">1. Komplexe Satzgefüge / Cấu trúc câu phức nâng cao</h2>'),
    ('<h2 id="2-verbalperiphrasen-verbal-periphrases">2. Verbalperiphrasen / Verbal Periphrases</h2>', '<h2 id="2-verbalperiphrasen-verbal-periphrases">2. Verbalperiphrasen / Cụm diễn đạt tương đương động từ</h2>'),
    ('<h2 id="3-gehobenere-konjunktiv-i-formen-elevated-subjunctive-i">3. Gehobenere Konjunktiv-I-Formen / Elevated Subjunctive I</h2>', '<h2 id="3-gehobenere-konjunktiv-i-formen-elevated-subjunctive-i">3. Gehobenere Konjunktiv-I-Formen / Thể giả định I nâng cao (Konjunktiv I)</h2>'),
    ('<h2 id="4-stilistische-varianten-der-wortstellung-stylistic-word-order">4. Stilistische Varianten der Wortstellung / Stylistic Word Order</h2>', '<h2 id="4-stilistische-varianten-der-wortstellung-stylistic-word-order">4. Stilistische Varianten der Wortstellung / Các biến thể trật tự từ theo phong cách</h2>'),
    ('<h2 id="5-textgrammatik-text-grammar">5. Textgrammatik / Text Grammar</h2>', '<h2 id="5-textgrammatik-text-grammar">5. Textgrammatik / Ngữ pháp văn bản</h2>'),
    ('<h3 id="kohasionsmittel-cohesion-devices">Kohäsionsmittel / Cohesion Devices</h3>', '<h3 id="kohasionsmittel-cohesion-devices">Kohäsionsmittel / Phương tiện liên kết văn bản</h3>'),
    ('<h2 id="6-modalpartikeln-meisterhafter-einsatz-master-level-modal-particles">6. Modalpartikeln (Meisterhafter Einsatz) / Master-Level Modal Particles</h2>', '<h2 id="6-modalpartikeln-meisterhafter-einsatz-master-level-modal-particles">6. Modalpartikeln (Meisterhafter Einsatz) / Hư từ tình thái chuyên sâu</h2>'),
    ('<h2 id="7-besondere-konstruktionen-special-constructions">7. Besondere Konstruktionen / Special Constructions</h2>', '<h2 id="7-besondere-konstruktionen-special-constructions">7. Besondere Konstruktionen / Cấu trúc ngữ pháp đặc thù</h2>'),
    ('<h2 id="8-stilregister-style-registers">8. Stilregister / Style Registers</h2>', '<h2 id="8-stilregister-style-registers">8. Stilregister / Các phong cách ngôn ngữ (Trang trọng / Đời thường)</h2>'),
    ('<h2 id="ubungen-exercises">Übungen / Exercises</h2>', '<h2 id="ubungen-exercises">Übungen / Bài tập luyện tập</h2>')
]

for old, new in c2_replacements:
    c2_content = c2_content.replace(old, new)

with open(c2_path, 'w', encoding='utf-8') as f:
    f.write(c2_content)
print("Updated C2/02_Grammatik.html")


# ── 5. Update grammar_summary.json ──
with open('grammar_summary.json', 'r', encoding='utf-8') as f:
    gs = json.load(f)

# Title updates in grammar_summary.json
title_updates = {
    # A1
    "15. Demonstrativpronomen und Frageartikel / Demonstrative Pronouns and Question Article": "15. Demonstrativpronomen und Frageartikel / Đại từ chỉ định và từ để hỏi",
    "16. Komparation: gut, gern, viel / Comparison (Irregular)": "16. Komparation: gut, gern, viel / So sánh (Bất quy tắc: gut, gern, viel)",
    "17. Verben mit Dativ / Verbs with Dative": "17. Verben mit Dativ / Động từ đi với Dativ",
    "18. Höfliche Aufforderung: Konjunktiv II / Polite Requests": "18. Höfliche Aufforderung: Konjunktiv II / Yêu cầu lịch sự (Konjunktiv II)",
    "19. Zahlwörter: Ordinalzahlen und Datum / Ordinal Numbers and Dates": "19. Zahlwörter: Ordinalzahlen und Datum / Số thứ tự và ngày tháng",
    "20. Wortbildung: Nomen / Word Formation: Nouns": "20. Wortbildung: Nomen / Cấu tạo từ: Danh từ ghép",
    "21. Verben mit Akkusativ + Dativ / Verbs with Two Objects": "21. Verben mit Akkusativ + Dativ / Động từ với hai tân ngữ (Akkusativ + Dativ)",
    "22. Einkaufsdeklination / Shopping — Accusative in Practice": "22. Einkaufsdeklination / Mua sắm — Biến cách Akkusativ trong thực tế",
    "23. Preise / Prices &amp; Einkaufsdialog / Shopping Dialogue": "23. Preise / Giá cả &amp; Hội thoại mua sắm",
    # C1
    "3. Modalpartikeln / Modal Particles": "3. Modalpartikeln / Hư từ tình thái (Modalpartikeln)",
    "7. Irreale Vergleiche / Unreal Comparisons": "7. Irreale Vergleiche / So sánh không có thật (als ob / als nếu)",
    # C2
    "1. Komplexe Satzgefüge / Complex Sentence Structures": "1. Komplexe Satzgefüge / Cấu trúc câu phức nâng cao",
    "2. Verbalperiphrasen / Verbal Periphrases": "2. Verbalperiphrasen / Cụm diễn đạt tương đương động từ",
    "3. Gehobenere Konjunktiv-I-Formen / Elevated Subjunctive I": "3. Gehobenere Konjunktiv-I-Formen / Thể giả định I nâng cao (Konjunktiv I)",
    "4. Stilistische Varianten der Wortstellung / Stylistic Word Order": "4. Stilistische Varianten der Wortstellung / Các biến thể trật tự từ theo phong cách",
    "5. Textgrammatik / Text Grammar": "5. Textgrammatik / Ngữ pháp văn bản",
    "6. Modalpartikeln (Meisterhafter Einsatz) / Master-Level Modal Particles": "6. Modalpartikeln (Meisterhafter Einsatz) / Hư từ tình thái chuyên sâu",
    "7. Besondere Konstruktionen / Special Constructions": "7. Besondere Konstruktionen / Cấu trúc ngữ pháp đặc thù",
    "8. Stilregister / Style Registers": "8. Stilregister / Các phong cách ngôn ngữ (Trang trọng / Đời thường)",
    "Übungen / Exercises": "Übungen / Bài tập luyện tập"
}

for lvl, topics in gs.items():
    for t in topics:
        title = t.get('title', '')
        if title in title_updates:
            t['title'] = title_updates[title]
        # Also clean any inline English in html
        h = t.get('html', '')
        for old, new in a1_replacements + a2_reps + c1_replacements + c2_replacements:
            if old in h:
                h = h.replace(old, new)
        t['html'] = h

with open('grammar_summary.json', 'w', encoding='utf-8') as f:
    json.dump(gs, f, ensure_ascii=False, indent=2)

print("Updated grammar_summary.json successfully.")
