# QUẬN 1 TOURISM — 5 ngôn ngữ thuyết minh, không Docker

React Native + Expo Go SDK 57 · FastAPI · PostgreSQL cài trên Windows.

**Nếu bạn đã chạy bản cũ: đọc `docs/UPDATE_5_LANGUAGES.md` trước. Chạy `npm.cmd run db:migrate` để thêm cột; không cần tạo lại database.**

## 1. Chuẩn bị

- Node.js 22.13+ hoặc 24.
- Python **3.12 hoặc 3.13**. Script tự tìm bản đã cài, không bắt buộc riêng 3.12.
- PostgreSQL 16/17+ và pgAdmin; dịch vụ PostgreSQL đang chạy.
- Expo Go phù hợp SDK 57 trên điện thoại.

Không cần Docker hoặc WSL. Giải nén vào thư mục bạn có quyền ghi, ví dụ `C:\Users\<ten-ban>\source\quan-1-tourism-no-docker`. Không chạy ngay trong ZIP hoặc trong system32/Program Files.

## 2. Tạo database

Mở pgAdmin → kết nối PostgreSQL local → chuột phải Databases → Create → Database → đặt tên **tourism** → Save.

Hoặc chạy trong Query Tool khi đang kết nối database `postgres`:

```sql
CREATE DATABASE tourism;
```

Ghi nhớ user/password PostgreSQL bạn đã đặt lúc cài. Tài khoản thường là `postgres`. Mật khẩu này khác mật khẩu đăng nhập quản trị ứng dụng.

## 3. Tạo cấu hình

Mở thư mục dự án trong VS Code → Terminal:

```powershell
npm run setup
```

Mở file **backend/.env**, thay `CHANGE_ME` bằng mật khẩu PostgreSQL:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/tourism
```

Giữ nguyên JWT_SECRET và ADMIN_PASSWORD do script sinh. Nếu user/port khác, sửa tương ứng. Mật khẩu có `@ : / # %` phải URL-encode trong URL, ví dụ `@` → `%40`, `#` → `%23`, `%` → `%25`.

**Không chia sẻ file .env.** Nếu chạy lại setup, cấu hình cũ được giữ nguyên.

## 4. Cài thư viện và khởi tạo dữ liệu

Tại thư mục gốc dự án:

```powershell
npm run install:backend
npm run install:apps
npm run db:init
```

Script tự tạo `backend/.venv`, dùng Python trong venv để cài packages. Không cần activate venv. Database được tạo bảng và nạp đúng 20 địa điểm minh họa. Chạy db:init lại không nhân đôi dữ liệu.

## 5. Mở 3 terminal

Cả ba terminal đều đứng ở **thư mục gốc dự án**.

**Terminal 1 — backend:**

```powershell
npm run backend
```

Kiểm tra trên máy tính: `http://localhost:8000/health/ready` phải có `status: ready`.

**Terminal 2 — worker nhập Wikipedia:**

```powershell
npm run worker
```

**Terminal 3 — ứng dụng Expo:**

```powershell
npm start
```

Quét QR bằng Expo Go. iPhone có thể dùng Camera để mở QR.

## 6. Kết nối điện thoại với backend

1. Điện thoại và máy tính dùng cùng Wi-Fi.
2. Chạy `ipconfig` trên Windows, lấy IPv4 của Wi-Fi, ví dụ `192.168.1.10`.
3. Trên điện thoại mở trình duyệt và thử `http://192.168.1.10:8000/health/ready`.
4. Trong ứng dụng → **Cài đặt → Địa chỉ backend** → nhập `http://192.168.1.10:8000` → **Lưu & kết nối**.

**Không nhập localhost trên điện thoại**: localhost là chính điện thoại. Chỉ backend trên PC dùng localhost để truy cập PostgreSQL.

Nếu cần sửa mặc định, chỉnh `mobile/.env`, sau đó chạy lại Expo. `npm run setup -- 192.168.1.10` chỉ đặt IP lúc tạo file lần đầu; nếu file đã có, sửa trực tiếp.

Nếu health trên điện thoại không mở được: kiểm tra backend, mạng Wi-Fi guest/client isolation và cho phép Python trên mạng Private trong Windows Firewall. Không cần mở PostgreSQL port ra điện thoại. Expo tunnel không tự tunnel API backend.

## 7. Đăng nhập quản trị

Cài đặt → Quản trị nội dung:
- Email: `admin@quan1.local`.
- Password: giá trị **ADMIN_PASSWORD** trong `backend/.env`.

Đổi giá trị ADMIN_PASSWORD sau khi đã seed thì chạy `npm run admin:reset` để cập nhật hash tài khoản. Token cũ có thể còn hiệu lực tới 8 giờ.

Luồng quản trị:
1. Tạo/sửa POI và tọa độ/bán kính, lưu.
2. Nhập URL Wikipedia vi/en, lưu, bấm nhập bài.
3. Worker tạo bản trích xuất có revision; nạp nháp vào trình soạn thảo.
4. Biên tập đủ Việt, Anh, Trung, Pháp và Nhật, lưu phiên bản mới.
5. Kiểm tra cả năm ngôn ngữ → Duyệt → Xuất bản.
6. Về giao diện khách, kéo xuống tải lại.

API Swagger: `http://localhost:8000/docs`. Bảng SQL: `docs/schema.sql`.

## Chức năng và giới hạn

- Giao diện tối giản chỉ Việt/Anh; thuyết minh độc lập Việt/Anh/Trung/Pháp/Nhật; bản đồ, tìm kiếm, bộ lọc, yêu thích.
- GPS foreground, tự chọn POI gần nhất, debounce 3s và cooldown 5 phút.
- Thuyết minh bằng giọng có trên thiết bị, có dừng và đổi tốc độ.
- Tải văn bản/tọa độ offline. Giọng offline phụ thuộc voice đã cài. Bản đồ vẫn cần mạng.
- Admin CRUD, phiên bản nội dung, duyệt/publish, worker Wikipedia, analytics có consent.

Đây là **pilot**, chưa có AI tự biên soạn/dịch, Neural TTS server, MP3 hay offline map. Không cần API key AI để chạy. 20 POI là nội dung demo, chưa phải dữ liệu đã kiểm duyệt production. Expo Go không cam kết geofence nền/khóa màn hình.

## Khắc phục lỗi

| Lỗi | Cách xử lý |
|---|---|
| No suitable Python runtime | Cài Python 3.12/3.13, mở lại VS Code, chạy `py -0p`; install:backend tự chọn bản phù hợp |
| Access denied / WinError 5 / EPERM | Giải nén sang thư mục người dùng có quyền ghi; đóng tiến trình giữ file; không sửa quyền toàn bộ ổ đĩa |
| password authentication failed | Sửa password/user PostgreSQL trong backend/.env, không dùng ADMIN_PASSWORD thay password DB |
| database tourism does not exist | Tạo database tourism trong pgAdmin trước db:init |
| Connection refused | Kiểm tra dịch vụ PostgreSQL Windows đang chạy và đúng port; API chỉ chạy sau db:init |
| QR mở app nhưng API lỗi | Thử health bằng trình duyệt điện thoại, kiểm tra LAN IP/firewall |
| SDK incompatible | Expo Go phải hỗ trợ SDK 57; không nâng riêng React Native tùy ý |
| iPhone không có tiếng | Tắt silent mode, tăng media volume, kiểm tra voice Việt/Anh |
| GPS không tự đọc | Cấp quyền, bật tự động, mở app, vào đúng radius; GPS accuracy phải ≤50m |
| Job đứng PENDING | Mở terminal worker bằng `npm run worker` |
| Job FAILED | Kiểm tra URL Wikipedia/mạng, thử lại hoặc nhập thủ công |
| Admin 401 | Đăng xuất/đăng nhập lại |

Dừng tiến trình bằng Ctrl+C trong từng terminal. Dữ liệu PostgreSQL vẫn được giữ.

## Kiểm thử và tài liệu

```powershell
npm run check
cd mobile
npx expo install --check
npx expo export --platform android --platform ios
```

Backend tests cần database riêng kết thúc `_test` vì sẽ xóa bảng trong database đó:

```powershell
cd backend
$env:DATABASE_URL="postgresql+psycopg://postgres:MAT_KHAU_DB@localhost:5432/tourism_test"
.\.venv\Scripts\python.exe -m pytest -q
```

- `docs/VERIFICATION.md`: kết quả đã kiểm tra và phần chưa kiểm tra.
- `docs/DEVICE_TEST.md`: checklist điện thoại thật.
- `docs/SCOPE.md`: đối chiếu báo cáo.
- `docs/OPEN_SOURCE.md`: repository và giấy phép tham khảo.

CI đi kèm dùng PostgreSQL service do GitHub Actions quản lý, không yêu cầu bạn cài Docker trên máy. Chưa push source lên GitHub của bạn.
