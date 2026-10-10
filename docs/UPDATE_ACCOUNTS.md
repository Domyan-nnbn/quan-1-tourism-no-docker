# Cập nhật tài khoản, yêu thích và cảnh báo khoảng cách

Bản dành cho dự án `D:\cnpm\quan-1-tourism-no-docker`. Không Docker.

## Cập nhật dự án đang chạy

1. Dừng terminal backend, worker và Expo bằng Ctrl+C.
2. Giải nén ZIP ra chỗ tạm. Mở thư mục `quan-1-tourism-no-docker` bên trong, chép **nội dung** vào thư mục dự án đang dùng và đồng ý thay thế các file mã nguồn trùng tên.
3. Giữ `backend\.env`, `mobile\.env`, `backend\.venv` và `mobile\node_modules` đang có. ZIP không chứa những file cấu hình riêng và thư mục thư viện này. Không xóa database và không cần chạy lại seed cho bản cập nhật.
4. Mở PowerShell trong thư mục dự án:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run db:migrate
npm.cmd run db:accounts
npm.cmd run check
npm.cmd run backend
```

`db:migrate` bổ sung cột ngôn ngữ còn thiếu. `db:accounts` tạo ba bảng `users`, `auth_sessions`, `favorites` nếu chưa tồn tại. Cả hai chạy lại được, không thay thế thuyết minh đã nhập và không thêm dữ liệu demo.

5. Terminal thứ hai:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker\mobile
npx.cmd expo start --clear
```

Quét QR bằng Expo Go. Không có dependency mới; nếu chưa cài thư viện thì chạy `npm.cmd run install:backend` và `npm.cmd run install:apps` từ thư mục gốc trước.

Nếu migration báo database chưa khởi tạo, kiểm tra `DATABASE_URL` trong `backend\.env` trước. Chỉ với database mới/trống, chạy `npm.cmd run db:init` để tạo bảng và dữ liệu mẫu. Đừng tạo nhầm database thứ hai khi dữ liệu đã có ở database khác.

## Tài khoản người dùng

Cài đặt → Tài khoản → Đăng nhập / Đăng ký → Tạo tài khoản.
- Họ tên, email, mật khẩu tối thiểu 8 ký tự, xác nhận mật khẩu.
- Đăng ký thành công sẽ đăng nhập ngay.
- Phiên user hết hạn sau 30 ngày, lưu trong SecureStore trên điện thoại và xác minh với server khi mở app.
- Chạm trái tim để thêm/bỏ yêu thích. Danh sách lưu PostgreSQL theo user; cùng tài khoản trên điện thoại khác dùng cùng danh sách. Kéo xuống tab Đã lưu để tải thay đổi từ thiết bị khác.
- Khách chưa đăng nhập vẫn xem và nghe thuyết minh; bấm yêu thích sẽ mở đăng nhập.
- Đăng xuất xóa phiên trên server và trên thiết bị, đồng thời xóa danh sách yêu thích khỏi màn hình. Dữ liệu yêu thích vẫn thuộc user trong database.
- Yêu thích cũ chỉ lưu chung trên thiết bị không tự gán cho user nào. Bạn chọn lưu lại sau khi đăng nhập.
- Đăng nhập, xác minh phiên, đồng bộ yêu thích và đăng xuất cần kết nối backend. Nếu mất mạng, chức năng nghe văn bản đã tải ngoại tuyến vẫn dùng được; không tự xếp hàng các thay đổi yêu thích.

## Tài khoản admin

Ngay **màn hình Đăng nhập người dùng**, có nút **Đăng nhập dành cho admin**.
- Email mặc định: `admin@quan1.local`, hoặc `ADMIN_EMAIL` trong `backend\.env`.
- Mật khẩu: `ADMIN_PASSWORD` đã dùng khi khởi tạo admin.
- User không truy cập được API admin dù tự gửi trường role=admin khi đăng ký.
- Không có đăng ký admin công khai. Admin hiện có được giữ nguyên.
- Đăng nhập admin thành công mở trang quản trị. Nút Quay lại ứng dụng giữ phiên; nút Đăng xuất thu hồi phiên. Trong Cài đặt → Tài khoản có nút vào lại quản trị.
- Phiên admin hết hạn sau 8 giờ. Các token JWT của bản cũ không còn hợp lệ: đăng nhập lại một lần sau khi cập nhật.
- Đổi ADMIN_PASSWORD rồi chạy `npm.cmd run admin:reset` sẽ đổi mật khẩu và thu hồi các phiên admin đó.
- Mỗi thiết bị đang dùng một vai trò ở một thời điểm. Đăng xuất user trước khi đăng nhập admin và ngược lại.

## Địa chỉ backend tự điền

App phải biết địa chỉ backend **trước khi** gửi đăng nhập; không thể tìm server chỉ từ email/mật khẩu.

Thứ tự khi mở app:
1. Địa chỉ đi kèm phiên đã lưu trên thiết bị.
2. Địa chỉ bạn đã lưu trong Cài đặt.
3. `EXPO_PUBLIC_API_URL` trong `mobile\.env`.
4. Nếu chưa có cấu hình, lấy IP LAN máy đang chạy Expo và ghép cổng 8000. Chỉ dùng khi backend cùng máy với Expo; không suy đoán host tunnel công khai.

Sau khi đăng nhập, API URL được điền sẵn và khóa chỉnh sửa để tránh gửi phiên sang máy chủ khác. Đăng xuất trước khi đổi server. Không đồng bộ một địa chỉ LAN của máy A qua tài khoản sang mạng B.

Nếu IP Wi-Fi thay đổi hoặc cấu hình đã lưu không đúng, sửa kết nối trong Cài đặt khi chưa đăng nhập. Cấu hình đã lưu được ưu tiên nên sửa `.env` không tự ghi đè kết nối cũ. Điện thoại và máy tính cần cùng LAN và cổng backend phải truy cập được. Expo tunnel chỉ chuyển tiếp Expo, không tự chuyển tiếp backend.

Để bật suy luận LAN cho lần cài mới, để `EXPO_PUBLIC_API_URL=` trống. Với bản build độc lập không có Metro, cấu hình URL backend cố định trước khi build hoặc nhập trong Cài đặt.

## Bản đồ và Quận 1

- Bật GPS ở tab Bản đồ.
- Điểm tham chiếu của khu du lịch Quận 1: 10.777, 106.700.
- Khi khoảng cách tới điểm này **trừ sai số GPS lớn hơn 5 km**, hiện “Bạn đang ở quá xa Quận 1”, khoảng cách và nút Xem Quận 1.
- Chỉ dùng mẫu GPS không quá 30 giây, sai số không quá 100 m. Mẫu chưa đủ tốt hiển thị hướng dẫn chờ GPS, không kết luận người dùng ở quá xa.
- Mốc 5 km là vùng cảnh báo gần trung tâm lịch sử, không phải polygon ranh giới hành chính. Vị trí được tính trên điện thoại, không gửi GPS lên backend.
- Vẫn cho xem địa điểm và nghe thủ công. Tự động đọc tiếp tục dùng bán kính riêng từng POI.
- Đổi ngưỡng tại `mobile/src/district.ts`: `DISTRICT_FAR_METERS`.

## Kiểm tra trên điện thoại của bạn

1. Đăng ký user A, lưu hai POI. Đăng xuất rồi đăng ký B: danh sách B trống.
2. Đăng nhập lại A: hai POI còn nguyên. Thử tài khoản A trên máy khác và kéo tải lại.
3. Từ màn hình login user chuyển sang admin, đăng nhập bằng tài khoản đã có; đăng xuất admin và thử đăng nhập user.
4. Đóng/mở app khi có mạng: phiên và backend được nhớ.
5. GPS chính xác ở gần trung tâm không báo xa; ở cách trung tâm hơn 5 km có banner. Từ chối GPS thì hiện hướng dẫn.
6. Kiểm tra thuyết minh năm ngôn ngữ bạn đã nhập vẫn còn.

Bản này chưa bổ sung xác minh email, quên mật khẩu, Google login hay lịch sử nghe gắn user. Analytics hiện có vẫn theo cơ chế consent cũ. Backend giới hạn thử đăng nhập theo IP trong một tiến trình; triển khai công khai cần cấu hình HTTPS và giới hạn dùng chung nếu chạy nhiều tiến trình.
