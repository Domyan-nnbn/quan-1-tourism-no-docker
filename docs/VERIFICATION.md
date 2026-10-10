# Kết quả kiểm tra bản bàn giao

Ngày: 10/10/2026. Đây là kết quả thực hiện khi tạo bộ mã nguồn, không phải kết quả test điện thoại của người dùng.

| Kiểm tra | Kết quả |
|---|---|
| TypeScript `tsc --noEmit` | Đạt |
| Geofence unit tests | 5/5 đạt: khoảng cách, debounce/cooldown/re-entry, GPS accuracy, vùng chồng nhau, chặn phát lại |
| Expo SDK dependency check | Đã đồng bộ SDK 57; lần kiểm tra online sau khi sửa TypeScript báo up to date; lần cuối dùng bundled metadata offline vì proxy timeout |
| Metro export Android | Thành công, bundle Hermes được tạo |
| Metro export iOS | Thành công, bundle Hermes được tạo |
| Backend API tests | 5/5 đạt trên PGlite (PostgreSQL WASM) qua TCP + psycopg, không dùng SQLite |
| Khởi tạo seed hai lần | Thành công, vẫn đúng 20 POI demo có cả Việt/Anh, không nhân đôi |
| SQL schema | Xuất từ SQLAlchemy bằng PostgreSQL dialect |
| PostgreSQL 17 native / Docker Compose | Chưa chạy được trong môi trường này; CI đã cấu hình PostgreSQL 17 service để xác nhận sau khi push |
| Điện thoại Android/iPhone thật | Chưa kiểm tra, xem DEVICE_TEST.md |
| Wikipedia network thực tế | Chưa xác nhận end-to-end; test worker dùng nguồn giả lập có kiểm soát |
| AI / Neural TTS / offline maps | Chưa tích hợp, không có kết quả kiểm thử giả |

Backend tests xác nhận:
1. API admin yêu cầu auth; publish bị chặn trước review; sửa nháp không đè published; unpublish ẩn POI.
2. Không cho duyệt khi thiếu tiếng Anh; chặn source URL giả mạo/localhost.
3. Idempotency trả cùng job; worker hoàn tất nhưng chỉ tạo DRAFT.
4. Không có consent bị 403; event ID chống trùng; revoke xóa events và chặn thu thập tiếp.
5. Manifest chỉ chứa POI đã xuất bản và metadata offline đúng giới hạn.

PGlite không thay thế kiểm tra PostgreSQL native, đa worker hoặc tải đồng thời. Có cảnh báo deprecation từ Starlette TestClient về httpx; tests vẫn đạt. Không có tài khoản hoặc API key thực được nhúng trong ZIP.

## Biến thể không Docker

Đã bỏ Compose/Dockerfile và thêm npm scripts chạy Python venv trực tiếp. Đã kiểm tra cú pháp Node, tạo cấu hình và chạy lại setup không ghi đè. Chưa thực thi launcher trên Windows thật trong môi trường này. Kết quả API/mobile phía trên áp dụng cùng mã ứng dụng không đổi.

## Cập nhật ngôn ngữ — 10/10/2026

- TypeScript: đạt.
- App: 8/8 unit tests đạt, gồm ghép voice đúng ngôn ngữ và tránh đọc Trung bằng voice ngôn ngữ khác.
- Backend: 7/7 integration tests đạt trên PostgreSQL WASM/PGlite qua psycopg.
- Migration chạy lại được, giữ nguyên ID và kịch bản Việt/Anh.
- Import demo chỉ điền ngôn ngữ thiếu, không ghi đè bản dịch hiện có hay kịch bản đã sửa.
- Khởi tạo 20 POI mới có đủ vi/en/zh/fr/ja; seed chạy hai lần không nhân đôi.
- Export Android/iOS: thành công.
- Chưa kiểm thử đủ 5 giọng trên điện thoại thật. Bản dịch là nội dung demo, cần người biết ngôn ngữ kiểm duyệt trước production.

## Cập nhật tài khoản — 10/10/2026

- TypeScript: đạt; 12/12 unit tests mobile đạt (geofence, ngôn ngữ, tự nhận API, cảnh báo xa và GPS không đủ chính xác).
- Backend: 13/13 integration tests đạt trên PGlite/PostgreSQL WASM qua psycopg.
- Kiểm tra đăng ký, chuẩn hóa email, email trùng, password hash Argon2; không nâng quyền qua payload đăng ký.
- Kiểm tra user không vào được admin; admin không dùng API yêu thích user; không xác thực bị từ chối.
- Hai tài khoản A/B có yêu thích riêng; thao tác lặp không nhân đôi; đăng nhập lại lấy đúng yêu thích; B không xóa được yêu thích A.
- Token logout không dùng lại được; token hết hạn bị từ chối; giới hạn thử đăng nhập hoạt động.
- Migration chạy lại được; bổ sung ba bảng vào database kiểu cũ và giữ nguyên thuyết minh.
- Metro export Android/iOS tạo bundle Hermes thành công.
- Chưa thao tác trên điện thoại thật hoặc PostgreSQL Windows của người dùng. Checklist trong UPDATE_ACCOUNTS.md.
