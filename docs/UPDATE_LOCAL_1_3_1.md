> **Lưu ý bản 1.3.2:** hướng dẫn khóa Google Maps/native ở dưới đã được thay thế bằng [UPDATE_MAP_1_3_2.md](UPDATE_MAP_1_3_2.md); bản mới dùng WebView, cần cài lại dependency mobile.

# Cập nhật trong mã nguồn 1.3.1

## Thay đổi

- Bỏ phần ước tính số giây của 5 kịch bản ở admin; không hiển thị cam kết thuyết minh “1 phút”. Không sửa văn bản lịch sử đã lưu trong database.
- GPS hiển thị: đang tắt, đang bật, đang tìm vị trí, thiếu quyền, dịch vụ vị trí tắt, vị trí cũ, thiếu chính xác hoặc đã có vị trí hợp lệ. Thiếu quyền có nút mở cài đặt ứng dụng.
- Khoảng cách và sắp xếp gần nhất chỉ dùng vị trí còn mới, đạt kiểm tra độ chính xác. Khi không đạt, hiện danh mục và sắp theo tên.
- Bản đồ có thông báo tải, nhắc khi chưa báo tải xong sau 15 giây, nút tải lại và chuyển sang danh sách. Callback tải xong không đảm bảo mọi ô bản đồ luôn có mạng; nút tải lại luôn có sẵn. Không cam kết sửa được lỗi khóa Google Maps hoặc lỗi dịch vụ bản đồ từ phía nhà cung cấp.
- Bỏ thông báo mất kết nối bị lặp ở danh sách. Chặn các yêu cầu tải catalog chồng nhau. Chuyển bài nghe dừng bài cũ trước khi kiểm tra bài mới.
- Đưa ô API URL vào cài đặt kết nối nâng cao; bản khóa API không hiển thị ô chỉnh sửa. Chưa có server cố định thì vẫn cấu hình như trước.
- Admin hiển thị tên trạng thái tác vụ dễ hiểu, có nút làm mới và hướng dẫn mở bản nháp khi nhập hoàn tất.
- Thêm cấu hình APK nội bộ / AAB phát hành và Google Maps Android qua biến môi trường.
- Nội dung thông báo giới hạn đăng nhập/yêu cầu không còn ghi “một phút”; thời gian giới hạn thực tế không đổi.

## Cập nhật máy Windows đang có dữ liệu

1. Dừng Expo, API và worker bằng Ctrl+C.
2. Sao lưu thư mục source hiện tại nếu có thay đổi riêng chưa commit.
3. Giải nén ZIP sang thư mục tạm. Chép nội dung thư mục `quan-1-tourism-no-docker` vào thư mục dự án hiện tại; chọn thay thế file source khi hỏi.
4. Giữ nguyên `backend/.env`, `mobile/.env`, `.venv`, `node_modules`, thư mục `.git` và PostgreSQL hiện có. ZIP không chứa những file/mục này. Không xóa hay tạo lại database.
5. Bản cập nhật này không thêm package hoặc schema migration. Nếu thư viện đã cài đủ, chỉ chạy:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run check
npm.cmd run backend
```

Mở terminal khác nếu cần nhập Wikipedia:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run worker
```

Mở terminal cho Expo:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker\mobile
npx.cmd expo start --tunnel --clear
```

API vẫn cần địa chỉ truy cập được từ điện thoại. Expo tunnel không thay cho tunnel/hosting backend.

## Build Android cài trực tiếp (chưa tạo APK trong lần cập nhật)

Đã có `mobile/eas.json`: `preview` tạo APK nội bộ với JavaScript đóng gói sẵn; `production` tạo AAB. Các bước sau cần tài khoản Expo và dịch vụ ngoài dự án nên người vận hành thực hiện sau:

1. Có API HTTPS công khai và database đang chạy.
2. Tạo hoặc liên kết dự án EAS bằng `npx.cmd eas-cli@latest init` trong thư mục `mobile`.
3. Cấu hình môi trường EAS `preview` (và `production` khi phát hành):
   - `EXPO_PUBLIC_API_URL`: origin HTTPS, ví dụ `https://api.example.com`, không thêm `/api/v1`.
   - `GOOGLE_MAPS_ANDROID_API_KEY`: khóa Maps SDK for Android. Hạn chế khóa theo API, package `vn.quan1.tourism` và SHA-1 chứng thư ký của đúng bản build. Khóa bản đồ được nhúng trong app nên cần hạn chế sử dụng ở Google Cloud.
   - Profile đã đặt `EXPO_PUBLIC_API_LOCKED=true`.
4. Các biến dùng để đọc app config cần khả dụng khi EAS CLI đánh giá cấu hình (dùng EAS visibility phù hợp như Sensitive, không dùng Secret cho giá trị cần đọc tại CLI). Không commit khóa vào Git.
5. Chạy:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker\mobile
npx.cmd eas-cli@latest build --platform android --profile preview
```

`app.config.js` chặn profile phát hành thiếu API HTTPS hoặc khóa Maps. `mobile/.easignore` loại trừ `.env` khỏi gói tải lên; cần thiết lập biến trong môi trường EAS. APK này không cần Metro trên laptop, nhưng vẫn cần backend online. Hướng dẫn chính thức: https://docs.expo.dev/build-reference/apk/ và https://docs.expo.dev/build/eas-json/.

## Phạm vi chưa thực hiện

Không tạo tài khoản cloud, triển khai server, chạy GitHub Actions, tạo chứng thư, build APK trên EAS hoặc gọi API AI. Worker vẫn nhập Wikipedia thành bản nháp vi/en; dịch tự động 5 ngôn ngữ chưa được tích hợp. Không thêm offline hoặc theo dõi vị trí nền.

## Kiểm tra trên điện thoại sau cập nhật

- Từ chối quyền GPS: thông báo rõ và mở được cài đặt; vẫn nghe thủ công được.
- Tắt dịch vụ vị trí: app báo dịch vụ tắt; bật lại rồi bấm GPS.
- Bật GPS: thấy trạng thái tìm vị trí trước khi có fix; fix cũ/thiếu chính xác không hiển thị khoảng cách như đang chính xác.
- Đang nghe A rồi chọn nghe B: A dừng; nếu B thiếu giọng/nội dung thì báo lỗi, không để A tiếp tục với nhãn B.
- Mất mạng: thấy một thông báo kết nối và nút thử lại; không tải catalog chồng nhau.
- Bản đồ trống hoặc tải chậm: thử tải lại; chuyển được sang danh sách.
- Chuyển nền/khóa màn hình: GPS, phát giọng và request dừng như trước.
- Admin không còn phần thời lượng; nhập Wikipedia vẫn tạo bản nháp và yêu cầu duyệt trước khi xuất bản.
