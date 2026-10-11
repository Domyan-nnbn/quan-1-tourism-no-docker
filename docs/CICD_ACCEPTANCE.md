# Nghiệm thu CI/CD không Docker

CI/CD đã được viết trong repository. Chưa có URL GitHub/server hoặc quyền truy cập nên chưa thể chạy workflow/triển khai thật trong phiên cập nhật. Không dùng kết quả unit test để tuyên bố production đã hoạt động.

## 1. Chuẩn bị repository

Đưa toàn bộ source, lockfiles, scripts và `.github/workflows` lên GitHub; không đưa `.env`, `.venv`, node_modules, dump DB hoặc khóa SSH. CI chạy trên push và pull request, giới hạn mỗi job 20 phút.

Hai job bắt buộc: `mobile`, `backend` trong workflow `Quality checks`. Sau lần chạy đầu, vào Settings → Rules/Branches, bảo vệ nhánh chính: yêu cầu PR, review và cả hai status checks đạt trước khi merge. Đây là cấu hình trên GitHub, file YAML không tự bật bảo vệ nhánh.

CI mobile: npm ci → TypeScript → JUnit tests → Expo dependency check → Android/iOS export. CI backend: PostgreSQL native → requirements.lock → pytest (bao gồm native concurrency) → xuất OpenAPI. Artifact giữ 30 ngày: `mobile-checks-<sha>`, `backend-checks-<sha>`. Khi test thất bại vẫn cố tải báo cáo có sẵn. Nếu setup thất bại trước test, xem log job vì chưa có JUnit.

## 2. Chuẩn bị staging/production

Theo `OPERATIONS.md`: Ubuntu, Python, PostgreSQL, systemd, user deploy, shared/backend.env, reverse proxy HTTPS. Mỗi môi trường có database riêng. Đặt WORKER_REQUIRED=true để smoke kiểm tra cả worker. Không dùng database demo/test cho production.

Trong GitHub Environments tạo `staging` và `production`. Mỗi môi trường cấu hình:

| Loại | Tên |
| --- | --- |
| Secret | DEPLOY_HOST |
| Secret | DEPLOY_USER |
| Secret | DEPLOY_SSH_KEY |
| Secret | DEPLOY_KNOWN_HOSTS |
| Variable | PUBLIC_API_URL |

Xác minh SSH host key bằng kênh tin cậy trước khi lưu KNOWN_HOSTS. Với production, cấu hình required reviewer và giới hạn nhánh phát hành nếu gói GitHub hỗ trợ. Workflow không tự cấp người duyệt.

## 3. Chạy deploy

Actions → Release backend without Docker → Run workflow → chọn staging / deploy và commit cần kiểm tra. Workflow chạy lại CI trước release. Nó tạo archive có checksum SHA-256, backup DB, migrate, restart API/worker rồi kiểm tra local + HTTPS public. Khi thành công ghi `last-success.json` trên server. Workflow còn lưu `deployment-check-<environment>-<run_id>` chứa report kiểm tra public; nếu deploy thất bại trước bước đó thì xem log vì chưa có report. CD là kích hoạt thủ công với quy trình tự động, chưa có tự promotion từ staging sang production.

Sau staging đạt, chạy production từ đúng commit SHA đã kiểm tra. Theo dõi log và artifacts; kiểm tra thủ công đăng nhập, thao tác admin/user bằng tài khoản thử riêng. Bundle Expo export không phải APK/IPA hay EAS Update.

## 4. Lưu minh chứng read-only từ Windows

Công cụ sau chỉ GET readiness/catalog, không tạo hoặc xóa dữ liệu. API và worker phải đang chạy, WORKER_REQUIRED=true. Dùng URL HTTPS thật:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
.\backend\.venv\Scripts\python.exe deploy\verify.py --url https://API_THAT_CUA_BAN --report verification-staging.json
```

Exit code 0 = đạt, 1 = không đạt. Report chỉ có thời gian, origin, passed và loại lỗi. Không có mật khẩu/token. Khi dùng local có thể thay URL bằng http://localhost:8000. Health đáp ứng được không chứng minh mọi nghiệp vụ đã đúng; cần kiểm thử hành trình người dùng.

## 5. Diễn tập rollback

Trên staging đã có ít nhất hai release, chạy workflow action=rollback, rollback_sha=SHA đầy đủ của release trước đã tồn tại trên host. Xác nhận readiness, login và nội dung. Rollback code chỉ cho phép khi schema hiện tại phù hợp với code đích; không tự downgrade/xóa dữ liệu để ép tương thích.

Nếu migration không tương thích hoặc cần restore DB: dừng ghi, giữ backup, phục hồi vào database riêng, kiểm tra rồi mới chuyển cấu hình. Runbook chi tiết ở OPERATIONS.md. Không diễn tập phá dữ liệu trên production.

## 6. Hồ sơ nghiệm thu

| Minh chứng | Cần ghi |
| --- | --- |
| CI | URL workflow run, commit SHA, kết quả mobile/backend, JUnit và OpenAPI artifact |
| Service integration | Kết quả test_service_flow và các test native, loại PostgreSQL/phiên bản |
| Deploy staging | SHA, thời điểm, URL staging, kết quả smoke |
| Nghiệp vụ | Tài khoản thử, nhập bài → duyệt → public → lưu yêu thích; không ghi mật khẩu |
| Rollback | SHA cũ/mới, schema, readiness sau quay lại |
| Backup restore | Database thử riêng, thời gian phục hồi, đối chiếu dữ liệu |
| Điện thoại | Android/iOS, Wi-Fi/4G, GPS/khóa màn hình theo DEVICE_TEST.md |

Còn để production: kiểm thử tải, cảnh báo tập trung, dependency/security scanning và chính sách backup/retention. Không có một phần trăm hoàn thiện thay thế các minh chứng trên.
