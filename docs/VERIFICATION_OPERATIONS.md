> Kết quả lịch sử bản 1.2. Kết quả hiện tại: [VERIFICATION_STABILITY.md](VERIFICATION_STABILITY.md).

# Xác minh bản backend 1.2.0 — 11/10/2026

| Hạng mục | Kết quả thực tế |
|---|---|
| Backend API, migration, queue recovery, readiness, observability và rollback logic | **21 passed** |
| Kiểm thử cần PostgreSQL native với nhiều connection/process | **4 skipped trong môi trường bàn giao**, được bật bằng `NATIVE_POSTGRES=1` trong CI |
| Mobile TypeScript | Passed (`tsc --noEmit`) |
| Mobile unit tests | **18 passed** |
| Expo export Android | Passed |
| Expo export iOS | Passed |
| Parse YAML CI/CD | Passed |
| Python compile app và deploy scripts | Passed |
| Chạy GitHub Actions trên repo thật | Chưa chạy; cần đưa source lên repo |
| SSH/systemd/CD trên host staging/production | Chưa chạy; cần cấu hình host, database, secrets và HTTPS |
| Expo Go trên điện thoại thật, GPS/bản đồ, 4G | Chưa kiểm thử lại trực tiếp trong lần cập nhật này |

Backend tại môi trường bàn giao được chạy với PGlite (PostgreSQL WASM qua TCP), không phải server PostgreSQL native nhiều kết nối. Không suy diễn kết quả này thành đã kiểm chứng concurrency thực tế.

Bốn bài chưa chạy local: worker đồng thời nhận job khác nhau; các request import cùng idempotency key; kill tiến trình worker thật rồi tiếp tục job; các request favorites cùng user đồng thời. CI cài PostgreSQL native trực tiếp và chạy cả bốn bài, không dùng Docker.

Các bài đã chạy xác nhận: migration lặp lại an toàn, phát hiện checksum bị thay đổi, tiếp nhận database trước phiên bản mà giữ nội dung, schema thiếu cột trả 503, worker heartbeat cũ trả 503 khi bắt buộc, lease hết hạn được thu hồi, kết quả worker cũ bị từ chối, lỗi mạng thử lại ba lần rồi FAILED, request log không chứa token/query. Test rollback dùng mock systemd/network để kiểm tra luồng đổi lại release và chặn schema không tương thích.

App dùng cùng AccountController trong hook thực tế và unit tests. Đã kiểm tra mất mạng giữ token, retry khôi phục phiên, 401 xóa phiên, response cũ không ghi đè tài khoản mới, đổi backend trong khi restore, logout thất bại do mất mạng và đồng bộ lại favorites sau response bị mất.

Có một cảnh báo deprecation từ Starlette TestClient dùng httpx; các bài test đã chạy vẫn pass. Chưa tự nâng cấp dependency để xử lý cảnh báo này vì không thuộc thay đổi nghiệp vụ.

Giới hạn vận hành: metrics HTTP là cửa sổ trong từng process, chưa có dashboard/cảnh báo; CD triển khai backend/worker, không phát hành mobile; rollback tự động chỉ khi schema của bản trước khớp database hiện tại. Xem OPERATIONS.md để cấu hình và diễn tập trên staging.
