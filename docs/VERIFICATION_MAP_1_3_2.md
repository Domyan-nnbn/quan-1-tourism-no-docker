# Xác minh bản đồ 1.3.2

- TypeScript: đạt. Mobile: 39/39 kiểm thử đạt (3 kiểm thử mới cho bridge bản đồ).
- Export Android: đạt, 716 modules. Đây là bundle JS/assets, không phải APK native.
- Leaflet JS/CSS thật đóng gói trong mapAssets.json được chạy trong JSDOM, không tải tile công cộng: khởi tạo, vẽ POI/vòng bán kính/GPS, xóa dấu GPS, chọn POI, tooltip chứa văn bản có HTML không thực thi, đổi tâm, attribution và sự kiện tile load/error đều đạt.
- Cấu hình standalone: chấp nhận origin HTTPS mà không cần khóa Google Maps; dependency native Google Maps đã bỏ.
- Chưa chạy UI WebView trên điện thoại thật hoặc Android emulator. Thử kiểm tra bằng Chromium không chạy được do môi trường không tải được browser; không coi JSDOM là xác nhận hình ảnh native.
- Nền tile live qua mạng Wi-Fi/4G cần người dùng kiểm tra sau khi cập nhật. Không có tải tile tự động để crawl/prefetch, không thêm offline.
- Không sửa backend nghiệp vụ, migration, dữ liệu PostgreSQL hoặc khóa API.

Hướng dẫn: UPDATE_MAP_1_3_2.md.
