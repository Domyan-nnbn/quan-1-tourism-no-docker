# Đối chiếu QUAN_1_TOURISM.docx

Đây là bản pilot chạy Expo Go, chưa phải toàn bộ hệ thống production trong báo cáo.

## Các thay đổi thiết kế theo yêu cầu

- PWA → React Native + Expo SDK 57 + TypeScript.
- MongoDB → PostgreSQL, SQLAlchemy. React không kết nối trực tiếp database.
- Giữ FastAPI modular backend, tách API/auth/models/worker.
- Redis/RQ → hàng đợi bền vững trong PostgreSQL cho tác vụ nhập Wikipedia, dùng SKIP LOCKED và retry có backoff. Không tuyên bố đã dùng Redis.
- Neural TTS/audio storage → Expo Speech trên thiết bị cho pilot.
- Admin dashboard → màn hình quản trị ngay trong mobile.

| Use case | Mức triển khai trong mã nguồn |
|---|---|
| UC01 bản đồ/POI | Native map, marker, vòng bán kính, tìm kiếm, lọc, khoảng cách, chỉ đường ngoài app |
| UC02 GPS narration | Foreground, bán kính mặc định 30m, debounce 3s, cooldown 5 phút, fix ≤15 giây, accuracy ≤25m và ≤nửa radius, vùng sai số nằm trong radius, gần nhất trong vùng chồng nhau; không ngắt bài đang đọc; không gửi GPS lên server |
| UC03 ngôn ngữ | UI du khách Việt/Anh, kịch bản vi/en/zh/fr/ja. UI quản trị dùng tiếng Việt |
| Kết nối trực tuyến | Bản 1.3 bỏ UC04 tải offline và endpoint manifest. App tải nội dung từ API; dừng GPS/giọng đọc khi chuyển nền |
| UC05 consent | SecureStore token, kiểm tra consent phía server, thu hồi xóa sự kiện; không lưu GPS |
| UC06 quản trị POI | Tạo, sửa, lưu trữ, radius validation, phiên đăng nhập có thể thu hồi |
| UC07 nguồn Wikipedia | Chỉ nhận HTTPS vi/en Wikipedia, không redirect tùy ý |
| UC08 khởi tạo workflow | Tạo tác vụ nhập Wikipedia trả 202; idempotency key |
| UC09 duyệt/edit | Bản nháp version mới, duyệt đủ Việt/Anh/Trung/Pháp/Nhật; không đè published version |
| UC10 publish | Duyệt trước khi publish, unpublish, đổi phiên bản; dùng device TTS nên CHƯA có production audio-ready gate |
| UC11 theo dõi | Polling mỗi 10 giây khi mở màn hình admin, trạng thái và retry; CHƯA có SSE/audio task |
| UC12 analytics | Số lượt bắt đầu/kết thúc nghe và số POI published |
| UC13 sync Wikipedia | Worker lấy revision, parse đúng revision, trích các đoạn, metadata |
| UC14 AI draft | CHƯA tích hợp provider; không giả lập AI bằng việc cắt văn bản |
| UC15 dịch tự động | CHƯA tích hợp; quản trị viên nhập/duyệt đủ 5 ngôn ngữ |
| UC16 Neural TTS | CHƯA có file audio server; pilot dùng giọng TTS thiết bị |
| UC17 recovery | Retry tối đa 3 lần, backoff, thu hồi job PROCESSING khi lease 120 giây hết hạn; cần kiểm thử đa worker thật trước production |
| UC18 aggregate | SQL tổng hợp lúc đọc; chưa có read-model/scheduled aggregation |

## Chưa hoàn thành các gate production

- Chạy local không Docker/WSL; PostgreSQL cài trực tiếp.
- Chưa chạy trên điện thoại thật trong môi trường tạo mã; cần checklist DEVICE_TEST.md.
- Chưa có AI provider, translation provider, MP3/object storage, offline maps.
- Có migration phiên bản và checksum, kiểm tra schema; giữ nguyên dữ liệu khi nâng cấp đúng quy trình.
- Có mã CD/rollback, log và metrics trong tiến trình; chưa triển khai staging/production thật, load test, observability stack và security scan chuyên sâu.
- CI có sẵn nhưng chưa được chạy trên tài khoản GitHub của bạn.
- Rate limit login hiện ở bộ nhớ một API process; dùng shared limiter khi chạy nhiều instance.
- Có thu hồi phiên server-side và đổi mật khẩu; chưa có refresh-token rotation hoặc quên mật khẩu qua email.
- Không lưu tọa độ GPS nhưng server hạ tầng vẫn có thể có IP trong access logs; cần retention policy khi triển khai.
- 20 POI minh họa không phải bộ nội dung production đã được kiểm chứng. Vị trí pin/cổng vào và phạm vi địa lý cần khảo sát.

## Phát triển tiếp pipeline báo cáo

Cần chọn và cấu hình provider AI/Translation/TTS, bổ sung adapter + integration test; yêu cầu credential được quyết định riêng, không có khóa API được nhúng trong app. AI phải dừng ở bản nháp; Admin duyệt rồi mới dịch/TTS. Sau đó bổ sung Audio/Localization tables, audio-ready publish gate, object storage, checksum audio, Redis nếu cần scale và môi trường staging.

## Cập nhật 5 ngôn ngữ

UI khách giữ Việt/Anh. Kịch bản, API, analytics và Admin hỗ trợ vi/en/zh/fr/ja. Ngôn ngữ TTS độc lập UI, có kiểm tra voice. Approve phiên bản mới yêu cầu đủ 5 bản. Các bài đã publish cũ không bị gỡ; migration chỉ thêm cột rỗng. Có bộ bản dịch demo và lệnh nhập an toàn cho các bài demo chưa sửa. Không có dịch tự động runtime. Hướng dẫn ngôn ngữ: UPDATE_5_LANGUAGES.md; nâng cấp hiện tại: UPDATE_STABILITY_1_3.md.

## Hồ sơ BE và CI/CD

Xem BE_SERVICES_CONTRACTS.md để đối chiếu component, sequence và hợp đồng; CICD_ACCEPTANCE.md để triển khai và thu thập minh chứng thực tế.
