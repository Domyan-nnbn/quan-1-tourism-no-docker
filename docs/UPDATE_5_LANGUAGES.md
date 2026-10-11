# Cập nhật lên 5 ngôn ngữ thuyết minh

## Kết quả

- Giao diện khách: Tiếng Việt / English.
- Thuyết minh: Tiếng Việt / English / 中文 (Trung giản thể, giọng Mandarin) / Français / 日本語.
- Hai lựa chọn độc lập, giữ sau khi mở lại app.
- Admin có 5 ô kịch bản; approve phiên bản mới yêu cầu đủ 5 bản tối thiểu 20 ký tự mỗi bản.
- PostgreSQL lưu trực tiếp `vi`, `en`, `zh`, `fr`, `ja` trong content_versions.
- Điện thoại dùng giọng TTS tương ứng đã có trên máy. Nếu chưa có voice, app báo thiếu, không đọc bằng giọng ngôn ngữ khác.
- Bộ 20 POI có bản dịch demo soạn sẵn. Không có dịch tự động bằng API; không yêu cầu khóa dịch vụ.

## Với database bạn đang dùng

1. Ctrl+C để dừng backend, worker và Expo.
2. Giải nén đè mã nguồn bản cập nhật vào thư mục dự án hiện tại. Giữ nguyên `backend/.env`, `mobile/.env`, `.venv` và node_modules. ZIP không chứa các file cấu hình riêng này.
3. Từ thư mục dự án chạy:

```powershell
npm.cmd run db:migrate
```

Lệnh chỉ thêm các cột mới còn thiếu. Không xóa địa điểm, không đổi tài khoản/mật khẩu, không ghi đè Việt/Anh, không chạy lại seed.

4. Nếu muốn bổ sung Trung/Pháp/Nhật cho các bài mẫu chưa sửa:

```powershell
npm.cmd run db:demo-translations
```

Chỉ điền các bản dịch còn trống của kịch bản demo ban đầu, khi Việt/Anh vẫn khớp bản mẫu. Không ghi đè nội dung đã sửa hoặc các bản dịch đã có. Nếu bạn đã sửa bài mẫu, hãy nhập bản dịch cho đúng bài mới qua SQL hoặc Admin.

5. Chạy kiểm tra rồi mở lại backend, worker, Expo ở các terminal riêng:

```powershell
npm.cmd run check
npm.cmd run backend
```

```powershell
npm.cmd run worker
```

```powershell
npm.cmd start
```

Trong app kéo xuống tải lại. Chọn ngôn ngữ thuyết minh trong Cài đặt hoặc ngay trong chi tiết địa điểm. Bản 1.3 cần kết nối API; không còn gói tải offline.

## Cách làm hoàn toàn bằng pgAdmin

Trên database tourism:

1. Query Tool → mở và chạy `docs/migrate_5_languages.sql`.
2. Muốn nạp bản dịch cho demo chưa sửa: mở và chạy `docs/translations_demo.sql`.

Với bài riêng, có thể cập nhật trực tiếp bản đang phát:

```sql
UPDATE content_versions AS c
SET zh = '中文解说内容……',
    fr = 'Votre narration française…',
    ja = '日本語の解説文……'
FROM pois AS p
WHERE p.published_version = c.id
  AND p.name = 'Chợ Bến Thành'
RETURNING p.name, c.id;
```

Đây là sửa bản published trực tiếp; SQL không tạo lịch sử/duyệt tự động. Qua Admin thì phải lưu phiên bản mới rồi duyệt đủ 5 ngôn ngữ và xuất bản.

## Với database mới

Tạo tourism, chạy setup và cài thư viện như README; db:init sẽ tạo schema 5 ngôn ngữ và nạp 20 POI demo với đủ 5 kịch bản. Không cần chạy migration trên database mới đã tạo bằng phiên bản này.

## Voice trên điện thoại

Cài voice tiếng Việt, Anh, Trung, Pháp và Nhật trong phần Text-to-speech/Giọng nói của hệ điều hành nếu thiếu. Sau khi cài voice, tải lại app để kiểm tra danh sách giọng. Danh sách giọng và chất lượng TTS phụ thuộc máy; chưa kiểm tra cả 5 giọng trên thiết bị thật.
