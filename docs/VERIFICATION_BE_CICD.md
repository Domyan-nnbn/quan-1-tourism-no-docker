# Xác minh bổ sung BE services / CI/CD — 11/10/2026

Bổ sung trên bản 1.3, không thay schema, dependency mobile hay dữ liệu nghiệp vụ.

| Kiểm tra | Kết quả thực hiện |
| --- | --- |
| Backend pytest | 29 đạt, 5 native PostgreSQL test skip |
| Luồng tích hợp service | API tạo job → worker thật xử lý → nháp → biên tập đủ 5 bản → approve/publish → public → favorite/consent/logout → unpublish đạt; network Wikipedia được thay bằng nguồn cố định |
| Release tests | Smoke readiness/catalog; activation; rollback tương thích; chặn rollback schema sai; archive traversal/symlink; phục hồi API cũ tương thích sau validation thất bại |
| Mobile JUnit | 34 kiểm thử chạy đạt bằng đúng lệnh reporter mới của CI |
| OpenAPI export | Xuất thành công 26 paths; có đổi mật khẩu, không còn offline manifest |
| Workflow YAML | Parse được ci.yml và cd.yml; chưa phải bằng chứng runner GitHub đã chạy |
| Python mới | py_compile đạt cho release.py, verify.py, export_openapi.py |

Backend dùng PGlite PostgreSQL WASM qua TCP trong môi trường kiểm tra; các ca tranh chấp native vẫn phải chạy trên GitHub hoặc PostgreSQL thật với NATIVE_POSTGRES=1. Có một cảnh báo deprecation Starlette/httpx, không làm test thất bại. Không nâng dependency chỉ để ẩn cảnh báo này.

Chưa có deploy staging/production, restore DB thật, workflow GitHub run, load test hoặc điện thoại thật trong lần cập nhật này. Bản bổ sung không đổi code mobile; kết quả export Android/iOS trước đó ở VERIFICATION_STABILITY.md vẫn áp dụng cho source mobile hiện tại.

## Thay đổi được bàn giao

- Hợp đồng service, component/deployment diagram và sequence: BE_SERVICES_CONTRACTS.md.
- Runbook cấu hình repo/server, thu minh chứng CI/CD và rollback: CICD_ACCEPTANCE.md.
- CI lưu JUnit/OpenAPI theo commit, có timeout; CD lưu report kiểm tra public sau release.
- Công cụ deploy/verify.py chỉ đọc health/catalog, không sửa database.
- Sửa thông tin lỗi thời trong SCOPE.md.

## Cập nhật

Dừng API/worker trước khi chép đè source. Giữ backend/.env, mobile/.env và database. Chép cả .github khi đưa lên repo. Bản bổ sung này không thêm package hay migration; nếu đã cài bản 1.3 thành công thì không cần cài lại mobile. Nếu lần npm ci trước bị ngắt, hoàn tất npm.cmd run install:apps rồi npm.cmd run check. Backend cài theo lockfile và chạy db:migrate như hướng dẫn UPDATE_STABILITY_1_3.md.
