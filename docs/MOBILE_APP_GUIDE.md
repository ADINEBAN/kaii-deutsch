# 📱 Hướng Dẫn Sử Dụng Mobile App WordFeather Cho Realme GT Neo 2T

Phiên bản ứng dụng di động được thiết kế riêng cho điện thoại **Realme GT Neo 2T** (tỷ lệ màn hình 20:9, tấm nền Super AMOLED 120Hz) với phong cách thiết kế **Liquid Glass (Kính mờ cao cấp)** và đầy đủ 100% chức năng học tiếng Đức như trên web.

> **Lưu ý quan trọng**: Phiên bản web hiện tại trên laptop được giữ nguyên vẹn 100%, không bị ảnh hưởng hay thay đổi giao diện.

---

## 🚀 1. Cách Để Laptop Làm Local Server

Để điện thoại Realme GT Neo 2T có thể kết nối với laptop và phát âm qua mô hình giọng đọc Thorsten TTS:

### Bước 1: Kết nối chung mạng
- Đảm bảo **Laptop** và **Realme GT Neo 2T** đang kết nối vào **cùng một mạng Wi-Fi**.
- *Hoặc*: Bật **Điểm phát sóng di động (Hotspot)** từ điện thoại Realme rồi lấy laptop kết nối vào mạng Wi-Fi đó.

### Bước 2: Khởi động Server trên Laptop
Trên laptop, bạn chỉ cần mở terminal và chạy:
```bash
./run_local.sh
```
*(Hoặc chạy lệnh: `python3 dev_server.py`)*

Server sẽ tự động:
1. Bật container giọng đọc Thorsten TTS (Docker).
2. Lắng nghe trên cổng `8080` ở tất cả các card mạng (`0.0.0.0`).
3. Tự động hiển thị địa chỉ IP nội bộ của laptop, ví dụ:
   ```text
   📱 DÀNH CHO ĐIỆN THOẠI REALME GT NEO 2T:
      👉 http://192.168.1.15:8080/m
   ```

---

## 📲 2. Cài Đặt App Vào Màn Hình Chính Realme GT Neo 2T

Nhờ kiến trúc PWA (Progressive Web App), bạn có thể cài đặt WordFeather thành một App Android độc lập mà không cần qua Google Play:

1. Mở trình duyệt **Google Chrome** (hoặc trình duyệt mặc định) trên Realme GT Neo 2T.
2. Nhập địa chỉ hiển thị trên laptop: `http://<IP-LAPTOP>:8080/m` (ví dụ: `http://192.168.1.15:8080/m`).
3. Khi trang web tải xong, bạn sẽ thấy thanh thông báo cài đặt hoặc:
   - Nhấn vào biểu tượng **3 chấm (⋮)** ở góc trên bên phải Chrome.
   - Chọn **"Cài đặt ứng dụng"** (Install app) hoặc **"Thêm vào Màn hình chính"** (Add to Home screen).
   - Nhấn **Cài đặt**.
4. Biểu tượng **WordFeather** với logo lông vũ sẽ xuất hiện ngay trên màn hình chính điện thoại của bạn.
5. Khi mở từ icon này, ứng dụng sẽ chạy **toàn màn hình (Standalone Native)**, không có thanh địa chỉ trình duyệt, hiệu ứng phản hồi siêu nhạy ở tần số quét **120Hz**.

---

## ✨ 3. Bố Cục & Các Chức Năng Đầy Đủ Trên Mobile

Giao diện được bố trí theo công thái học ngón tay cái (**Thumb-Zone Friendly**) với thanh điều hướng đáy (Bottom Navigation Bar) gồm 5 mục:

### 🔍 1. Tra từ (Dictionary)
- **Tìm kiếm tức thì**: Tra cứu thần tốc trong toàn bộ 5.243 từ vựng theo cả tiếng Đức và tiếng Việt.
- **Bộ lọc nhanh**: Lọc theo cấp độ (A1 đến C2) và từ loại (Danh từ, Động từ, Tính từ).
- **Màu sắc mạo từ**: Phân biệt trực quan qua huy hiệu kính phát sáng:
  - `der` (Maskulin): Màu xanh Sapphire
  - `die` (Feminin): Màu hồng Ruby
  - `das` (Neutrum): Màu xanh Emerald
  - `pl.` (Số nhiều): Màu vàng Gold
- **Phát âm chuẩn**: Nhấn nút loa 🔊 để nghe phát âm từ Thorsten TTS trực tiếp từ laptop.
- **Ví dụ thực tế**: Kèm bản dịch nghĩa tiếng Việt đời sống.
- **Theo ngôi**: Mở rộng các câu ví dụ chia theo từng ngôi `ich`, `du`, `er/sie/es`...

### 📖 2. Ngăn Kéo Chia Động Từ (Conjugation Drawer)
- Nhấn nút **"📖 Chia động từ"** ở bất kỳ động từ nào.
- Một ngăn kéo kính mờ (Bottom Sheet) sẽ trượt từ đáy màn hình lên hiển thị đầy đủ bảng chia thì:
  - Hiện tại (Präsens)
  - Quá khứ (Präteritum)
  - Hoàn thành (Perfekt)
  - Giả định II (Konjunktiv II)
  - Mệnh lệnh (Imperativ)
- **Chạm vào bất kỳ dạng động từ nào** để nghe phát âm ngay lập tức.

### 📚 3. Từ vựng theo 37 Chủ đề (Wortschatz)
- Duyệt từ vựng theo 37 chủ đề đời sống: *Gia đình & Con người, Ăn uống, Nhà ở, Mua sắm, Du lịch, Công nghệ...*
- Có số lượng từ cho từng chủ đề theo cấp độ được chọn.

### 💬 4. Mẫu câu giao tiếp A–Z (Sätze)
- Toàn bộ 1.708 câu giao tiếp thực tế từ A1 đến C2.
- Thanh trượt chữ cái (A → Z) giúp định vị câu mẫu cực nhanh.
- Có nút phát âm từng câu và bản dịch tiếng Việt thực tế.

### 📖 5. Ngữ pháp (Grammatik)
- 117 chủ điểm ngữ pháp trọng tâm theo 6 cấp độ A1 đến C2.
- Dạng thẻ accordion kính mờ thu gọn/mở rộng mượt mà kèm bảng tra cứu.

### ⚡ 6. Luyện tập & Mini Games (4 Chế độ)
- **🃏 Lật thẻ 3D (Flashcard)**: Thẻ kính 3D lật mượt mà giữa mặt trước (tiếng Đức) và mặt sau (tiếng Việt) khi chạm. Nút nghe phát âm, đánh dấu thuộc/chưa thuộc kèm đếm tiến độ.
- **🔗 Game Nối từ (Word Matching)**: Game tương tác trực quan với 6 cặp thẻ (12 ô). Chạm 1 ô tiếng Đức và 1 ô tiếng Việt tương ứng để nối cặp. Tự động phát âm củng cố khi nối đúng, rung báo lỗi khi chọn sai, bảng tổng kết cúp vàng kèm số lần thử.
- **📝 Trắc nghiệm Đức → Việt**: Hiển thị từ vựng tiếng Đức kèm nút nghe phát âm, chọn nghĩa tiếng Việt chuẩn xác trong 4 phương án.
- **🎯 Trắc nghiệm Việt → Đức**: Hiển thị nghĩa tiếng Việt cùng ngữ cảnh câu ví dụ, bạn chọn từ vựng tiếng Đức chính xác (kèm mạo từ der/die/das). Hệ thống phát âm ngay từ tiếng Đức chuẩn xác để bạn vừa học mặt chữ vừa luyện nghe.

---

## 🎨 4. Bộ Icon Tinh Gọn Không Màu (Monochrome Iconify)
- Toàn bộ icon trong bản mobile đã được chuyển sang thư viện **Iconify** với phong cách **Lucide Line thuần nét không màu (Monochrome)** theo màu chữ kính (`currentColor`).
- Không dùng emoji sặc sỡ, đảm bảo giao diện công nghệ hiện đại, tối giản và chuyên nghiệp chuẩn Liquid Glass.
- Hoạt động 100% offline ngay cả khi không có mạng Internet.

