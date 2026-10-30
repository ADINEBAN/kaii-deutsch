# -*- coding: utf-8 -*-
import re

exact_translations = {
    # B1 remaining
    "Printmedien verlieren gegenüber digitalen Angeboten zunehmend an Bedeutung.": "Truyền thông in ấn đang ngày càng đánh mất dần vị thế trước các dịch vụ số hóa.",
    "Quatsch! Das glaube ich dir nicht.": "Vớ vẩn! Tôi không tin lời bạn đâu.",
    "Die Qualität des Materials überzeugt die meisten Kunden.": "Chất lượng của chất liệu đã thuyết phục được hầu hết khách hàng.",
    "Sie spielt seit Jahren begeistert Xylophon im Schulorchester.": "Cô ấy đã say mê chơi đàn mộc cầm (xylophone) trong dàn nhạc của trường nhiều năm nay.",
    "Sie macht jeden Morgen Yoga, um den Tag entspannt zu beginnen.": "Cô ấy tập yoga mỗi sáng để khởi đầu một ngày mới thật thư thái.",
    "Zusammenfassend kann man sagen, dass Sprachenlernen viele Vorteile hat.": "Tóm lại, có thể khẳng định rằng việc học ngoại ngữ mang lại rất nhiều lợi ích.",
    "Zwar ist das Leben in der Großstadt teurer, aber es bietet auch mehr Möglichkeiten.": "Đúng là cuộc sống ở thành phố lớn đắt đỏ hơn, nhưng nó cũng mang lại nhiều cơ hội hơn.",

    # B2
    "Die von der Regierung beschlossenen Maßnahmen stoßen auf heftige Kritik.": "Các biện pháp do chính phủ ban hành đang vấp phải sự chỉ trích gay gắt.",
    "Bezüglich Ihrer Bewerbung möchten wir Ihnen mitteilen, dass Sie in die engere Auswahl gekommen sind.": "Liên quan đến hồ sơ ứng tuyển của bạn, chúng tôi xin thông báo rằng bạn đã lọt vào danh sách rút gọn.",
    "Dadurch, dass immer mehr Menschen in Städten leben, nimmt der Druck auf die Infrastruktur zu.": "Do ngày càng có nhiều người sinh sống tại các thành phố, áp lực lên cơ sở hạ tầng ngày một gia tăng.",
    "Der Minister betonte, die Regierung werde alle notwendigen Maßnahmen ergreifen.": "Bộ trưởng nhấn mạnh rằng chính phủ sẽ thực hiện mọi biện pháp cần thiết.",
    "Es sei denn, die Wirtschaftslage verbessert sich, werden weitere Stellen abgebaut.": "Trừ khi tình hình kinh tế được cải thiện, nếu không sẽ có thêm nhiều việc làm bị cắt giảm.",
    "Er dürfte inzwischen in Berlin angekommen sein.": "Chắc hẳn bây giờ anh ấy đã đến Berlin rồi.",
    "Falls sich die Prognosen bestätigen sollten, müsste man die Strategie grundlegend überdenken.": "Nếu các dự báo được xác nhận là đúng, người ta sẽ phải suy xét và định hình lại chiến lược một cách căn bản.",
    "Gesetzt den Fall, die Verhandlungen scheitern, müssten Alternativen in Betracht gezogen werden.": "Giả sử các cuộc đàm phán thất bại, người ta sẽ phải tính đến các phương án thay thế.",
    "Hätte man rechtzeitig investiert, wäre die Situation heute eine andere.": "Nếu người ta đầu tư kịp thời, tình hình ngày hôm nay đã hoàn toàn khác.",
    "Hinsichtlich der Qualität der Ausbildung gibt es erhebliche Unterschiede zwischen den Bundesländern.": "Về chất lượng đào tạo, đang có sự chênh lệch đáng kể giữa các bang.",
    "Indem man erneuerbare Energien fördert, kann man den CO2-Ausstoß deutlich reduzieren.": "Bằng cách thúc đẩy năng lượng tái tạo, người ta có thể cắt giảm đáng kể lượng khí thải CO2.",
    "Infolge der Pandemie hat sich das Arbeiten von zu Hause fest etabliert.": "Do hậu quả của đại dịch, hình thức làm việc tại nhà đã được thiết lập và duy trì vững chắc.",
    "Je komplexer die Gesellschaft wird, desto wichtiger wird interkulturelle Kompetenz.": "Xã hội càng trở nên phức tạp thì năng lực giao tiếp liên văn hóa càng trở nên quan trọng hơn.",
    "Die kürzlich veröffentlichte Studie belegt, dass regelmäßiger Sport das Wohlbefinden steigert.": "Nghiên cứu vừa được công bố chứng minh rằng việc tập thể dục đều đặn giúp nâng cao sức khỏe thể chất và tinh thần.",
    "Laut einer Erhebung des Statistischen Bundesamtes ist die Geburtenrate leicht gestiegen.": "Theo khảo sát của Cục Thống kê Liên bang, tỷ lệ sinh đã tăng nhẹ.",
    "Man muss davon ausgehen, dass sich die Lage in den nächsten Monaten nicht wesentlich verbessern wird.": "Người ta phải dự liệu rằng tình hình trong vài tháng tới sẽ không có chuyển biến cải thiện đáng kể nào.",
    "Mithilfe moderner Technologien lässt sich die Effizienz der Produktion deutlich steigern.": "Nhờ sự trợ giúp của công nghệ hiện đại, hiệu quả sản xuất có thể được nâng cao rõ rệt.",
    "Nichtsdestotrotz bleibt die Digitalisierung eine der größten Herausforderungen unserer Zeit.": "Dẫu vậy, chuyển đổi số vẫn là một trong những thách thức lớn nhất của thời đại chúng ta.",
    "Obgleich die Ergebnisse vielversprechend sind, bedarf es weiterer Forschung.": "Mặc dù các kết quả ban đầu rất triển vọng, vẫn cần phải có thêm các nghiên cứu tiếp theo.",
    "Sofern die Rahmenbedingungen stimmen, kann die Wirtschaft wieder wachsen.": "Miễn là các điều kiện khung được đảm bảo, nền kinh tế hoàn toàn có thể tăng trưởng trở lại.",
    "Selbst wenn man alle Argumente berücksichtigt, überwiegen die Vorteile.": "Ngay cả khi đã cân nhắc tất cả các luận điểm, những lợi ích mang lại vẫn chiếm ưu thế vượt trội.",
    "Trotz aller Bemühungen ist es bisher nicht gelungen, das Problem zu lösen.": "Bất chấp mọi nỗ lực, cho đến nay người ta vẫn chưa thể giải quyết triệt để được vấn đề.",
    "Ungeachtet der Kritik hält die Regierung an ihren Plänen fest.": "Bất chấp những lời chỉ trích, chính phủ vẫn kiên định với kế hoạch của mình.",
    "Vorausgesetzt, dass alle Beteiligten kooperieren, kann das Projekt erfolgreich abgeschlossen werden.": "Với điều kiện tất cả các bên liên quan cùng hợp tác, dự án có thể hoàn thành một cách tốt đẹp.",
    "Während die ältere Generation oft skeptisch ist, befürworten junge Menschen die Veränderung.": "Trong khi thế hệ lớn tuổi thường có tâm lý hoài nghi, thì giới trẻ lại rất ủng hộ sự thay đổi.",
    "Zu den wichtigsten Aufgaben der Zukunft gehört der Schutz der natürlichen Ressourcen.": "Một trong những nhiệm vụ trọng đại nhất của tương lai là việc bảo vệ các nguồn tài nguyên thiên nhiên.",

    # C1
    "Angesichts der rasanten technologischen Entwicklung stehen traditionelle Berufsfelder vor tiefgreifenden Umbrüchen.": "Trước sự phát triển công nghệ thần tốc, các ngành nghề truyền thống đang đứng trước những cuộc chuyển dịch sâu sắc.",
    "Es bedarf einer grundlegenden Überarbeitung der bestehenden Rechtsvorschriften, um Rechtssicherheit zu gewährleisten.": "Cần phải có sự sửa đổi căn bản các quy định pháp luật hiện hành nhằm đảm bảo tính pháp lý vững chắc.",
    "Es gilt zu bedenken, dass kurzfristige Erfolge nicht selten mit langfristigen Nachteilen erkauft werden.": "Cần phải suy xét rằng những thành công ngắn hạn thường phải đánh đổi bằng những bất lợi lâu dài.",
    "Dass die Ressourcen endlich sind, zwingt uns dazu, nachhaltige Alternativen zu entwickeln.": "Việc các nguồn tài nguyên là hữu hạn buộc chúng ta phải khẩn trương phát triển các giải pháp thay thế bền vững.",
    "Es entbehrt nicht einer gewissen Ironie, dass ausgerechnet jene Länder, die am wenigsten zum Klimawandel beitragen, am stärksten unter dessen Folgen leiden.": "Thật trớ trêu khi chính những quốc gia đóng góp ít nhất vào biến đổi khí hậu lại là những nơi phải gánh chịu hậu quả nặng nề nhất.",
    "Für den Fall, dass die Verhandlungen ergebnislos bleiben, haben die Gewerkschaften mit Streik gedroht.": "Trong trường hợp các cuộc đàm phán không mang lại kết quả, các công đoàn đã đe dọa sẽ tiến hành đình công.",
    "Ganz gleich, wie man zu diesem Thema steht, lässt sich die Notwendigkeit von Reformen kaum bestreiten.": "Bất kể người ta giữ lập trường nào về chủ đề này, tính cần thiết của cải cách là điều khó có thể phủ nhận.",
    "Es lässt sich nicht von der Hand weisen, dass die Globalisierung sowohl Chancen als auch Risiken birgt.": "Không thể phủ nhận một thực tế là toàn cầu hóa luôn tiềm ẩn cả cơ hội lẫn rủi ro.",
    "Im Hinblick auf die bevorstehenden Verhandlungen wäre es ratsam, alle Optionen sorgfältig abzuwägen.": "Hướng tới các cuộc đàm phán sắp tới, sẽ là sáng suốt nếu cân nhắc cẩn trọng mọi phương án.",
    "Inwiefern sich die theoretischen Erkenntnisse auf die Praxis übertragen lassen, bleibt abzuwarten.": "Mức độ mà các phát hiện lý thuyết có thể ứng dụng vào thực tiễn vẫn còn cần phải chờ xem xét thêm.",
    "Die kürzlich verabschiedeten Gesetze, die von der Opposition als unzureichend kritisiert worden sind, sollen zum Jahresende in Kraft treten.": "Những đạo luật mới được thông qua, dù bị phe đối lập chỉ trích là chưa thỏa đáng, dự kiến sẽ có hiệu lực vào cuối năm.",
    "Es liegt auf der Hand, dass eine bloße Symptombehandlung das eigentliche Problem nicht lösen wird.": "Một điều quá rõ ràng là việc chỉ xử lý phần ngọn sẽ không thể nào giải quyết được gốc rễ vấn đề.",
    "Es mangelt nicht an Ideen, wohl aber an der Bereitschaft, diese konsequent umzusetzen.": "Không hề thiếu những ý tưởng, nhưng lại thiếu đi sự sẵn sàng hành động quyết liệt để hiện thực hóa chúng.",
    "Nichtsdestoweniger bleibt die Frage offen, ob die vorgeschlagenen Maßnahmen ausreichen, um die gewünschten Ergebnisse zu erzielen.": "Dẫu vậy, vẫn còn bỏ ngỏ câu hỏi liệu các biện pháp được đề xuất có đủ sức mang lại kết quả mong muốn hay không.",
    "Sofern die Rahmenbedingungen stimmen und die notwendigen Ressourcen bereitgestellt werden, dürfte das Projekt innerhalb des vorgesehenen Zeitrahmens realisierbar sein.": "Miễn là các điều kiện khung được đáp ứng và nguồn lực cần thiết được phân bổ đầy đủ, dự án sẽ có thể hoàn thành trong khung thời gian dự kiến.",
    "Es steht außer Frage, dass die Sicherung der Biodiversität eine der drängendsten Aufgaben unserer Zeit darstellt.": "Không còn nghi vấn gì nữa, việc bảo tồn đa dạng sinh học là một trong những nhiệm vụ cấp bách nhất của thời đại chúng ta.",
    "Unter Berücksichtigung aller relevanten Faktoren ergibt sich ein differenzierteres Bild, als es die öffentliche Debatte vermuten lässt.": "Khi xem xét toàn diện tất cả các yếu tố liên quan, một bức tranh sâu sắc và đa chiều hơn sẽ hiện ra so với những gì dư luận đang suy đoán.",
    "Vor dem Hintergrund der aktuellen Krise erscheint eine grundlegende Neuausrichtung der Wirtschaftspolitik unerlässlich.": "Trước bối cảnh cuộc khủng hoảng hiện tại, việc tái định hướng căn bản chính sách kinh tế dường như là điều không thể thiếu.",
    "Es wäre verfehlt anzunehmen, dass technologischer Fortschritt allein die bestehenden gesellschaftlichen Probleme lösen kann.": "Sẽ là một sai lầm nếu nghĩ rằng tiến bộ công nghệ đơn thuần có thể tự giải quyết hết mọi vấn đề xã hội đang tồn tại.",
    "Zusammenfassend lässt sich konstatieren, dass die Komplexität der Problematik einen interdisziplinären Ansatz erfordert.": "Tóm lại có thể khẳng định rằng tính phức tạp của vấn đề đòi hỏi một cách tiếp cận liên ngành thấu đáo.",

    # C2
    "Die Brisanz des Themas lässt sich schwerlich bestreiten, zumal die jüngsten Entwicklungen die schlimmsten Befürchtungen bestätigt haben.": "Tính chất nhạy cảm và bùng nổ của chủ đề này khó có thể chối cãi, nhất là khi những diễn biến gần đây đã chứng thực những lo ngại tồi tệ nhất.",
    "Chronischer Fachkräftemangel, gepaart mit einer zunehmend alternden Gesellschaft, stellt eine der drängendsten Herausforderungen unserer Zeit dar.": "Tình trạng thiếu hụt trầm trọng nhân lực lành nghề, kết hợp với xã hội già hóa nhanh chóng, đang đặt ra một trong những thách thức sống còn nhất hiện nay.",
    "Dem landläufig verbreiteten Vorurteil, Digitalisierung führe unweigerlich zu Vereinsamung, ist mit Nachdruck zu widersprechen — sie eröffnet vielmehr neue Formen der Gemeinschaft.": "Định kiến phổ biến cho rằng số hóa tất yếu dẫn đến sự cô lập cần phải bị bác bỏ dứt khoát — trên thực tế, nó mở ra những hình thái kết nối cộng đồng hoàn toàn mới mẻ.",
    "Die Diskrepanz zwischen Anspruch und Wirklichkeit könnte kaum größer sein, was die Glaubwürdigkeit der handelnden Akteure nachhaltig untergräbt.": "Sự chênh lệch giữa kỳ vọng và thực tế khó có thể lớn hơn, điều này đang làm xói mòn sâu sắc uy tín của các bên liên quan.",
    "Es erübrigt sich beinahe, darauf hinzuweisen, dass eine bloße Symptombekämpfung der Tragweite des Problems in keiner Weise gerecht wird.": "Gần như là thừa thãi khi phải nhắc lại rằng việc chỉ chữa cháy triệu chứng hoàn toàn không đáp ứng nổi mức độ hệ trọng của vấn đề.",
    "Erst wenn man die historische Genese des Konflikts in den Blick nimmt, erschließen sich die tieferliegenden Ursachen der gegenwärtigen Krise.": "Chỉ khi người ta thấu thị được nguồn gốc lịch sử của cuộc xung đột, những nguyên nhân sâu xa của cuộc khủng hoảng hiện tại mới thực sự lộ rõ.",
    "Freilich ließe sich einwenden, dass die vorgeschlagenen Maßnahmen einer empirischen Grundlage entbehren — gleichwohl erscheinen sie als plausible Ansätze.": "Dĩ nhiên có thể phản bác rằng các biện pháp đề xuất còn thiếu cơ sở thực nghiệm — tuy nhiên chúng vẫn tỏ ra là những hướng tiếp cận rất hợp lý."
}

for lvl in ['B1', 'B2', 'C1', 'C2']:
    path = f'{lvl}/03_Saetze.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = 0
    for de, vi in exact_translations.items():
        pattern = re.compile(rf'<li><strong>{re.escape(de)}</strong>\s*—\s*(.*?)</li>')
        if pattern.search(content):
            content = pattern.sub(f'<li><strong>{de}</strong> — {vi}</li>', content)
            changed += 1

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Applied {changed} updates to {path}")

