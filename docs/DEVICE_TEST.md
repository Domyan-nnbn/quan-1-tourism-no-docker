# Kiểm tra trên Expo Go thật

Các mục này chưa được tự động xác nhận trên điện thoại trong môi trường tạo mã.

1. Cùng Wi-Fi với backend; mở /health/ready bằng trình duyệt điện thoại.
2. Quét Expo QR, thấy 20 POI, tìm “Bến Thành”, lọc danh mục; đăng ký/đăng nhập user để lưu yêu thích.
3. Đổi tiếng Anh: UI du khách và bài đọc thay đổi. Yêu thích còn khi khởi động lại.
4. Chọn một POI, đọc Việt/Anh, dừng ngay; kiểm tra tốc độ, silent mode iOS.
5. Từ chối quyền vị trí: app vẫn cho xem/đọc; cấp quyền rồi bản đồ hiện vị trí thật.
6. Bật auto; di chuyển vào radius của POI. Nếu đang xa Quận 1, tạo POI thử nghiệm tại tọa độ thực của bạn qua admin (đánh dấu rõ nội dung thử).
7. Giữ trong vùng >3 giây: chỉ phát một lần; đứng yên không lặp. Rời vùng >radius+20m; cooldown đủ 5 phút mới phát lại.
8. App background/khóa màn hình: không cam kết GPS; khi mở lại phải có fix mới. Bài đọc dừng khi app background.
9. Tải gói → tắt mạng: văn bản/danh sách còn, map không được coi là offline. Kiểm tra giọng có offline trên hệ điều hành.
10. Tắt/bật consent, nghe một bài, đối chiếu thống kê admin. Tắt consent xóa sự kiện đã ghi của token đó khi server reachable.
11. Admin tạo draft chỉ có Việt: approve bị chặn. Thêm Anh, duyệt rồi publish; công khai mới thấy.
12. Tạo draft mới cho POI đã published: khách vẫn thấy phiên bản cũ tới khi publish bản mới.
13. Import Wikipedia: state PENDING → PROCESSING → COMPLETED, content dừng DRAFT; mất mạng thì retry/FAILED.
14. Logout: màn hình quản trị yêu cầu đăng nhập lại.
15. Kiểm tra text scaling, màn hình nhỏ và nút bấm, thông báo lỗi khi API tắt.

Kiểm tra tài khoản A/B, admin và cảnh báo xa theo `UPDATE_ACCOUNTS.md`.
