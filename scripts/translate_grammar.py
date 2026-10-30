#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate all remaining English explanations, table headers, and examples in grammar_summary.json
and 02_Grammatik*.html into accurate, natural Vietnamese.
"""

import json
import re

TRANSLATIONS = {
    # Full grammar explanations & rules
    'Modal verbs change the meaning of the main verb. The main verb goes to the end in its infinitive form.':
        'Động từ khuyết thiếu làm biến đổi ý nghĩa của động từ chính. Động từ chính luôn đứng ở cuối câu ở dạng nguyên mẫu.',
    'Take the stem of the verb and add the correct ending.':
        'Lấy gốc động từ và thêm đuôi chia tương ứng theo từng ngôi.',
    'Verbs ending in -t, -d, -n add an extra "e".':
        'Các động từ có gốc kết thúc bằng -t, -d, -n sẽ thêm âm "e" đệm khi chia.',
    'Many German verbs have a separable prefix. In main clauses, the prefix goes to the end.':
        'Nhiều động từ tiếng Đức có tiền tố tách. Trong câu chính, tiền tố sẽ tách ra và đứng ở vị trí cuối câu.',
    'The Perfekt is used for the past (in conversation).':
        'Thì Hiện tại hoàn thành (Perfekt) dùng để diễn tả các sự việc trong quá khứ (đặc biệt trong văn nói giao tiếp).',
    'These vowels sound different from English. Practice them with the example words.':
        'Các nguyên âm này phát âm khác biệt. Hãy luyện tập phát âm qua các từ ví dụ dưới đây.',
    'Danke an meinen Lehrer / Thanks to my teacher, Shamim Manzar.':
        'Lời cảm ơn gửi đến người thầy Shamim Manzar.',
    'The endings are the same as "ein/eine".':
        'Đuôi chia giống hệt như mạo từ không xác định "ein/eine".',
    'The verb is always in ':
        'Động từ luôn đứng ở vị trí số 2 trong câu trần thuật.',
    'In a main clause, the conjugated verb always stays in second position — no matter what comes first.':
        'Trong câu chính, động từ đã chia luôn luôn đứng ở vị trí thứ 2 — bất kể thành phần nào đứng ở đầu câu.',
    'In spoken German, the genitive is often replaced by "von" + dative, especially with names.':
        'Trong văn nói tiếng Đức, sở hữu cách (Genitiv) thường được thay thế bằng cấu trúc "von" + Dativ, đặc biệt khi đi với tên riêng.',
    'The "s"-genitive with names ("Zahirs Auto") and the "von + Dativ" version mean the same thing.':
        'Cấu trúc sở hữu thêm "s" với tên riêng ("Zahirs Auto") và cấu trúc "von + Dativ" đều mang ý nghĩa tương đương nhau.',
    'In the accusative masculine singular, the possessive article takes the ending -en.':
        'Ở cách Akkusativ giống đực số ít, quán từ sở hữu nhận thêm đuôi -en.',
    'Feminine job titles: usually the ending -in.':
        'Tên nghề nghiệp giống cái: thông thường sẽ thêm hậu tố -in.',
    'For polite requests, use könnten/würden instead of the imperative.':
        'Để đưa ra lời yêu cầu lịch sự, hãy sử dụng könnten hoặc würden thay cho câu mệnh lệnh.',
    'Form unreal sentences with "wenn".':
        'Thành lập câu điều kiện không có thật với "wenn".',
    'Connect the sentences.':
        'Nối các câu sau lại với nhau.',
    'Fill in the correct article:':
        'Điền mạo từ chính xác vào chỗ trống:',
    'Fill in the correct form.':
        'Điền dạng đúng của từ vào chỗ trống.',
    'Combining transport vocabulary with a "wenn"-clause.':
        'Kết hợp từ vựng phương tiện giao thông cùng mệnh đề "wenn".',
    'Comparative and superlative in context, including the "genauso ... wie" / "so ... wie" (just as ... as) equal-comparison pattern.':
        'So sánh hơn và so sánh nhất trong ngữ cảnh, bao gồm cấu trúc so sánh bằng "genauso ... wie" / "so ... wie" (bằng nhau như...).',
    'Example sentences with "es gibt".':
        'Các câu ví dụ thực tế với cấu trúc "es gibt" (có...).',
    'Example sentences with this construction.':
        'Các câu ví dụ thực tế với cấu trúc này.',
    'More Dativ+Akkusativ verb examples.':
        'Các câu ví dụ bổ sung cho động từ đi cùng 2 tân ngữ Dativ và Akkusativ.',
    'More practice examples with "wenn" for habitual/conditional actions.':
        'Các ví dụ luyện tập thêm với "wenn" diễn tả thói quen hoặc hành động có điều kiện.',
    'Nominativ relative clauses: the relative pronoun matches the personal pronoun it replaces.':
        'Mệnh đề quan hệ ở cách Nominativ: đại từ quan hệ tương ứng với đại từ nhân xưng mà nó thay thế.',
    'Akkusativ relative clauses: note that the verb still goes to the end of the relative clause.':
        'Mệnh đề quan hệ ở cách Akkusativ: lưu ý động từ luôn chuyển về đứng ở cuối mệnh đề quan hệ.',
    'Note — word order: subject + verb + dative (noun) + accusative (noun). If the accusative object is a pronoun, it comes before the dative: "Ich gebe ihn ihm" (I give it to him).':
        'Lưu ý trật tự từ: Chủ ngữ + Động từ + Tân ngữ Dativ (danh từ) + Tân ngữ Akkusativ (danh từ). Nếu tân ngữ Akkusativ là đại từ, nó sẽ đứng trước Dativ: "Ich gebe ihn ihm" (Tôi đưa nó cho anh ấy).',
    'Note: "Wie spät ist es?" / "Wie viel Uhr ist es?" both ask for the time. The informal format is used in everyday speech; the formal 24-hour format is used for timetables, opening hours, etc.':
        'Lưu ý: "Wie spät ist es?" và "Wie viel Uhr ist es?" đều dùng để hỏi giờ. Cách nói thông thường dùng trong đời sống hằng ngày; định dạng 24 giờ trang trọng dùng cho lịch trình, giờ mở cửa...',
    'Note: "was für ein" keeps ein-word endings; "welcher" declines like the definite article.':
        'Lưu ý: "was für ein" chia theo đuôi nhóm mạo từ ein; "welcher" biến đuôi theo mạo từ xác định.',
    '"Was für ein/eine" asks about the type/kind (uses ein-words); "welcher/welches/welche" asks about a specific choice from a known set (declines like the definite article).':
        '"Was für ein/eine" hỏi về chủng loại (dùng đuôi từ ein); "welcher/welches/welche" hỏi về một lựa chọn cụ thể trong nhóm đã biết (chia đuôi như mạo từ xác định).',
    '"halb" refers to the NEXT hour!':
        '"halb" trong tiếng Đức là chỉ RƯỠI về phía giờ TIẾP THEO (ví dụ halb 9 = 8 rưỡi)!',
    '"kein" for nouns with indefinite article or no article. "nicht" for everything else.':
        '"kein" dùng phủ định danh từ đi với mạo từ không xác định hoặc không có mạo từ. "nicht" dùng phủ định cho tất cả trường hợp còn lại.',
    '"man" stands for "everyone" or "an unspecified person" and conjugates like er/es/sie.':
        '"man" đại diện cho "người ta / mọi người" (ngôi chung chung không xác định) và chia động từ như er/es/sie.',
    'Practice questions and answers with reflexive verbs.':
        'Câu hỏi và câu trả lời luyện tập với động từ phản thân.',
    'Some verbs take only dative (gratulieren, helfen) or only accusative (treffen, sehen, fragen).':
        'Một số động từ chỉ đi với Dativ (gratulieren, helfen) hoặc chỉ đi với Akkusativ (treffen, sehen, fragen).',
    'Some verbs take two objects: a person (Dative) and a thing (Accusative).':
        'Một số động từ đi cùng 2 tân ngữ: người (Dativ) và vật (Akkusativ).',
    'These pronouns replace a noun with an indefinite or negated article.':
        'Các đại từ này thay thế cho danh từ đi cùng mạo từ không xác định hoặc mạo từ phủ định.',
    'Unreal/hypothetical "wenn"-clauses with Konjunktiv II.':
        'Mệnh đề giả định không có thật với "wenn" sử dụng Konjunktiv II.',
    'Das Passiv verschiebt den Fokus vom Handelnden auf die Handlung/das Objekt. / Passive shifts focus from the doer to the action/object.':
        'Thể bị động (Passiv) chuyển trọng tâm từ người thực hiện sang bản thân hành động hoặc đối tượng tiếp nhận.',
    'Adjective endings with no article, after the indefinite article, and after the definite article.':
        'Biến đuôi tính từ khi không có quán từ, sau quán từ không xác định và sau quán từ xác định.',
    '"Doch, ich..." = "Yes, I actually do..."':
        '"Doch, ich..." = "Có chứ, thực ra tôi có..." (dùng để khẳng định lại câu hỏi phủ định)',
    'doch = "yes, actually", used to contradict a negative question':
        'doch = "có chứ, thực ra là có", dùng để phản bác/khẳng định lại câu hỏi phủ định',
    'for all plurals, the pronoun is sie':
        'đối với tất cả danh từ số nhiều, đại từ thay thế là sie',
    'for both, we use the pronoun er':
        'chúng ta sử dụng đại từ er',
    'for both, we use the pronoun es':
        'chúng ta sử dụng đại từ es',
    'for both, we use the pronoun sie':
        'chúng ta sử dụng đại từ sie',
    'declines like the definite article':
        'chia đuôi giống như mạo từ xác định',
    'verb goes to the END':
        'động từ chuyển về vị trí CUỐI CÙNG',
    'word order stays the same':
        'trật tự từ giữ nguyên không đổi',
    'in conversation':
        'trong văn nói giao tiếp',

    # Modal verbs short labels in table header
    '(can)': '(có thể)',
    '(must)': '(phải)',
    '(may)': '(được phép)',
    '(want)': '(muốn)',
    '(should)': '(nên)',
    '(would like)': '(muốn / thích)',
    'can': 'có thể',
    'must': 'phải',
    'may': 'được phép',
    'want': 'muốn',
    'should': 'nên',
    'would like': 'muốn / thích',

    # Table headings
    'Vokal / Vowel': 'Nguyên âm',
    'Beispiele / Examples': 'Từ ví dụ',
    'Satzstruktur / Sentence structure:': 'Cấu trúc câu:',
    'Ende / end': 'Cuối câu',
    'Position 2': 'Vị trí 2',

    # Short pronoun / preposition translations
    '(to me)': '(cho tôi / với tôi)',
    '(to him)': '(cho anh ấy)',
    '(to her)': '(cho cô ấy)',
    '(my)': '(của tôi)',
    '(your)': '(của bạn)',
    '(his/its)': '(của anh ấy/nó)',
    '(her)': '(của cô ấy)',
    '(their/your)': '(của họ/của Ngài)',
    '(you, informal)': '(bạn, thân mật)',
    '(you, formal)': '(Ngài / Quý vị, trang trọng)',
    '(you all)': '(các bạn)',
    '(you all are)': '(các bạn là)',
    '(you all have)': '(các bạn có)',
    '(you all/they are)': '(các bạn / họ là)',
    '(you are)': '(bạn là)',
    '(you are, formal)': '(Ngài là)',
    '(you have)': '(bạn có)',
    '(you)': '(bạn)',
    '(we)': '(chúng tôi / chúng ta)',
    '(we are)': '(chúng tôi là)',
    '(we have)': '(chúng tôi có)',
    '(they)': '(họ)',
    '(they/you formal)': '(họ / Ngài)',
    '(they/you have)': '(họ / Ngài có)',
    '(he/she/it is)': '(anh ấy / cô ấy / nó là)',
    '(he/she/it has)': '(anh ấy / cô ấy / nó có)',
    '(I have)': '(tôi có)',
    '(to be)': '(thì, là, ở)',
    '(to have)': '(có)',
    '(to come)': '(đến)',
    '(to do/make)': '(làm)',
    '(to read)': '(đọc)',
    '(to speak)': '(nói)',
    '(to like)': '(thích)',
    '(not "eueren")': '(không phải "eueren")',
    '(no, not any)': '(không, không có cái nào)',
    '(not)': '(không)',
    '(for)': '(cho, dành cho)',
    '(with)': '(với, cùng với)',
    '(to)': '(đến, tới)',
    '(at/around)': '(vào lúc, quanh)',
    '(at/near)': '(tại, gần)',
    '(to/after)': '(đến / sau)',
    '(from 9 to 5)': '(từ 9 giờ đến 17 giờ)',
    '(on Monday)': '(vào thứ Hai)',
    '(at 8 o\'clock)': '(vào lúc 8 giờ)',
    '(at midday)': '(vào buổi trưa)',
    '(at night)': '(vào ban đêm)',
    '(in the morning)': '(vào buổi sáng)',
    '(in the late morning)': '(vào khoảng giữa sáng)',
    '(in the afternoon)': '(vào buổi chiều)',
    '(in the evening)': '(vào buổi tối)',
    '(in May)': '(vào tháng Năm)',
    '(in summer)': '(vào mùa hè)',
    '(It\'s half past eight.)': '(Bây giờ là 8 rưỡi.)',
    '(It\'s quarter past eight.)': '(Bây giờ là 8 giờ 15 phút.)',
    '(It\'s quarter to nine.)': '(Bây giờ là 9 giờ kém 15.)',
    '(It\'s quarter to nine)': '(Bây giờ là 9 giờ kém 15)',

    # Example sentence translations
    '(I can speak German.)': '(Tôi có thể nói tiếng Đức.)',
    '(You have to go now.)': '(Bây giờ bạn phải đi rồi.)',
    '(He had to get up early.)': '(Anh ấy đã phải thức dậy sớm.)',
    '(We wanted to drink tea.)': '(Chúng tôi đã muốn uống trà.)',
    '(I wasn\'t allowed to smoke here.)': '(Tôi đã không được phép hút thuốc ở đây.)',
    '(May I smoke here?)': '(Tôi có được phép hút thuốc ở đây không?)',
    '(I\'d like to drink a coffee.)': '(Tôi muốn uống một tách cà phê.)',
    '(I have learned German.)': '(Tôi đã học tiếng Đức.)',
    '(He has eaten a cake.)': '(Anh ấy đã ăn một chiếc bánh ngọt.)',
    '(He got up at 7.)': '(Anh ấy đã thức dậy lúc 7 giờ.)',
    '(I get up at 7.)': '(Tôi thức dậy lúc 7 giờ.)',
    '(We start at 9.)': '(Chúng tôi bắt đầu lúc 9 giờ.)',
    '(We shop at the supermarket.)': '(Chúng tôi mua sắm tại siêu thị.)',
    '(I\'ll call you tomorrow.)': '(Ngày mai tôi sẽ gọi điện cho bạn.)',
    '(Tomorrow I go to school.)': '(Ngày mai tôi đi học.)',
    '(I go to school.)': '(Tôi đi học.)',
    '(I am at school.)': '(Tôi đang ở trường học.)',
    '(I go to the doctor.)': '(Tôi đi khám bác sĩ.)',
    '(I went/drove to Berlin.)': '(Tôi đã đi Berlin.)',
    '(I walk through the park.)': '(Tôi đi bộ qua công viên.)',
    '(I buy you a pen.)': '(Tôi mua cho bạn một cây bút.)',
    '(You bring me a camera.)': '(Bạn mang cho tôi một chiếc máy ảnh.)',
    '(He/She sends you a book.)': '(Anh ấy/Cô ấy gửi cho bạn một cuốn sách.)',
    '(We give you all books.)': '(Chúng tôi tặng sách cho tất cả các bạn.)',
    '(You give me a watch as a gift.)': '(Bạn tặng tôi một chiếc đồng hồ đeo tay.)',
    '(I explain the structures to you.)': '(Tôi giải thích các cấu trúc cho bạn.)',
    '(I give it to him)': '(Tôi đưa nó cho anh ấy)',
    '(I\'m going to Pakistan on October 5th.)': '(Tôi sẽ đi Pakistan vào ngày 5 tháng 10.)',
    '(When is your birthday? — My birthday is on April 3rd.)': '(Khi nào là sinh nhật bạn? — Sinh nhật tôi vào ngày 3 tháng 4.)',
    '(Where is your bag?)': '(Túi xách của bạn ở đâu?)',
    '(Write your name!)': '(Hãy viết tên của bạn!)',
    '(His mother is cooking.)': '(Mẹ anh ấy đang nấu ăn.)',
    '(That\'s for you.)': '(Cái này dành cho bạn.)',
    '(That\'s my book.)': '(Đó là cuốn sách của tôi.)',
    '(The course starts at 10.)': '(Khóa học bắt đầu lúc 10 giờ.)',
    '(There are no parking spaces here.)': '(Ở đây không có chỗ đỗ xe.)',
    '(When are you coming back?)': '(Khi nào bạn sẽ quay lại?)',
    '(Are you taking the umbrella?)': '(Bạn có mang theo ô không?)',
    '(In the evening I watch TV.)': '(Buổi tối tôi xem ti vi.)',
    '(I\'ve been learning German for a year.)': '(Tôi đã học tiếng Đức được một năm rồi.)',
    '(I stayed at my grandma\'s — no movement, but still takes "sein".)': '(Tôi đã ở lại nhà bà — không chuyển động, nhưng vẫn đi với "sein".)',
    '(I don\'t know whether she has time.)': '(Tôi không biết liệu cô ấy có thời gian hay không.)',
    '(I think it\'s good that we\'re learning German.)': '(Tôi thấy rất tốt khi chúng ta đang cùng học tiếng Đức.)',
    '(I don\'t feel like dancing. → I don\'t feel like it. → What do you feel like then?)':
        '(Tôi không hứng thú khiêu vũ. → Tôi không thích việc đó. → Vậy bạn muốn làm gì?)',
    '(Question word + verb + subject + rest)': '(Từ để hỏi + Động từ + Chủ ngữ + Thành phần còn lại)',
    '(Verb comes first)': '(Động từ đứng ở vị trí đầu câu)',
    '(von deinem Lehrer / from your teacher)': '(từ người thầy của bạn)',
    'Put the ladder there.': 'Hãy đặt chiếc thang ở đằng kia.',
    'She has her account checked.': 'Cô ấy nhờ người kiểm tra tài khoản của mình.',
    'You should have the tyres changed before winter.': 'Bạn nên mang xe đi thay lốp trước khi mùa đông đến.',
    'He must have been sick.': 'Chắc chắn là anh ấy đã bị ốm.',
    'He might have missed the train.': 'Có thể là anh ấy đã bị lỡ chuyến tàu.',
    'The car is repaired — state': 'Chiếc xe đã được sửa xong — trạng thái',
    'The problem is solved — state': 'Vấn đề đã được giải quyết — trạng thái',
    'Be that as it may ...': 'Dù có thế nào đi chăng nữa...',
    'process — the door is being opened': 'tiến trình — cánh cửa đang được mở ra',
    'state — the door is open': 'trạng thái — cánh cửa đang mở'
}

def translate_html_text(html_text):
    result = html_text

    # Sort keys by length descending to replace longer matches first
    sorted_keys = sorted(TRANSLATIONS.keys(), key=len, reverse=True)
    for k in sorted_keys:
        v = TRANSLATIONS[k]
        result = result.replace(k, v)

    # General pattern cleanup
    # "(I speak...)" -> replace remaining "(...)" if obvious english
    # Replace (can) -> (có thể)
    result = re.sub(r'<th>können\s*<em>\(can\)</em></th>', '<th>können <em>(có thể)</em></th>', result)
    result = re.sub(r'<th>müssen\s*<em>\(must\)</em></th>', '<th>müssen <em>(phải)</em></th>', result)
    result = re.sub(r'<th>dürfen\s*<em>\(may\)</em></th>', '<th>dürfen <em>(được phép)</em></th>', result)
    result = re.sub(r'<th>wollen\s*<em>\(want\)</em></th>', '<th>wollen <em>(muốn)</em></th>', result)
    result = re.sub(r'<th>sollen\s*<em>\(should\)</em></th>', '<th>sollen <em>(nên)</em></th>', result)
    result = re.sub(r'<th>möchten\s*<em>\(would like\)</em></th>', '<th>möchten <em>(muốn/thích)</em></th>', result)

    result = re.sub(r'Satzstruktur\s*/\s*Sentence structure:', 'Satzstruktur / Cấu trúc câu:', result)
    result = re.sub(r'\(Ende\s*/\s*end\)', '(Cuối câu)', result)
    result = re.sub(r'Vokal\s*/\s*Vowel', 'Nguyên âm', result)
    result = re.sub(r'Beispiele\s*/\s*Examples', 'Từ ví dụ', result)

    return result

def main():
    print("Loading grammar_summary.json...")
    with open('grammar_summary.json', 'r', encoding='utf-8') as f:
        gram = json.load(f)

    changed_topics = 0
    total_topics = 0
    for lvl, topics in gram.items():
        for t in topics:
            total_topics += 1
            old_html = t['html']
            new_html = translate_html_text(old_html)
            if new_html != old_html:
                t['html'] = new_html
                changed_topics += 1

    print(f"Updated {changed_topics} of {total_topics} topics in grammar_summary.json.")

    with open('grammar_summary.json', 'w', encoding='utf-8') as f:
        json.dump(gram, f, ensure_ascii=False, indent=2)
    print("Saved updated grammar_summary.json successfully.")

    # Also update HTML source files
    import glob
    for fpath in sorted(glob.glob('*/02_Grammatik*.html')):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = translate_html_text(content)
        if new_content != content:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {fpath} with Vietnamese translations.")

if __name__ == '__main__':
    main()

