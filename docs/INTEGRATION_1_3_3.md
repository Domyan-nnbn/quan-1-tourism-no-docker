# QUẬN 1 TOURISM 1.3.3 — các thay đổi đã tích hợp

## Đã thay đổi trực tiếp trong mã nguồn

1. **Chống đếm trùng lượt nghe:** `mobile/App.tsx` tạo `X-Listen-ID` bằng `expo-crypto` cho mỗi lần phát. Backend lưu UUID ẩn danh vào `listen_sessions` bằng PostgreSQL `ON CONFLICT DO NOTHING` rồi tăng `pois.listen_count` **chỉ một lần trong cùng transaction**. API vẫn hỗ trợ ứng dụng cũ không truyền header (nhưng không thể chống đếm lại của ứng dụng cũ). Header sai UUID trả 422; POI chưa xuất bản trả 404.
2. **Migration giữ dữ liệu:** thêm `backend/app/migrations/0005_listen_sessions.sql`, model `ListenSession` và kiểm thử `backend/tests/test_listen_dedup.py`. **Không** sửa checksum migration 0001–0004, không xóa bảng cũ. `db:migrate` là bắt buộc trước khi khởi động API mới.
3. **Chất lượng kịch bản:** `mobile/src/narrationQuality.ts` và test mới ước tính thời lượng 5 ngôn ngữ. Dashboard đánh dấu thiếu/quá ngắn/quá dài đối với mục tiêu tham khảo 45–85 giây và báo địa điểm cần rà soát. Đây là **cảnh báo**, không chứng nhận chất lượng dịch hay kiểm duyệt lịch sử. TTS thực tế có thể khác đáng kể.
4. **Mobile:** trang chi tiết hiển thị ảnh POI (nếu có URL), giờ mở cửa dạng văn bản và thời lượng đọc tham khảo. Không lấy hình tùy ý từ Wikipedia để tránh sai bản quyền.
5. **Bảo mật khi chia sẻ mã nguồn:** gói ZIP xuất ra đã **loại bỏ** `backend/.env`, `mobile/.env`, `node_modules`, `.venv`, `.git`, cache, certificate/key cá nhân. Chạy lại `npm run setup` sẽ tạo thông tin đăng nhập mới cho bản sạch. Nếu file RAR cũ đã chia sẻ, hãy **đổi JWT_SECRET, mật khẩu PostgreSQL/ADMIN_PASSWORD đã lộ** (đổi ADMIN_PASSWORD rồi chạy `npm.cmd run admin:reset`; đổi JWT_SECRET sẽ vô hiệu các token JWT nếu được sử dụng).
6. **Công cụ quản trị:** `npm.cmd run doctor` kiểm tra phiên bản Node, `.env`, `.venv`, Expo cài đặt và `/health/ready` (không hiện mật khẩu). `npm.cmd run db:prune-listens` dọn UUID cũ hơn 45 ngày; không thay tổng lượt nghe.
7. **Phiên bản:** thống nhất FastAPI/root/mobile về `1.3.3`.

## Nâng cấp trên máy có PostgreSQL và dữ liệu cũ

Mở PowerShell tại `D:\cnpm\quan-1-tourism-no-docker`. **Sao lưu database trước.** Dừng các terminal API và Worker đang chạy. Giải nén/copy mã nguồn mới nhưng **giữ nguyên** `backend/.env` và `mobile/.env` cũ trên máy (gói ZIP mới không có hai file đó).

```powershell
# Chỉ làm nếu chưa có .env; setup không ghi đè .env đã tồn tại.
npm.cmd run setup
npm.cmd run install:backend
npm.cmd run install:apps
npm.cmd run db:migrate
# Mở ba terminal riêng:
npm.cmd run backend
npm.cmd run worker
npm.cmd start
```

Không chạy `db:init` để nâng cấp dữ liệu có sẵn. Sau khi backend chạy, ở terminal thứ tư có thể dùng `npm.cmd run doctor`. Khi phiên bản cũ vẫn chạy, **không tự ý chạy lẫn API cũ và schema mới**, hãy nâng cấp đồng bộ.

Lịch dọn thông tin idempotency khi backend không bị gián đoạn: trong Windows Task Scheduler đặt công việc `npm.cmd run db:prune-listens` hằng ngày. Dữ liệu `listen_sessions` chỉ lưu mã UUID ngẫu nhiên, POI ID và thời điểm tạo, không lưu GPS hoặc danh tính người dùng. Giới hạn 60 lần gọi `/listen` mỗi phút/IP hiện có vẫn là giới hạn trong bộ nhớ **mỗi tiến trình**; nó không chống mọi bot hay giả mạo yêu cầu.

## Phạm vi chưa tự động tích hợp

- AI biên soạn, dịch tự động, Neural TTS/MP3: chưa cấu hình API, chi phí hoặc giấy phép. Giữ `expo-speech` và quy trình duyệt 5 ngôn ngữ.
- PWA React riêng, vai trò editor/reviewer, quên mật khẩu qua email và hạ tầng production: cần đặc tả, tên miền, dịch vụ hoặc quyết định sản phẩm.
- Không thể xác minh Expo Go/GPS/TTS/Leaflet trên điện thoại thật hoặc chứng minh backup/deploy staging khi không có thiết bị, PostgreSQL và thông tin triển khai.
- Nội dung 20 POI chỉ là demo; cảnh báo thời lượng không tự sửa nội dung. Cần biên tập, fact-check và kiểm duyệt độc lập trước khi phát hành.

## Các kiểm thử

- `backend/tests/test_listen_dedup.py` kiểm tra idempotency và UUID không hợp lệ; yêu cầu PostgreSQL test (`DATABASE_URL` phải kết thúc `_test`).
- `mobile/src/narrationQuality.test.ts` kiểm tra 5 ngôn ngữ, thiếu và quá dài.
- `python -m pytest backend/tests/test_release.py` không cần database; toàn bộ backend test còn lại cần PostgreSQL.
- `npm.cmd run check` cần cài xong dependencies trong `mobile/node_modules`.

**Quan trọng:** Nếu `npm.cmd run db:migrate` gặp lỗi, không chạy lại `db:init` để khắc phục một cách mù quáng; đọc thông báo và kiểm tra backup/migration cũ trước.
