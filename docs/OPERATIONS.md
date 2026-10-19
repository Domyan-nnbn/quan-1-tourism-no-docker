# Backend, migration và phát hành không Docker

Backend từ bản 1.2.0 triển khai sáu cải tiến: phân lớp backend, migration có phiên bản, readiness, kiểm thử lỗi, CD và theo dõi vận hành. Đây vẫn là **modular monolith**: các service gọi hàm Python trong cùng tiến trình API; API và worker giao tiếp qua bảng `jobs` của PostgreSQL. Không phát sinh các microservice HTTP riêng.

## 1. Cấu trúc và giao tiếp

| Thành phần | Vai trò |
|---|---|
| `app/main.py` | Khởi tạo FastAPI, CORS, middleware và gắn router |
| `app/routers/` | Đường dẫn HTTP, validation đầu vào, xác thực và phân quyền |
| `app/services/` | Đăng nhập, xuất bản nội dung, yêu thích, consent; quyết định transaction commit |
| `app/repositories/` | Truy vấn và ghi dữ liệu; repository queue quản lý transaction nhận/hoàn tất job |
| `app/security.py` | Hash mật khẩu, phiên đăng nhập và dependency kiểm tra quyền |
| `app/worker.py` | Lấy nguồn Wikipedia, gọi queue repository; không tự xuất bản nội dung |
| `app/migrate.py`, `app/migrations/` | SQL có phiên bản, checksum và khóa migration |
| `app/observability.py` | Request ID, log JSON và thống kê HTTP trong tiến trình |

Các endpoint và dữ liệu trả về trước đây được giữ lại. Việc tách lớp không yêu cầu app đổi API URL. Truy cập database diễn ra ở backend; điện thoại không kết nối trực tiếp PostgreSQL.

Luồng import: admin gửi yêu cầu có `Idempotency-Key` → service tạo một job → worker nhận job bằng row lock `FOR UPDATE SKIP LOCKED` → giải phóng transaction trước khi truy cập Wikipedia → lưu bản nháp và hoàn tất job trong cùng transaction → admin duyệt, sau đó mới xuất bản.

## 2. Cập nhật dự án đang chạy trên Windows

1. Dừng terminal API, worker và Expo bằng Ctrl+C; sao lưu database bằng pgAdmin Backup hoặc `pg_dump`.
2. Giải nén bản mới vào thư mục khác trước; giữ nguyên `backend/.env`, `mobile/.env` và database hiện có. Không chép đè `.env` thật bằng `.env.example`.
3. Chép các file mã nguồn mới vào dự án, gồm cả `.github`, `deploy`, `backend/app`, `backend/tests`, `scripts`, `mobile/src` và tài liệu. Với bản cũ trước tài khoản/ngôn ngữ, thay toàn bộ mã nguồn từ ZIP mới; chỉ giữ `.env` và dữ liệu.
4. Chạy từ thư mục gốc dự án:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run install:backend
npm.cmd run install:apps
npm.cmd run db:migrate
npm.cmd run check
```

Migration không thêm lại dữ liệu demo và không xóa tài khoản, phiên hay nội dung thuyết minh. Database mới: chạy `npm.cmd run db:init` sau khi cấu hình PostgreSQL để tạo admin và dữ liệu demo nếu `SEED_DEMO=true`. Database đã có dữ liệu không cần chạy lại seed.

Trong `backend/.env`, thêm:

```dotenv
WORKER_REQUIRED=true
WORKER_STALE_SECONDS=90
JOB_LEASE_SECONDS=120
```

Mở terminal riêng cho từng tiến trình:

```powershell
# Terminal 1 — thư mục gốc
npm.cmd run backend
```

```powershell
# Terminal 2 — thư mục gốc
npm.cmd run worker
```

```powershell
# Terminal 3 — thư mục mobile
npx.cmd expo start --tunnel --clear
```

Nếu backend vẫn trên máy cá nhân và dùng điện thoại qua 4G, giữ thêm terminal `cloudflared tunnel --url http://localhost:8000` và đặt API URL về HTTPS backend đang hoạt động. Tunnel Expo chỉ chuyển tiếp Metro; không thay thế tunnel backend. Bản cập nhật không tự biến IP `192.168.x.x` thành máy chủ công khai.

## 3. Migration có phiên bản

Lệnh chuẩn duy nhất là `npm.cmd run db:migrate` / `python -m app.migrate`. `db:accounts` là alias tương thích tới cùng runner. Những script vá bảng/cột cũ chỉ còn để tương thích và kiểm thử database cũ; không dùng chúng để quản lý schema mới.

- `0001_baseline.sql`: tạo database mới hoặc tiếp nhận schema cũ được hỗ trợ; bổ sung bảng tài khoản và cột năm ngôn ngữ nếu chưa có.
- `0002_worker_leases.sql`: thêm ownership/lease job và heartbeat worker.
- `0003_admin_dashboard.sql`: thêm ảnh/giờ mở cửa POI, khóa người dùng và cấu hình app.
- `schema_migrations`: version, checksum SHA-256 của SQL đã chuẩn hóa newline, thời điểm áp dụng.
- Khóa advisory transaction ngăn hai tiến trình migrate cùng lúc. Tất cả migration chưa chạy được áp dụng trong một transaction.
- Chạy lại không thực thi migration đã ghi. Nếu SQL đã áp dụng bị sửa, revision lạ hoặc schema thiếu/sai cột, runner dừng thay vì tự đoán cách sửa.
- Không chỉnh nội dung migration đã áp dụng. Thay đổi mới phải tạo migration tiếp theo và cập nhật ORM tương ứng.
- Không tự migrate hay seed lúc API nhận request. Seed khởi tạo gọi migration trước, nhưng vẫn là lệnh quản trị riêng.

Không có auto-down migration xóa dữ liệu. Với thay đổi phá tương thích, phải lên kế hoạch sao lưu/khôi phục và maintenance window. Kiểm tra schema tập trung bảng, tên/loại/nullability cột và migration checksum; chưa phải công cụ phát hiện mọi loại drift của index, trigger hoặc quyền PostgreSQL.

## 4. Readiness, worker bị ngắt và quan sát

`GET /health/live`: API còn trả lời HTTP, không phụ thuộc database.

`GET /health/ready`: trả 200 khi database truy cập được, đủ bảng/cột, migration khớp mã nguồn và có worker heartbeat mới nếu `WORKER_REQUIRED=true`; ngược lại trả 503.

```json
{
  "status": "ready",
  "database": "postgresql",
  "checks": {"database": true, "schema": true, "worker": true},
  "worker_required": true
}
```

Mặc định local `WORKER_REQUIRED=false`: worker không chạy vẫn cho API tra cứu/đăng nhập hoạt động, nhưng `checks.worker=false` phản ánh đúng trạng thái. Staging/production phải đặt `true`; CD từ chối readiness không yêu cầu worker. TTL mặc định 90 giây đủ cho hai request nguồn có timeout, heartbeat chỉ cập nhật giữa các lượt xử lý để phát hiện worker bị treo.

Mỗi lần nhận job sinh `lease_owner` riêng và hạn 120 giây. Worker chết để lại job PROCESSING; vòng xử lý tiếp theo thu hồi lease hết hạn và thử lại. Worker cũ trả kết quả muộn không được ghi vì ownership/lease không còn hợp lệ. Tối đa ba lần thử tự động, backoff 10/20 giây sau hai lần lỗi; admin có thể retry job FAILED. Nội dung hoàn tất luôn là DRAFT. Đây là xử lý có thể thử lại nhiều lần với cơ chế chặn ghi kết quả trùng, không hứa mạng bên ngoài được gọi đúng một lần.

`GET /api/v1/admin/operations` yêu cầu Bearer token admin:

- `jobs`: số job theo từng state trong PostgreSQL, gồm PENDING, RETRY_PENDING, PROCESSING, FAILED, COMPLETED nếu có.
- `http`: số request, tỷ lệ 4xx/5xx, thời gian trung bình trong 300 giây gần nhất, giới hạn 10.000 mẫu của **tiến trình API hiện tại**. Reset khi restart; chưa phải hệ thống metrics tổng hợp nhiều máy.

Mỗi request có `X-Request-ID`; giá trị từ client chỉ được chấp nhận với ký tự/chều dài hợp lệ. Log JSON ghi UTC timestamp, request ID, method, route template, status, duration_ms. Không ghi body, password, Bearer token, query string hoặc ID động trong URL. Worker ghi job ID, attempt, thời gian và loại lỗi. Có thể theo dõi trên server:

```bash
journalctl -u quan1-api@staging -u quan1-worker@staging -f
```

Chưa cài dashboard hay cảnh báo từ xa tự động. Muốn giữ lịch sử dài hạn/nhiều replica, chuyển JSON logs tới hệ thống thu thập log và bổ sung backend metrics tập trung; không cộng các tỷ lệ trung bình trực tiếp giữa các process.

## 5. CI và kiểm thử

`.github/workflows/ci.yml` chạy trên push, pull request và khi CD gọi lại. Không có service container: runner cài PostgreSQL trực tiếp bằng apt/systemd.

- Mobile: `npm ci`, typecheck, node tests, kiểm tra dependency Expo và export Android/iOS.
- Backend: cài `requirements.lock`, PostgreSQL riêng `tourism_test`, pytest. `NATIVE_POSTGRES=1` bật kiểm thử row locking đồng thời và tiến trình worker bị kill thật.
- Kiểm thử backend bảo vệ xuất bản năm ngôn ngữ, session, tài khoản, favorites, consent, migration checksum, schema drift, heartbeat cũ, network retry, lease recovery và log không lộ token.
- Kiểm thử app dùng cùng `AccountController` được hook React sử dụng: mất mạng, khôi phục token, 401, đổi backend trong khi request còn chạy, response favorites muộn của tài khoản cũ, logout cần mạng, refresh sau mất response.
- Test release mô phỏng smoke thất bại để xác nhận chuyển lại symlink/restart bản trước, và chặn rollback khi schema không tương thích.

Chạy backend tests với database **riêng, có tên kết thúc `_test`**; fixture xóa các bảng trong database này. Không dùng database đang chạy app.

```powershell
# Trong backend, đã kích hoạt .venv
$env:DATABASE_URL="postgresql+psycopg://tourism:MAT_KHAU@localhost:5432/tourism_test"
$env:NATIVE_POSTGRES="1"
python -m pytest -q
```

## 6. CD staging/production không Docker

CD triển khai backend API và worker; chưa phát hành app lên Play Store/App Store hay EAS Update. Expo export trong CI là kiểm tra build, không phải phát hành mobile.

`.github/workflows/cd.yml` chạy qua Actions → Release backend without Docker → Run workflow. Chọn môi trường và `deploy` hoặc `rollback`. CI phải qua trước khi job phát hành bắt đầu. Release dùng đầy đủ Git commit SHA, archive SHA-256, thư mục bất biến `/opt/quan1-<environment>/releases/<sha>`.

Quy trình: kiểm thử → tạo artifact → SSH → tạo venv release → backup PostgreSQL → dừng API/worker → migrate → đổi symlink `current` → restart systemd → kiểm tra local và HTTPS public cho readiness và danh sách địa điểm. Đây là triển khai có thời gian gián đoạn ngắn, không phải zero-downtime.

**Chuẩn bị server một lần** (Ubuntu 24.04, Python 3.12, venv, PostgreSQL/client `pg_dump` cùng major với server, reverse proxy HTTPS). Staging và production phải dùng database/tài khoản riêng. Có thể dùng hai host, hoặc cùng host với staging port 8001 và production port 8000.

Ví dụ chạy với quyền quản trị trên server; tài khoản SSH `deploy` cần được tạo trước theo chính sách của server:

```bash
sudo useradd --system --user-group --no-create-home quan1
sudo usermod -a -G quan1 deploy
sudo install -d -o deploy -g quan1 -m 0750 /opt/quan1-staging /opt/quan1-production
sudo install -d -o deploy -g quan1 -m 0750 /opt/quan1-staging/{releases,incoming,shared,backups}
sudo install -d -o deploy -g quan1 -m 0750 /opt/quan1-production/{releases,incoming,shared,backups}
sudo cp deploy/quan1-api@.service deploy/quan1-worker@.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Đăng nhập lại SSH sau khi đổi group. File `/opt/quan1-staging/shared/backend.env` do `deploy:quan1` sở hữu, mode `0640`. Production có file riêng. Dùng giá trị thật cho mật khẩu/secret:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/tourism_staging
JWT_SECRET=RANDOM_AT_LEAST_32_CHARACTERS
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=STRONG_PASSWORD_AT_LEAST_12_CHARACTERS
SEED_DEMO=false
WORKER_REQUIRED=true
WORKER_STALE_SECONDS=90
JOB_LEASE_SECONDS=120
API_PORT=8001
CORS_ORIGINS=https://YOUR_WEB_FRONTEND
```

Production đổi database và `API_PORT=8000`. Mật khẩu có ký tự đặc biệt phải URL-encode trong DATABASE_URL. Không commit `.env`, key SSH hoặc dump database lên Git.

Cấp sudo hẹp cho deploy qua `visudo` (điều chỉnh đúng đường dẫn `systemctl` trên máy):

```sudoers
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart quan1-api@staging quan1-worker@staging
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl stop quan1-api@staging quan1-worker@staging
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart quan1-api@production quan1-worker@production
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl stop quan1-api@production quan1-worker@production
```

Cấu hình reverse proxy HTTPS chuyển đến port tương ứng. API chỉ bind loopback trên server. Worker không cần port công khai. Firewall không công khai PostgreSQL. Enable hai unit cho từng môi trường sau lần deploy đầu thành công để tự chạy khi reboot. Database mới sau deploy không có admin vì CD không seed: chạy `python -m app.seed` bằng venv của release, `SEED_DEMO=false`, rồi đăng nhập thử bằng admin cấu hình.

Tạo GitHub Environments tên chính xác `staging`, `production`. Mỗi environment đặt:

| Loại | Tên | Giá trị |
|---|---|---|
| Secret | `DEPLOY_HOST` | Hostname/IP SSH |
| Secret | `DEPLOY_USER` | Tài khoản `deploy` |
| Secret | `DEPLOY_SSH_KEY` | Private key của deploy |
| Secret | `DEPLOY_KNOWN_HOSTS` | Host key được xác minh ngoài pipeline |
| Variable | `PUBLIC_API_URL` | HTTPS origin, không dấu `/` cuối, ví dụ `https://api.example.com` |

CD dùng `StrictHostKeyChecking=yes`; không tự tin host key lấy từ mạng trong lúc deploy. Giới hạn nhánh/tag được phép deploy production và bật reviewer nếu gói GitHub hỗ trợ. Chạy staging, kiểm tra đăng nhập/yêu thích/bản đồ/thuyết minh trên thiết bị, rồi deploy **cùng commit/tag** lên production. Pipeline chưa tự cưỡng chế rằng SHA đã qua kiểm thử thủ công ở staging.

Tham khảo cấu hình reusable workflow/environment secrets: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows

### Rollback

Run workflow → action `rollback` → nhập đủ SHA của release đã có trên server. Không tải lại code, không chạy down migration. Trước khi đổi release, runner kiểm tra schema hiện tại có khớp migration của release đích không.

Nếu smoke của release mới thất bại và release trước tương thích schema, script tự đổi lại `current`, restart và kiểm tra lại. Workflow vẫn báo lỗi để thể hiện release mới thất bại. Nếu schema đã nâng cấp và bản cũ không khớp, rollback bị chặn; không chạy code cũ tùy tiện trên DB mới.

Khôi phục khi schema không tương thích: dừng ghi/API/worker; chọn đúng dump trước migration ở `backups`; phục hồi vào **database mới** bằng pg_restore; kiểm tra dữ liệu; đổi DATABASE_URL tới database đã phục hồi và chọn release tương ứng; khởi động và smoke lại. Có thể mất các ghi phát sinh sau thời điểm backup nên phải quyết định có đối soát/chuyển dữ liệu trước. Không tự động ghi đè database production đang có dữ liệu.

Trước lần nâng cấp schema đầu tiên, nên triển khai bản tương thích lên staging và diễn tập backup/restore. Lần deploy đầu không có bản trước để tự rollback.

## 7. Phạm vi xác minh

Xem `docs/VERIFICATION_OPERATIONS.md` để biết kiểm thử nào đã chạy trong lần bàn giao này. Các file CD là cấu hình có thể triển khai sau khi chuẩn bị host/secrets; không có máy chủ production nào được triển khai hoặc thay đổi tự động trong phiên làm việc này.
