import re

def update_file(path, translations, title_de, title_vi, intro_vi):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update metadata and headers
    content = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title_de} — {title_vi} | WordFeather">', content)
    content = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{title_de} — {title_vi} | WordFeather">', content)
    content = content.replace('Quick jump:', 'Chuyển nhanh:')

    # Update title
    content = re.sub(r'<h1 id="[^"]*">(.*?) / Sentences from A to Z</h1>', f'<h1>\\1 / Mẫu câu từ A đến Z</h1>', content)
    content = re.sub(r'<h1>(.*?) / Sentences from A to Z</h1>', f'<h1>\\1 / Mẫu câu từ A đến Z</h1>', content)
    content = re.sub(r'<p>Beispielsätze für jeden Buchstaben mit deutscher und englischer Übersetzung\.', f'<p>Mẫu câu ví dụ cho từng chữ cái kèm bản dịch tiếng Việt thực tế.', content)

    # Replace sentences
    replaced = 0
    for de, vi in translations.items():
        pattern = re.compile(rf'<li><strong>{re.escape(de)}</strong>\s*—\s*.*?</li>')
        if pattern.search(content):
            content = pattern.sub(f'<li><strong>{de}</strong> — {vi}</li>', content)
            replaced += 1
        else:
            print(f"NOT FOUND in {path}: {de[:30]}")

    print(f"Replaced {replaced}/{len(translations)} sentences in {path}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# B1 Translations
b1 = {
    "Obwohl er Angst vor dem Fliegen hat, reist er oft ins Ausland.": "Mặc dù sợ đi máy bay, anh ấy vẫn thường xuyên đi du lịch nước ngoài.",
    "Aufgrund des schlechten Wetters wurde die Veranstaltung abgesagt.": "Do thời tiết xấu, sự kiện đã bị hủy bỏ.",
    "An deiner Stelle würde ich den Arzt anrufen.": "Nếu tôi là bạn, tôi sẽ gọi điện cho bác sĩ.",
    "Bevor ich nach Deutschland gezogen bin, habe ich sechs Monate Deutsch gelernt.": "Trước khi chuyển đến Đức, tôi đã học tiếng Đức trong 6 tháng.",
    "Die Bewerbung muss bis Freitag eingereicht werden.": "Hồ sơ ứng tuyển phải được nộp trước thứ Sáu.",
    "Ich bin der Meinung, dass Bildung der Schlüssel zum Erfolg ist.": "Tôi cho rằng giáo dục chính là chìa khóa dẫn tới thành công.",
    "Nachdem ich das Studium abgeschlossen hatte, fand ich schnell eine Stelle.": "Sau khi tốt nghiệp đại học, tôi nhanh chóng tìm được một công việc.",
    "Trotz der Schwierigkeiten hat sie die Prüfung bestanden.": "Bất chấp nhiều khó khăn, cô ấy đã vượt qua kỳ thi.",
    "Es wäre schön, wenn wir uns öfter treffen könnten.": "Sẽ thật tuyệt nếu chúng ta có thể gặp nhau thường xuyên hơn.",
    "Entweder wir fahren mit dem Zug oder wir fliegen.": "Hoặc là chúng ta đi tàu hỏa, hoặc là chúng ta đi máy bay.",
    "Er arbeitet ehrenamtlich, um Flüchtlingen zu helfen.": "Anh ấy làm công việc tình nguyện để giúp đỡ những người tị nạn.",
    "Falls Sie Fragen haben, können Sie mich jederzeit anrufen.": "Nếu ngài có thắc mắc, ngài có thể gọi cho tôi bất cứ lúc nào.",
    "Ich finde es wichtig, dass man tolerant gegenüber anderen Kulturen ist.": "Tôi thấy rất quan trọng khi mọi người biết cởi mở và tôn trọng các nền văn hóa khác.",
    "Die Gleichberechtigung von Männern und Frauen ist ein wichtiges Thema.": "Bình đẳng giới giữa nam và nữ là một chủ đề vô cùng quan trọng.",
    "Gesundheit ist wertvoller als Geld.": "Sức khỏe quý giá hơn tiền bạc.",
    "Hätte ich früher angefangen zu lernen, hätte ich die Prüfung besser bestanden.": "Nếu tôi bắt đầu học sớm hơn, tôi đã đạt kết quả thi tốt hơn rồi.",
    "Je nachdem, wie das Wetter wird, machen wir einen Ausflug oder bleiben zu Hause.": "Tùy thuộc vào thời tiết thế nào, chúng tôi sẽ đi dã ngoại hoặc ở nhà.",
    "Der Klimawandel ist eine der größten Herausforderungen unserer Zeit.": "Biến đổi khí hậu là một trong những thách thức lớn nhất của thời đại chúng ta.",
    "Laut einer Studie lernen Kinder Sprachen schneller als Erwachsene.": "Theo một nghiên cứu, trẻ em học ngoại ngữ nhanh hơn người lớn.",
    "Meiner Meinung nach sollte jeder mindestens eine Fremdsprache sprechen.": "Theo ý kiến của tôi, mỗi người nên nói được ít nhất một ngoại ngữ.",
    "Nicht nur die Sprache, sondern auch die Kultur zu kennen, ist wichtig.": "Không chỉ học ngôn ngữ mà hiểu biết về văn hóa cũng rất quan trọng.",
    "Obwohl er seit zehn Jahren in Deutschland lebt, vermisst er seine Heimat.": "Dù đã sống ở Đức được 10 năm, anh ấy vẫn luôn nhớ về quê hương.",
    "Recycling ist eine einfache Möglichkeit, die Umwelt zu schützen.": "Tái chế là một cách đơn giản để bảo vệ môi trường.",
    "Seitdem ich regelmäßig Sport treibe, fühle ich mich viel besser.": "Từ khi tập thể thao đều đặn, tôi cảm thấy khỏe khoắn hơn rất nhiều.",
    "Sowohl in der Schule als auch an der Uni wird Teamarbeit betont.": "Cả ở trường phổ thông lẫn trường đại học, làm việc nhóm đều rất được chú trọng.",
    "Statt sich zu beschweren, sollte man nach einer Lösung suchen.": "Thay vì phàn nàn, người ta nên tìm kiếm giải pháp.",
    "Trotz aller Schwierigkeiten bin ich optimistisch.": "Bất chấp mọi khó khăn, tôi vẫn luôn lạc quan.",
    "Um die Umwelt zu schützen, sollte man weniger Auto fahren.": "Để bảo vệ môi trường, chúng ta nên hạn chế đi ô tô.",
    "Verglichen mit anderen Ländern ist das Bildungssystem in Deutschland sehr gut.": "So với các quốc gia khác, hệ thống giáo dục ở Đức rất tốt.",
    "Wenn ich die Möglichkeit hätte, würde ich ein Jahr im Ausland leben.": "Nếu có cơ hội, tôi muốn sống ở nước ngoài một năm.",
    "Weder die Regierung noch die Industrie allein kann das Problem lösen.": "Cả chính phủ lẫn ngành công nghiệp đơn lẻ đều không thể giải quyết triệt để vấn đề này.",
    "Chronische Rückenschmerzen sind ein weit verbreitetes Leiden.": "Đau lưng mãn tính là một chứng bệnh phổ biến rộng rãi.",
    "Chancengerechtigkeit bedeutet, dass alle Menschen die gleichen Möglichkeiten haben.": "Bình đẳng cơ hội có nghĩa là tất cả mọi người đều có những cơ hội như nhau.",
    "Coole Fotos vom letzten Urlaub eignen sich nicht für eine Bewerbung.": "Những bức ảnh chụp sành điệu từ kỳ nghỉ không phù hợp để dùng trong hồ sơ xin việc.",
    "Ich habe einen Kredit bei der Bank beantragt.": "Tôi đã làm thủ tục xin vay tiền tại ngân hàng.",
    "Ihr monatliches Einkommen reicht kaum für die Miete und Lebensmittel.": "Thu nhập hàng tháng của cô ấy chỉ vừa đủ trả tiền thuê nhà và mua thực phẩm.",
    "Im Gegenteil. Dich ruft alle fünf Minuten jemand an.": "Ngược lại ấy chứ. Cứ 5 phút lại có người gọi điện cho bạn.",
    "Pressefreiheit ist ein Grundrecht in demokratischen Gesellschaften.": "Tự do báo chí là một quyền cơ bản trong các xã hội dân chủ.",
    "Plastikmüll im Meer schadet Fischen, Vögeln und dem gesamten Ökosystem.": "Rác thải nhựa trên biển gây hại cho các loài cá, chim và toàn bộ hệ sinh thái.",
    "Qualität hat ihren Preis — billige Produkte halten oft nicht lange.": "Chất lượng đi liền với giá cả — sản phẩm rẻ tiền thường không dùng được lâu bền.",
    "Quelle: Bundesamt für Statistik, Jahresbericht 2024.": "Nguồn: Cục Thống kê Liên bang, Báo cáo thường niên 2024.",
    "X-Beine können bei Kindern durch gezielte Gymnastik korrigiert werden.": "Chân vòng kiềng chữ X ở trẻ em có thể được uốn nắn nhờ các bài tập thể dục chuyên biệt.",
    "Yoga hilft nicht nur gegen Rückenschmerzen, sondern baut auch Stress ab.": "Yoga không chỉ giúp giảm đau lưng mà còn giải tỏa căng thẳng stress rất hiệu quả.",
    "Zwischen 8 und 17 Uhr ist das Bürgeramt für den Publikumsverkehr geöffnet.": "Văn phòng hành chính mở cửa phục vụ người dân từ 8 giờ đến 17 giờ.",
    "Zuverlässigkeit ist eine der wichtigsten Eigenschaften am Arbeitsplatz.": "Sự đáng tin cậy là một trong những phẩm chất quan trọng nhất tại nơi làm việc.",
    "Zivildienst war früher eine Alternative zum Wehrdienst in Deutschland.": "Trước đây tại Đức, phục vụ cộng đồng dân sự là một hình thức thay thế cho nghĩa vụ quân sự."
}

# B2 Translations
b2 = {
    "Angesichts der wachsenden Umweltprobleme müssen wir dringend handeln.": "Trước tình hình các vấn đề môi trường ngày càng gia tăng, chúng ta cần phải hành động khẩn cấp.",
    "Die Auswirkungen des Klimawandels lassen sich nicht mehr leugnen.": "Những tác động tiêu cực của biến đổi khí hậu không còn có thể phủ nhận được nữa.",
    "Aufgrund der steigenden Nachfrage wurde die Produktion erhöht.": "Do nhu cầu ngày càng tăng cao, sản lượng sản xuất đã được nâng lên.",
    "Es besteht kein Zweifel daran, dass künstliche Intelligenz unseren Alltag verändern wird.": "Không còn nghi ngờ gì nữa, trí tuệ nhân tạo sẽ làm thay đổi sâu sắc cuộc sống hàng ngày của chúng ta.",
    "Es gilt zu bedenken, dass jede Medaille zwei Seiten hat.": "Cần phải cân nhắc rằng vấn đề nào cũng luôn có hai mặt của nó.",
    "Im Gegensatz zu früher arbeiten heute viele Menschen im Homeoffice.": "Khác với trước đây, ngày nay rất nhiều người làm việc tại nhà (home office).",
    "In Anbetracht der Situation sollten wir vorsichtig sein.": "Xét thấy tình hình thực tế, chúng ta nên hết sức cẩn trọng.",
    "Infolgedessen verloren viele Menschen ihre Arbeit.": "Hậu quả là rất nhiều người đã bị mất việc làm.",
    "Je früher wir anfangen, desto schneller sind wir fertig.": "Chúng ta bắt đầu càng sớm thì càng nhanh chóng hoàn thành.",
    "Die Kehrseite der Medaille ist der Verlust von Privatsphäre.": "Mặt trái của vấn đề là sự suy giảm quyền riêng tư cá nhân.",
    "Laut aktuellen Prognosen wird die Wirtschaft in diesem Jahr wachsen.": "Theo các dự báo cập nhật nhất, nền kinh tế sẽ tăng trưởng trong năm nay.",
    "Man muss berücksichtigen, dass die Ressourcen begrenzt sind.": "Người ta cần phải lưu ý rằng nguồn tài nguyên là có hạn.",
    "Mithilfe moderner Technologien können wir Probleme effizienter lösen.": "Nhờ sự trợ giúp của công nghệ hiện đại, chúng ta có thể giải quyết các vấn đề hiệu quả hơn.",
    "Nach Ansicht von Experten ist eine Reform des Bildungssystems überfällig.": "Theo quan điểm của các chuyên gia, việc cải cách hệ thống giáo dục đã là quá hạn.",
    "Obgleich er gut vorbereitet war, fiel er durch die Prüfung.": "Mặc dù đã chuẩn bị rất kỹ lưỡng, anh ấy vẫn thi trượt.",
    "Das Pro und Kontra sollte gründlich abgewogen werden.": "Những điểm thuận lợi và bất lợi cần phải được cân nhắc kỹ càng.",
    "Die Qual der Wahl: Zu viele Optionen können überfordern.": "Nỗi khổ tâm khi đứng trước quá nhiều sự lựa chọn: quá nhiều phương án có thể gây quá tải.",
    "Rückblickend lässt sich sagen, dass die Entscheidung richtig war.": "Nhìn lại chặng đường đã qua, có thể khẳng định rằng quyết định đó là hoàn toàn đúng đắn.",
    "Sowohl ökonomische als auch ökologische Faktoren spielen eine Rolle.": "Cả các yếu tố kinh tế lẫn sinh thái môi trường đều đóng vai trò quan trọng.",
    "Trotz intensiver Verhandlungen konnte keine Einigung erzielt werden.": "Bất chấp các cuộc đàm phán căng thẳng, vẫn chưa đạt được sự đồng thuận nào.",
    "Ungeachtet der Kritik setzte der Minister seine Pläne durch.": "Bất chấp những lời chỉ trích, ngài bộ trưởng vẫn kiên quyết triển khai kế hoạch của mình.",
    "Von entscheidender Bedeutung ist die Motivation der Mitarbeiter.": "Động lực làm việc của nhân viên mang ý nghĩa quyết định sống còn.",
    "Während einige profitieren, haben andere das Nachsehen.": "Trong khi một số người hưởng lợi thì những người khác lại phải chịu thiệt thòi.",
    "Es zeichnet sich ab, dass der Trend anhalten wird.": "Đang ngày càng lộ rõ xu hướng này sẽ còn tiếp diễn.",
    "Zweifelsohne hat die Digitalisierung viele Vorteile gebracht.": "Không còn nghi ngờ gì nữa, quá trình chuyển đổi số đã mang lại rất nhiều lợi ích.",
    "Xylophon und Vibraphon gehören zur Familie der Stabspiele im Schlagwerk.": "Đàn mộc cầm (Xylophon) và Vibraphon thuộc bộ gõ định âm có thanh phím.",
    "Die Y-Achse eines Koordinatensystems zeigt die vertikalen Werte.": "Trục tung Y của hệ tọa độ biểu thị các giá trị thẳng đứng theo chiều dọc.",
    "Zivilcourage bedeutet, für demokratische Werte einzustehen, auch wenn es unbequem ist.": "Lòng can đảm công dân có nghĩa là sẵn sàng đứng lên bảo vệ các giá trị dân chủ, ngay cả khi gặp phiền toái.",
    "Zwecks besserer Übersichtlichkeit wurden die Daten tabellarisch aufbereitet.": "Nhằm mục đích tăng tính trực quan dễ hiểu, dữ liệu đã được tổng hợp dưới dạng bảng."
}

# C1 Translations
c1 = {
    "In Anbetracht der demografischen Entwicklung ist eine Reform des Rentensystems unumgänglich.": "Xét đến sự biến động nhân khẩu học, việc cải cách hệ thống lương hưu là điều không thể tránh khỏi.",
    "Die Argumentation des Autors hält einer kritischen Überprüfung nicht stand.": "Lập luận của tác giả không đứng vững trước sự thẩm định và phản biện khoa học.",
    "Es bedarf keiner weiteren Erklärung, dass die Bildungspolitik grundlegend reformiert werden muss.": "Không cần phải giải thích thêm rằng chính sách giáo dục cần phải được cải cách một cách căn bản.",
    "Derartige Maßnahmen erweisen sich bei näherer Betrachtung als kontraproduktiv.": "Những biện pháp như vậy khi xem xét kỹ lưỡng hơn lại cho thấy tác dụng ngược phản tác dụng.",
    "Es steht außer Frage, dass der technologische Fortschritt weitreichende Konsequenzen haben wird.": "Không còn nghi vấn gì nữa, sự tiến bộ công nghệ sẽ kéo theo những hệ quả sâu rộng.",
    "Die Behauptung entbehrt jeglicher wissenschaftlichen Grundlage.": "Khẳng định trên hoàn toàn thiếu cơ sở khoa học.",
    "Ganz abgesehen davon, dass die finanziellen Mittel ohnehin nicht ausreichen würden.": "Hoàn toàn chưa kể đến việc nguồn kinh phí đằng nào cũng không thể đủ được.",
    "Hinsichtlich der Machbarkeit des Projekts bestehen nach wie vor erhebliche Bedenken.": "Về tính khả thi của dự án, hiện vẫn còn nhiều băn khoăn lo ngại đáng kể.",
    "Infolgedessen sah sich die Unternehmensführung gezwungen, drastische Sparmaßnahmen einzuleiten.": "Hậu quả là ban lãnh đạo doanh nghiệp buộc phải áp dụng các biện pháp thắt lưng buộc bụng quyết liệt.",
    "Es lässt sich nicht von der Hand weisen, dass gravierende Mängel vorliegen.": "Không thể gạt bỏ một thực tế là đang tồn tại những thiếu sót và khuyết điểm nghiêm trọng.",
    "Die Konsequenzen dieser Entscheidung sind gegenwärtig noch gar nicht abzusehen.": "Những hệ quả của quyết định này ở thời điểm hiện tại thậm chí vẫn chưa thể lường hết được.",
    "Letzten Endes läuft die Debatte auf die Frage hinaus, wer die Kosten tragen soll.": "Suy cho cùng, cuộc tranh luận quy về một câu hỏi cốt lõi: ai sẽ là người gánh chịu chi phí.",
    "Maßgeblich für den Erfolg ist nicht zuletzt die Unterstützung durch die Öffentlichkeit.": "Yếu tố mang tính quyết định cho thành công không gì khác chính là sự ủng hộ của công chúng.",
    "Nichtsdestotrotz sollte man die Hoffnung auf eine friedliche Beilegung des Konflikts nicht aufgeben.": "Dẫu vậy, người ta không nên từ bỏ hy vọng vào một giải pháp hòa bình để giải quyết cuộc xung đột.",
    "Offensichtlich mangelt es an dem politischen Willen, die notwendigen Reformen anzupacken.": "Rõ ràng là đang thiếu đi ý chí chính trị để bắt tay thực hiện những cải cách cần thiết.",
    "Die Problematik liegt primär darin begründet, dass die Interessenlagen diametral entgegengesetzt sind.": "Vấn đề chủ yếu bắt nguồn từ chỗ lợi ích của các bên hoàn toàn đối nghịch nhau.",
    "Die Quintessenz des Berichts lässt sich in einem einzigen Satz zusammenfassen.": "Tinh hoa cốt lõi của bản báo cáo có thể được đúc kết lại trong một câu duy nhất.",
    "Die Relevanz dieser Thematik für die künftige Entwicklung kann kaum überschätzt werden.": "Tầm quan trọng của chủ đề này đối với sự phát triển trong tương lai không thể bị đánh giá thấp.",
    "Schlussendlich muss konstatiert werden, dass die bisherigen Bemühungen unzureichend waren.": "Cuối cùng phải nhìn nhận thực tế rằng những nỗ lực từ trước tới nay vẫn là chưa thỏa đáng.",
    "Die Tragweite dieses Beschlusses wird erst in einigen Jahren vollends sichtbar werden.": "Tầm ảnh hưởng sâu rộng của nghị quyết này sẽ chỉ thể hiện trọn vẹn sau một vài năm nữa.",
    "Ungeachtet aller Differenzen einigten sich die Parteien auf eine gemeinsame Erklärung.": "Bất chấp mọi bất đồng quan điểm, các bên đã thống nhất cùng đưa ra một tuyên bố chung.",
    "Von vornherein war klar, dass das Vorhaben auf erheblichen Widerstand stoßen würde.": "Ngay từ đầu đã thấy rõ rằng kế hoạch này sẽ vấp phải sự kháng cự đáng kể.",
    "Zusammenfassend lässt sich festhalten, dass dringender Handlungsbedarf besteht.": "Tổng kết lại có thể khẳng định chắc chắn rằng đang có nhu cầu hành động hết sức cấp thiết."
}

# C2 Translations
c2 = {
    "Es wäre vermessen anzunehmen, die Automatisierung werde ausschließlich Arbeitsplätze vernichten, ohne gleichzeitig neue Beschäftigungsfelder zu erschließen.": "Thật là hàm hồ nếu cho rằng tự động hóa sẽ chỉ phá hủy việc làm mà không đồng thời mở ra những lĩnh vực nghề nghiệp mới mẻ.",
    "Angesichts der sich abzeichnenden Krise drängt sich die Frage auf, ob die bisherigen Ansätze der Komplexität der Problematik gerecht werden.": "Trước cuộc khủng hoảng đang dần lộ diện, một câu hỏi cấp bách đặt ra là liệu các phương thức tiếp cận từ trước đến nay có đáp ứng nổi sự phức tạp của vấn đề hay không.",
    "Sei es auch noch so verlockend, die Schuld allein der Politik zuzuweisen — die Verantwortung liegt gleichermaßen bei jedem Einzelnen.": "Dù có cám dỗ đến đâu khi quy trút mọi lỗi lầm cho giới chính trị — trách nhiệm vẫn thuộc về từng cá nhân mỗi người.",
    "Dessen ungeachtet gilt es, die Errungenschaften der Aufklärung gegen ihre Verächter zu verteidigen, mag der Zeitgeist ihnen auch noch so feindlich gesinnt sein.": "Bất chấp điều đó, điều cốt yếu là phải kiên quyết bảo vệ những thành tựu của phong trào Khai sáng trước những kẻ khinh miệt, cho dù xu thế thời đại có vẻ đối địch đến đâu.",
    "Es entbehrt nicht einer gewissen Ironie, dass ausgerechnet jene, die vorgeben, die Freiheit zu schützen, deren Fundamente am nachhaltigsten untergraben.": "Thật trớ trêu khi chính những kẻ ngoài miệng luôn miệng bảo vệ tự do lại là những kẻ đang xói mòn nền tảng của nó một cách sâu sắc nhất.",
    "Die Fundamente einer offenen Gesellschaft stehen zur Disposition, wenn der gesellschaftliche Diskurs vollends erodiert.": "Nền móng của một xã hội mở sẽ bị lung lay nghiêm trọng nếu các cuộc đối thoại xã hội hoàn toàn bị xói mòn.",
    "Gerade weil die Globalisierung sowohl Gewinner als auch Verlierer hervorbringt, bedarf es eines differenzierten Diskurses, der der Komplexität der Materie Rechnung trägt.": "Chính vì toàn cầu hóa tạo ra cả người thắng cuộc lẫn kẻ thua cuộc, nên rất cần một cuộc thảo luận đa chiều và thấu đáo, phản ánh đúng tính chất phức tạp của vấn đề.",
    "Hätte man die Warnsignale nicht so beharrlich ignoriert, wäre die Katastrophe womöglich abwendbar gewesen — ein Umstand, der im Nachhinein umso bitterer anmutet.": "Nếu người ta không phớt lờ các tín hiệu cảnh báo một cách dai dẳng như vậy, thảm họa có lẽ đã có thể ngăn chặn được — một tình cảnh mà khi nhìn lại càng thấy cay đắng muôn phần.",
    "Inwiefern sich die auf theoretischer Ebene gewonnenen Erkenntnisse auf die gesellschaftliche Praxis übertragen lassen, bleibt eine offene und keineswegs triviale Frage.": "Mức độ mà những tri thức thu được trên bình diện lý thuyết có thể chuyển hóa vào thực tiễn xã hội vẫn là một câu hỏi mở và hoàn toàn không hề đơn giản.",
    "Koste es, was es wolle — die Bewahrung der demokratischen Grundwerte muss oberste Priorität genießen, zumal die Erosion demokratischer Institutionen weltweit besorgniserregende Ausmaße annimmt.": "Dù có phải trả giá bằng bất cứ điều gì — việc bảo tồn các giá trị dân chủ nền tảng phải được ưu tiên hàng đầu, nhất là khi sự xói mòn các thể chế dân chủ trên toàn cầu đang ở mức đáng báo động.",
    "Letzten Endes liegt es auf der Hand, dass eine nachhaltige Lösung nur durch einen interdisziplinären Ansatz zu erreichen ist, der sowohl ökonomische als auch ökologische und soziale Dimensionen berücksichtigt.": "Sau cùng, một điều hiển nhiên là giải pháp bền vững chỉ có thể đạt được thông qua phương pháp tiếp cận liên ngành, bao quát đồng thời các khía cạnh kinh tế, sinh thái và xã hội.",
    "Man tut gut daran, sich nicht von der vermeintlichen Simplizität der Fragestellung täuschen zu lassen, denn hinter der Oberfläche verbirgt sich ein Geflecht hochkomplexer Zusammenhänge.": "Người ta nên cẩn trọng để không bị đánh lừa bởi sự đơn giản biểu kiến của câu hỏi, bởi ẩn sau bề mặt ấy là một mạng lưới các mối tương quan vô cùng phức tạp.",
    "Nichtsdestoweniger wäre es verfehlt, die erzielten Fortschritte geringzuschätzen, mögen sie im Lichte der verbleibenden Herausforderungen auch bescheiden anmuten.": "Tuy nhiên, sẽ là sai lầm nếu coi nhẹ những bước tiến đã đạt được, dẫu chúng có vẻ khiêm tốn khi so sánh với những thách thức to lớn còn lại phía trước.",
    "Obschon die empirische Evidenz zu diesem Zeitpunkt noch lückenhaft ist, legen die vorläufigen Befunde den Schluss nahe, dass ein kausaler Zusammenhang besteht.": "Mặc dù bằng chứng thực nghiệm ở thời điểm hiện tại vẫn còn khiếm khuyết, các kết quả ban đầu đều chỉ ra rằng tồn tại một mối quan hệ nhân quả.",
    "Die Polemik, mit der die Debatte bisweilen geführt wird, droht den Blick auf die eigentlichen Sachfragen zu verstellen.": "Những luận điệu bút chiến quá khích đôi khi xuất hiện trong cuộc tranh luận đang đe dọa che khuất đi các vấn đề thực chất cốt lõi.",
    "Retrospektiv betrachtet war es ein Fehler, die langfristigen Konsequenzen zugunsten kurzfristiger Profite außer Acht zu lassen.": "Nhìn nhận theo góc độ hồi cứu, việc bỏ qua các hệ quả dài hạn chỉ để đổi lấy những món lợi nhuận ngắn hạn quả thực là một sai lầm nghiêm trọng.",
    "Sofern die gesellschaftlichen Rahmenbedingungen es zulassen und die notwendigen Ressourcen mobilisiert werden können, dürfte einer Umsetzung des ambitionierten Vorhabens nichts im Wege stehen.": "Miễn là các điều kiện khung của xã hội cho phép và các nguồn lực cần thiết được huy động đầy đủ, sẽ không có gì có thể cản trở việc hiện thực hóa dự án đầy tham vọng này.",
    "Die Tragweite dieser Entscheidung ist kaum zu überschätzen, da sie die Weichen für die kommenden Jahrzehnte stellen wird.": "Tầm quan trọng của quyết định này không thể nào đánh giá thấp, bởi nó sẽ định hình phương hướng và mở đường cho nhiều thập kỷ tới.",
    "Ungeachtet der berechtigten Einwände, die gegen den Vorschlag vorgebracht worden sind, sollte man das Kind nicht mit dem Bade ausschütten.": "Bất chấp những ý kiến phản bác chính đáng đã nêu ra đối với đề xuất, người ta cũng không nên vì loại bỏ cái xấu mà vô tình vứt bỏ luôn cả những điều quý giá.",
    "Vor dem Hintergrund der sich verschärfenden geopolitischen Spannungen erscheint eine grundlegende Neuausrichtung der Außenpolitik nicht nur wünschenswert, sondern geradezu unumgänglich.": "Trước bối cảnh những căng thẳng địa chính trị ngày càng leo thang, việc tái định hướng căn bản chính sách đối ngoại không chỉ là điều đáng mong đợi mà thực sự đã trở nên cấp thiết khôn cưỡng.",
    "Wie dem auch sei — die Fakten sprechen eine deutliche Sprache, und es wäre unverantwortlich, die Augen vor der Realität zu verschließen.": "Dù thế nào đi chăng nữa — các sự thật thực tế đã tự nói lên tất cả bằng một ngôn ngữ rõ ràng, và sẽ là vô trách nhiệm nếu người ta cứ nhắm mắt làm ngơ trước thực tại.",
    "Zusammenfassend lässt sich konstatieren, dass die Thematik einer weitaus differenzierteren Betrachtung bedarf, als sie ihr in der öffentlichen Debatte gemeinhin zuteilwird.": "Tóm lại có thể khẳng định rằng chủ đề này đòi hỏi một góc nhìn sâu sắc và phân hóa kỹ lưỡng hơn rất nhiều so với những gì nó thường nhận được trong các cuộc tranh luận công chúng."
}

update_file('B1/03_Saetze.html', b1, 'Sätze B1', 'Mẫu câu B1', 'Tuyển tập các mẫu câu tiếng Đức B1 chuẩn ngữ cảnh giao tiếp và thi chứng chỉ.')
update_file('B2/03_Saetze.html', b2, 'Sätze B2', 'Mẫu câu B2', 'Tuyển tập các mẫu câu tiếng Đức B2 chuẩn ngữ cảnh học thuật và đời sống.')
update_file('C1/03_Saetze.html', c1, 'Sätze C1', 'Mẫu câu C1', 'Tuyển tập các mẫu câu tiếng Đức C1 nâng cao chuyên sâu.')
update_file('C2/03_Saetze.html', c2, 'Sätze C2', 'Mẫu câu C2', 'Tuyển tập các mẫu câu tiếng Đức C2 thành thạo và văn phong bác học.')

