# -*- coding: utf-8 -*-

def update_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    orig = text
    for t, r in replacements:
        text = text.replace(t, r)
    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated {path}")
    else:
        print(f"No changes in {path}")

# A1/05_Hoeren.html
update_file('A1/05_Hoeren.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>\n<th>Deutsch</th>\n<th>Englisch</th>',
     '<th>Deutsch</th>\n<th>Tiếng Việt</th>\n<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>attention</td>', '<td>chú ý, thông báo</td>'),
    ('<td>delay</td>', '<td>chậm giờ, trễ chuyến</td>'),
    ('<td>platform</td>', '<td>đường ray, sân ga</td>'),
    ('<td>departure</td>', '<td>giờ khởi hành</td>'),
    ('<td>arrival</td>', '<td>giờ đến nơi</td>'),
    ('<td>stop</td>', '<td>điểm dừng (xe buýt, tàu)</td>'),
    ('<td>to transfer</td>', '<td>chuyển tàu, đổi chuyến</td>'),
    ('<td>exit</td>', '<td>lối ra</td>'),
    ('<td>special offer</td>', '<td>ưu đãi đặc biệt, giảm giá</td>'),
    ('<td>closed</td>', '<td>đã đóng cửa</td>')
])

# A1/07_Schreiben.html
update_file('A1/07_Schreiben.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>\n<th>Deutsch</th>\n<th>Englisch</th>',
     '<th>Deutsch</th>\n<th>Tiếng Việt</th>\n<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>first name</td>', '<td>tên gọi</td>'),
    ('<td>last name</td>', '<td>họ (tên gia đình)</td>'),
    ('<td>date of birth</td>', '<td>ngày tháng năm sinh</td>'),
    ('<td>place of birth</td>', '<td>nơi sinh</td>'),
    ('<td>gender</td>', '<td>giới tính</td>'),
    ('<td>male / female</td>', '<td>nam / nữ</td>'),
    ('<td>nationality</td>', '<td>quốc tịch</td>'),
    ('<td>address</td>', '<td>địa chỉ</td>'),
    ('<td>street</td>', '<td>tên đường</td>'),
    ('<td>house number</td>', '<td>số nhà</td>'),
    ('<td>phone number</td>', '<td>số điện thoại</td>'),
    ('<td>email address</td>', '<td>địa chỉ email</td>'),
    ('<td>profession</td>', '<td>nghề nghiệp</td>'),
    ('<td>marital status</td>', '<td>tình trạng hôn nhân</td>'),
    ('<td>single / married</td>', '<td>độc thân / đã kết hôn</td>'),
    ('<td>signature</td>', '<td>chữ ký</td>'),
    ('<td>date</td>', '<td>ngày tháng</td>'),
    ('<td>postal code</td>', '<td>mã bưu điện (PLZ)</td>'),
    ('<td>city</td>', '<td>địa phương / thành phố</td>'),
    ('<td>country</td>', '<td>quốc gia, đất nước</td>')
])

# A2/05_Hoeren.html
update_file('A2/05_Hoeren.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>\n<th>Deutsch</th>\n<th>Englisch</th>',
     '<th>Deutsch</th>\n<th>Tiếng Việt</th>\n<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>extension</td>', '<td>số máy lẻ</td>'),
    ('<td>answering machine</td>', '<td>máy trả lời tự động</td>'),
    ('<td>to call back</td>', '<td>gọi lại (điện thoại)</td>'),
    ('<td>busy</td>', '<td>máy bận</td>'),
    ('<td>to leave a message</td>', '<td>để lại lời nhắn</td>'),
    ('<td>delay</td>', '<td>sự chậm trễ</td>'),
    ('<td>cancellation</td>', '<td>hủy chuyến, mất điện/hỏng hóc</td>'),
    ('<td>diversion</td>', '<td>đường tránh, tuyến đường đổi hướng</td>'),
    ('<td>expected</td>', '<td>dự kiến</td>'),
    ('<td>construction</td>', '<td>công trình thi công</td>')
])

# A2/06_Sprechen.html
update_file('A2/06_Sprechen.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>', '<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>I suggest that we ...</td>', '<td>Tôi đề xuất rằng chúng ta...</td>'),
    ('<td>What do you think of ...?</td>', '<td>Bạn nghĩ sao về...?</td>'),
    ('<td>Agreed!</td>', '<td>Đồng ý! / Nhất trí!</td>'),
    ("<td>That's a good idea!</td>", '<td>Đó là một ý kiến hay!</td>'),
    ("<td>I don't think that's so good, because ...</td>", '<td>Tôi thấy điều đó chưa tốt lắm, vì...</td>'),
    ('<td>How about if we ...?</td>', '<td>Sẽ thế nào nếu chúng ta...?</td>'),
    ("<td>Let's do ...!</td>", '<td>Chúng mình cùng làm ... đi!</td>')
])

# A2/07_Schreiben.html
update_file('A2/07_Schreiben.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>', '<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>Dear ...</td>', '<td>Thân gửi... / ... thân mến</td>'),
    ('<td>Thanks for your message!</td>', '<td>Cảm ơn tin nhắn của bạn!</td>'),
    ("<td>I'm sorry.</td>", '<td>Tôi rất tiếc / Xin lỗi bạn.</td>'),
    ('<td>Do you feel like ...?</td>', '<td>Bạn có hứng thú ... không?</td>'),
    ('<td>Best regards</td>', '<td>Thân ái / Thân mến</td>'),
    ('<td>Dear Sir or Madam</td>', '<td>Kính gửi Quý bà và Quý ông</td>'),
    ("<td>I'm writing to you because ...</td>", '<td>Tôi viết thư này cho ngài vì...</td>'),
    ('<td>Could you please ...?</td>', '<td>Ngài có thể vui lòng ... được không?</td>'),
    ('<td>Sincerely</td>', '<td>Trân trọng kính chào</td>')
])

# B1/06_Sprechen.html
update_file('B1/06_Sprechen.html', [
    ('<th>Deutsch</th>\n<th>Englisch</th>', '<th>Deutsch</th>\n<th>Tiếng Việt</th>'),
    ('<td>I suggest that we ...</td>', '<td>Tôi đề xuất rằng chúng ta...</td>'),
    ('<td>How about if we ...?</td>', '<td>Sẽ thế nào nếu chúng ta...?</td>'),
    ('<td>We could ...</td>', '<td>Chúng ta hoàn toàn có thể...</td>'),
    ("<td>I think that's a good idea!</td>", '<td>Tôi thấy đó là một ý tưởng tuyệt vời!</td>'),
    ('<td>Yes, agreed!</td>', '<td>Vâng, tôi đồng ý!</td>'),
    ("<td>I don't think that's so good because ...</td>", '<td>Tôi thấy điều đó không hay lắm, bởi vì...</td>'),
    ('<td>I would rather ...</td>', '<td>Tôi muốn ... hơn</td>'),
    ('<td>Thank you for your presentation.</td>', '<td>Cảm ơn bạn rất nhiều vì bài thuyết trình.</td>'),
    ('<td>I found it particularly interesting that ...</td>', '<td>Tôi thấy đặc biệt thú vị khi...</td>'),
    ("<td>With us it's similar / different because ...</td>", '<td>Ở chỗ chúng tôi cũng tương tự / khác biệt, bởi vì...</td>'),
    ('<td>I have a question: ...</td>', '<td>Tôi có một câu hỏi:...</td>'),
    ('<td>I agree with you that ...</td>', '<td>Tôi đồng ý với bạn rằng...</td>')
])

# B1/07_Schreiben.html
update_file('B1/07_Schreiben.html', [
    ('<th>Funktion / Function</th>\n<th>Deutsch</th>\n<th>Englisch</th>',
     '<th>Chức năng</th>\n<th>Tiếng Đức</th>\n<th>Tiếng Việt</th>'),
    ('<td>These / Thesis</td>', '<td>Luận điểm</td>'),
    ('<td>I am of the opinion that ...</td>', '<td>Tôi cho rằng / Theo ý kiến tôi thì...</td>'),
    ('<td>Firstly ... / An important argument is ...</td>', '<td>Thứ nhất là... / Một luận điểm quan trọng là...</td>'),
    ('<td>Gegenargument / Counter</td>', '<td>Phản biện</td>'),
    ('<td>On the other hand ... / But one must consider ...</td>', '<td>Mặt khác... / Nhưng cũng cần phải cân nhắc...</td>'),
    ('<td>Beispiel / Example</td>', '<td>Ví dụ minh họa</td>'),
    ('<td>For example ... / A good example is ...</td>', '<td>Ví dụ như... / Một ví dụ điển hình là...</td>'),
    ('<td>Fazit / Conclusion</td>', '<td>Kết luận</td>'),
    ('<td>In summary ... / All in all ...</td>', '<td>Tóm lại... / Nhìn chung toàn diện...</td>'),
    ('You ordered a broken printer. Write to customer service.', 'Bạn đã đặt mua một chiếc máy in bị hỏng. Hãy viết thư gửi cho bộ phận chăm sóc khách hàng.')
])

