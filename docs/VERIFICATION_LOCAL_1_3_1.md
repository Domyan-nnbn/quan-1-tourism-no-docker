# Xác minh bản cập nhật 1.3.1

- TypeScript `tsc --noEmit`: đạt.
- Mobile: 36/36 kiểm thử đạt, gồm 2 ca mới cho trạng thái GPS.
- Expo export Android: đạt (741 modules). Đây là export JavaScript/assets, không phải build APK native.
- Cấu hình build: kiểm tra bằng dữ liệu giả — Expo Go không yêu cầu khóa Maps; preview từ chối thiếu HTTPS/khóa Maps; cấu hình đủ sinh plugin Maps đúng. Không gọi dịch vụ ngoài.
- Backend: chỉ đổi câu thông báo rate limit; kiểm tra cú pháp Python đạt, không chạy lại bộ DB integration.
- Đã tìm trong source giao diện: không còn chuỗi hiển thị một phút/1 phút hoặc phần ước tính thời lượng. Không chỉnh nội dung nằm trong database người dùng.
- Chưa kiểm thử trên điện thoại thật, native APK, GitHub Actions hoặc server. Checklist trong UPDATE_LOCAL_1_3_1.md.
- Không tích hợp/gọi AI, không thêm migration hay dependency.
