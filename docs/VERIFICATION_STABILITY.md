# Xác minh bản 1.3.0 — 11/10/2026

| Kiểm tra | Kết quả |
| --- | --- |
| Mobile TypeScript `tsc --noEmit` | Đạt |
| Mobile unit tests | 34 đạt, 0 lỗi |
| Backend pytest | 22 đạt; 5 ca PostgreSQL native được skip cục bộ |
| Export Expo Android/iOS | Cả hai đạt, bundle Hermes và assets được tạo |
| Endpoint offline | Kiểm thử xác nhận 404; catalog online vẫn có dữ liệu |
| Đổi mật khẩu | Kiểm thử mật khẩu cũ sai/đúng, giữ phiên hiện tại, thu hồi phiên khác và đăng nhập bằng mật khẩu mới |
| Chạy nền | Kiểm thử lifecycle gỡ watcher, bỏ callback cũ, abort signal và HTTP; không đăng ký TaskManager/background-location |
| GPS | Kiểm thử timestamp đo thực, sai số không rõ/không hợp lệ, bán kính nhỏ, vùng sai số vượt biên, dwell/cooldown và dừng thủ công |
| Phiên/yêu thích | Kiểm thử mất mạng, token hết hạn, logout/restore và phản hồi cũ; khôi phục cục bộ khi server cũ mất kết nối |
| Consent | Kiểm thử lưu yêu cầu thu hồi và token theo origin, không xóa nhầm khi đổi server |

Backend chạy với PostgreSQL WASM (PGlite qua TCP) trong database riêng để kiểm tra SQL/API. Không coi đó là bằng chứng cho tranh chấp trên PostgreSQL native. CI hiện bật `NATIVE_POSTGRES=1` để chạy các ca worker lease, migration/publication đồng thời trên PostgreSQL cài trực tiếp; chưa chạy workflow GitHub trong phiên này.

Chưa xác minh trên điện thoại Android/iOS thật, mạng 4G thật, GPS ngoài trời/khóa màn hình hay máy chủ production. Xuất bundle thành công không thay thế các kiểm tra này; xem DEVICE_TEST.md. Địa chỉ HTTPS cố định cần máy chủ/named tunnel được cấu hình thật.

Không thay schema/migration đã phát hành. Bản 1.3 giữ revision `0002_worker_leases`; giữ database và `.env` khi cập nhật. Các kết quả trong VERIFICATION.md và VERIFICATION_OPERATIONS.md là lịch sử.
