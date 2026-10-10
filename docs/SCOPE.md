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
| UC02 GPS narration | Foreground, bán kính mặc định 30m, debounce 3s, cooldown 5 phút, GPS accuracy gate 50m, gần nhất trong vùng chồng nhau; không ngắt bài đang đọc; không gửi GPS lên server |
| UC03 ngôn ngữ | UI du khách + kịch bản Việt/Anh. UI quản trị dùng tiếng Việt |
| UC04 offline | Tải manifest văn bản + tọa độ + version, checksum chống lỗi dữ liệu cục bộ; không có offline tiles/MP3/PMTiles. Giọng offline tùy máy |
| UC05 consent | SecureStore token, kiểm tra consent phía server, thu hồi xóa sự kiện; không lưu GPS |
| UC06 quản trị POI | Tạo, sửa, lưu trữ, radius validation, đăng nhập JWT |
| UC07 nguồn Wikipedia | Chỉ nhận HTTPS vi/en Wikipedia, không redirect tùy ý |
| UC08 khởi tạo workflow | Tạo tác vụ nhập Wikipedia trả 202; idempotency key |
| UC09 duyệt/edit | Bản nháp version mới, duyệt cả Việt/Anh; không đè published version |
| UC10 publish | Duyệt trước khi publish, unpublish, đổi phiên bản; dùng device TTS nên CHƯA có production audio-ready gate |
| UC11 theo dõi | Polling mỗi 5 giây, trạng thái và retry; CHƯA có SSE/audio task |
| UC12 analytics | Số lượt bắt đầu/kết thúc nghe và số POI published |
| UC13 sync Wikipedia | Worker lấy revision, parse đúng revision, trích các đoạn, metadata |
| UC14 AI draft | CHƯA tích hợp provider; không giả lập AI bằng việc cắt văn bản |
| UC15 dịch tự động | CHƯA tích hợp; quản trị viên nhập/duyệt tiếng Anh |
| UC16 Neural TTS | CHƯA có file audio server; pilot dùng giọng TTS thiết bị |
| UC17 recovery | Retry tối đa 3 lần, backoff, thu hồi job PROCESSING quá 5 phút; cần kiểm thử đa worker thật trước production |
| UC18 aggregate | SQL tổng hợp lúc đọc; chưa có read-model/scheduled aggregation |

## Chưa hoàn thành các gate production

- Chạy local không Docker/WSL; PostgreSQL cài trực tiếp.
- Chưa chạy trên điện thoại thật trong môi trường tạo mã; cần checklist DEVICE_TEST.md.
- Chưa có AI provider, translation provider, MP3/object storage, offline maps.
- Chưa có migration tăng dần; seed dùng create_all cho database mới. Không tự thay đổi schema database cũ.
- Chưa triển khai staging/production, CD, rollback, load test, observability stack và security scan chuyên sâu.
- CI có sẵn nhưng chưa được chạy trên tài khoản GitHub của bạn.
- Rate limit login hiện ở bộ nhớ một API process; dùng shared limiter khi chạy nhiều instance.
- Token admin hết hạn sau 8 giờ, chưa có refresh/revocation server-side.
- Không lưu tọa độ GPS nhưng server hạ tầng vẫn có thể có IP trong access logs; cần retention policy khi triển khai.
- 20 POI minh họa không phải bộ nội dung production đã được kiểm chứng. Vị trí pin/cổng vào và phạm vi địa lý cần khảo sát.

## Phát triển tiếp pipeline báo cáo

Cần chọn và cấu hình provider AI/Translation/TTS, bổ sung adapter + integration test; yêu cầu credential được quyết định riêng, không có khóa API được nhúng trong app. AI phải dừng ở bản nháp; Admin duyệt rồi mới dịch/TTS. Sau đó bổ sung Audio/Localization tables, audio-ready publish gate, object storage, checksum audio, offline package, Redis nếu cần scale và môi trường staging.

## Cập nhật 5 ngôn ngữ

UI khách giữ Việt/Anh. Kịch bản, API, offline manifest, analytics và Admin hỗ trợ vi/en/zh/fr/ja. Ngôn ngữ TTS độc lập UI, có kiểm tra voice. Approve phiên bản mới yêu cầu đủ 5 bản. Các bài đã publish cũ không bị gỡ; migration chỉ thêm cột rỗng. Có bộ bản dịch demo và lệnh nhập an toàn cho các bài demo chưa sửa. Không có dịch tự động runtime. Hướng dẫn UPDATE_5_LANGUAGES.md là nguồn hướng dẫn nâng cấp mới nhất.
