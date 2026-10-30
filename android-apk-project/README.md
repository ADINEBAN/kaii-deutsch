# KAII — Android APK Project

Dự án Android Studio WebView được tối ưu riêng cho điện thoại **Realme GT Neo 2T**:
- Tần số quét 120Hz mượt mà (Hardware Acceleration)
- Giao diện AMOLED Deep Dark `#070a13`
- Vuốt xuống để tải lại trang (Swipe-to-refresh)
- Tự động kết nối tới server local: `http://192.168.1.5:8080/m`

## Cách Build file APK

### Cách 1: Dùng Android Studio
1. Mở Android Studio -> Chọn **Open** -> Chọn thư mục `android-apk-project`.
2. Vào menu **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
3. Android Studio sẽ sinh file `app-debug.apk` tại `app/build/outputs/apk/debug/app-debug.apk`.
4. Chép file vào điện thoại Realme GT Neo 2T và cài đặt.

### Cách 2: Dùng lệnh dòng lệnh (nếu có Gradle)
```bash
cd android-apk-project
./gradlew assembleDebug
```

