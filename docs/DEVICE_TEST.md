# Kiểm tra trên Expo Go thật — bản 1.3

Chưa chạy các mục này trên điện thoại thật trong môi trường sửa mã.

1. Mở URL API `/health/ready` trên điện thoại, thử cả Wi-Fi và 4G với URL HTTPS public; giữ API, worker, cloudflared và Expo mở.
2. Quét QR, xem danh sách, tìm Bến Thành, lọc; giao diện khách Việt/Anh, thuyết minh đủ Việt/Anh/Trung/Pháp/Nhật.
3. Cài đủ voice TTS trên máy; chọn giọng/tốc độ, nghe và dừng. Kiểm tra iOS silent mode.
4. Đăng ký A, lưu yêu thích; đăng xuất rồi đăng nhập B: không lẫn yêu thích. Đăng nhập lại A trên thiết bị khác và kiểm tra đồng bộ.
5. Từ chối GPS: vẫn xem/nghe thủ công. Cấp quyền và bật GPS, kiểm tra vị trí/sai số, cảnh báo xa Quận 1.
6. Bật tự đọc: fix ≤15 giây, sai số ≤25m và ≤nửa radius, vùng sai số nằm trong radius 3 giây. Không lặp khi đứng yên; ra ngoài radius+20m có xét sai số; cooldown 5 phút.
7. GPS trong nhà/nhà cao tầng/sai số không biết: không tự đọc. Thử POI radius 10m: sai số 6m phải bị chặn.
8. Trong lúc đọc/bật GPS, chuyển app hoặc khóa màn hình: giọng dừng, watcher gỡ. Mở lại phải lấy fix mới; không có hai watcher.
9. Tắt mạng/API: báo lỗi, không có nút tải offline hay danh sách fallback. Kết nối lại và bấm thử lại: phiên/yêu thích khôi phục nếu token còn hợp lệ.
10. URL tunnel cũ chết: xóa phiên trên máy, đổi URL mới và đăng nhập lại. Không chuyển token tài khoản sang server khác.
11. Đổi mật khẩu: sai mật khẩu cũ bị chặn; đúng thì phiên đang dùng còn, thiết bị khác phải đăng nhập lại; mật khẩu cũ không đăng nhập được.
12. Tắt consent khi mất mạng, đổi máy chủ rồi quay lại: xóa thống kê đúng server/token khi có mạng; không gửi tọa độ.
13. Admin nhập Wikipedia: PENDING → PROCESSING → COMPLETED; nháp chưa công khai. Duyệt cần đủ 5 ngôn ngữ; publish mới thay nội dung công khai.
14. Hai admin xuất bản hai phiên bản cùng POI: chỉ một PUBLISHED, pointer trỏ đúng phiên bản. Xác minh trên PostgreSQL thật.
15. Nhấn lưu/yêu thích liên tiếp và chuyển nền lúc request đang chạy: không hiện kết quả cũ, không tự gửi lại mutation.
16. Kiểm tra màn hình nhỏ, cỡ chữ lớn, nút bấm và bản đồ trên Android/iOS. Map cần mạng; xuất bundle không chứng minh map/GPS đã hoạt động trên máy thật.
