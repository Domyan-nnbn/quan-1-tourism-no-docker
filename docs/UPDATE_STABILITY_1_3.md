# Nâng cấp 1.3.0 — online và chỉ khi mở app

Bản này không dùng Docker. Giữ PostgreSQL và dữ liệu hiện có. Không cần tạo lại database, chạy seed hay nhập lại bản dịch.

## Cập nhật trên Windows

1. Dừng Expo/API/worker bằng Ctrl+C. Sao lưu database trong pgAdmin và giữ bản source cũ để quay lại nếu cần.
2. Giải nén ZIP vào thư mục tạm. Chép nội dung thư mục `quan-1-tourism-no-docker` sang `D:\cnpm\quan-1-tourism-no-docker`.
3. Giữ nguyên `backend/.env`, `mobile/.env` và database. ZIP không chứa `.env`, `node_modules`, `.venv`. Chép cả thư mục `.github` nếu dùng CI/CD.
4. Tại thư mục gốc, chạy:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run install:backend
npm.cmd run install:apps
npm.cmd run db:migrate
npm.cmd run check
```

Schema vẫn là `0002_worker_leases`; migration xác nhận checksum và cấu trúc thay vì tạo lại dữ liệu. Đổi mật khẩu chỉ thay hash/phiên đăng nhập, không cần bảng mới.

## Chạy bằng Wi-Fi khác hoặc 4G

Giữ bốn terminal mở nếu dùng API trên máy tính và Expo Go:

```powershell
# Terminal 1, tại thư mục gốc
npm.cmd run backend
# Terminal 2, tại thư mục gốc
npm.cmd run worker
# Terminal 3
cloudflared tunnel --url http://localhost:8000
# Terminal 4
cd D:\cnpm\quan-1-tourism-no-docker\mobile
npx.cmd expo start --tunnel --clear
```

`@expo/ngrok` đã có trong devDependencies của mobile để Expo tìm được tại dự án. Nếu vẫn lỗi tunnel, gửi log mới; tunnel còn phụ thuộc mạng và dịch vụ bên ngoài.

Lấy URL HTTPS **vừa được cloudflared in ra**, mở `<URL>/health/ready` trên điện thoại để kiểm tra rồi nhập URL gốc vào Cài đặt → Địa chỉ backend. Không thêm `/health/ready` vào ô API URL. Expo tunnel chỉ chuyển tải mã app; Cloudflare tunnel mới chuyển tải API. Đóng tunnel/máy tính ngủ sẽ ngắt API. URL quick tunnel cũ không được coi là cố định.

## Tự điền và cố định máy chủ

App ghi nhớ URL đã lưu hoặc URL của phiên hiện có. `EXPO_PUBLIC_API_URL` trong `mobile/.env` là mặc định cho thiết bị mới. Nếu dùng địa chỉ HTTPS ổn định đã triển khai, có thể đặt:

```dotenv
EXPO_PUBLIC_API_URL=https://api.ten-mien-cua-ban.vn
EXPO_PUBLIC_API_LOCKED=true
```

Đây là ví dụ, phải thay bằng server thật. Khởi động lại Expo với `--clear`. Khi khóa, ô URL không cho sửa và app dùng cấu hình cố định. Giữ `EXPO_PUBLIC_API_LOCKED=false` cho LAN/quick tunnel. Chưa triển khai server hay tên miền thay bạn; named tunnel/tên miền cố định cần cấu hình riêng theo OPERATIONS.md.

Nếu phiên cũ giữ URL tunnel đã chết: vào Cài đặt, chọn **Xóa phiên trên máy để đổi kết nối**, rồi nhập URL mới và đăng nhập lại. Thao tác này chỉ xóa phiên tại thiết bị; không thu hồi được phiên server đang mất kết nối.

## Hành vi mới

- Bỏ nút tải/xóa gói offline và `/api/v1/offline/manifest`. Bản tải cũ trên thiết bị được xóa một lần khi khởi động; tài khoản, lựa chọn giọng và URL được giữ.
- Không đăng ký task nền. Chuyển nền/khóa màn hình: gỡ watcher GPS, dừng giọng đọc và hủy HTTP. Mở lại: tải danh sách, xác minh phiên và lấy GPS mới nếu trước đó đã bật.
- Khi API lỗi: bỏ danh sách đang hiển thị, báo lỗi và nút thử lại. Kiểm tra kết nối/danh sách mỗi 30 giây chỉ khi mở app. Phát hiện mất mạng có thể mất một chu kỳ kiểm tra, không đảm bảo tức thì.
- HTTP hết hạn sau 12 giây; GET có thể thử lại một lần khi lỗi mạng/502/503/504. Không tự phát lại yêu cầu đăng nhập, xuất bản hay thay đổi dữ liệu.
- GPS tự đọc chỉ nhận fix đo trong 15 giây, sai số biết rõ ≤25m, ≤nửa radius và vùng sai số nằm trong radius. Giữ trong vùng 3 giây; chọn địa điểm gần nhất; cooldown 5 phút. Nhà cao tầng có thể khiến GPS không đủ chính xác: vẫn cho nghe thủ công khi API kết nối.
- Yêu thích theo user: bỏ phản hồi cũ, tránh nhấn liên tiếp và đồng bộ lại sau kết nối. Không lưu hàng đợi thay đổi yêu thích.
- User/admin có **Đổi mật khẩu**: user tối thiểu 8 ký tự, admin 12; xác minh mật khẩu hiện tại, giữ phiên đang dùng và thu hồi các phiên khác. Chưa có quên mật khẩu qua email.
- Consent theo từng máy chủ: khi tắt mà mất mạng, nhớ yêu cầu xóa thống kê và thử lại khi mở app/kết nối đúng máy chủ. Không gửi GPS.
- Xuất bản nội dung khóa POI trong transaction, tránh hai yêu cầu đồng thời để lại nhiều phiên bản PUBLISHED. Admin có ước lượng thời lượng bài; đây không phải đảm bảo giọng nào cũng đọc đúng 60 giây.

Dữ liệu địa điểm chỉ giữ trong bộ nhớ của phiên đang mở để hiển thị. Token, cấu hình và yêu cầu thu hồi consent vẫn lưu trên thiết bị để bảo mật/khôi phục kết nối; đây không phải gói nội dung offline. Worker nhập bài và backend là tiến trình server, vẫn cần chạy khi ứng dụng điện thoại chuyển nền.

Xác minh đã làm: VERIFICATION_STABILITY.md. Kiểm tra điện thoại: DEVICE_TEST.md.
