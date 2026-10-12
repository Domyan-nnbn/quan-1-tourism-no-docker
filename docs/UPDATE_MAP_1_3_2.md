# Bản đồ Expo Go — cập nhật 1.3.2

Thay bản đồ Google native bằng Leaflet 1.9.4 chạy trong react-native-webview 13.16.1 (phiên bản được Expo SDK của dự án liệt kê). Leaflet JS/CSS được đóng gói trong source, không tải thư viện từ CDN khi mở app. Chỉ nền bản đồ OpenStreetMap cần mạng.

## Có trong bản cập nhật

- Điểm địa danh màu xanh lá: chạm để mở chi tiết POI trong app.
- Vòng bán kính địa điểm; vị trí người dùng màu xanh dương và vòng sai số GPS.
- Nút GPS đưa bản đồ về vị trí hợp lệ đang có; nút Xem Quận 1 đưa về trung tâm khi ở xa.
- Kéo và phóng to/thu nhỏ; tải lại bản đồ và chuyển về danh sách.
- Báo khi nền bản đồ tải lỗi/chậm. Tên POI được chèn bằng text DOM, không thực thi HTML.
- GPS, geofence, giọng đọc và backend vẫn do app hiện có quản lý. WebView không xin quyền vị trí riêng và không nhận token tài khoản/backend.
- Khi app ra nền, WebView được tháo khỏi giao diện; khi trở lại, tạo lại bản đồ và cập nhật dữ liệu mới. Không thêm dịch vụ nền hoặc tải vùng bản đồ offline.
- Đã bỏ react-native-maps và yêu cầu khóa Google Maps khi build APK. Chỉ đường ngoài app vẫn mở Google Maps như trước.

## Cập nhật trên Windows

1. Dừng Expo bằng Ctrl+C. Giải nén ZIP và chép đè source trong thư mục dự án. Giữ `.env`, `.venv`, `.git` và database.
2. Bản này thay dependency mobile nên cần cài lại (khác bản 1.3.1):

```powershell
cd D:\cnpm\quan-1-tourism-no-docker
npm.cmd run install:apps
npm.cmd run check
```

3. Mở lại Expo:

```powershell
cd D:\cnpm\quan-1-tourism-no-docker\mobile
npx.cmd expo start --tunnel --clear
```

4. Quét QR bằng Expo Go. API/PostgreSQL và Cloudflare tunnel giữ cách chạy trước đó. Không chạy `db:init`, không cần migration mới.

Nếu `npm ci` báo EPERM, đóng Metro và các tiến trình đang giữ thư mục `mobile/node_modules` rồi cài lại. Không chép `node_modules` từ ZIP; ZIP không chứa thư viện đã cài.

## APK

`eas.json` tiếp tục tạo APK profile preview. Cần API HTTPS công khai và tài khoản Expo; không cần `GOOGLE_MAPS_ANDROID_API_KEY` nữa. Các mục khóa Google Maps trong hướng dẫn 1.3.1 chỉ áp dụng bản đồ native cũ và được thay thế bởi tài liệu này.

## Nguồn và giới hạn

- Tile URL HTTPS: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`.
- Hiển thị © OpenStreetMap contributors trên bản đồ; giữ mặc định cache HTTP của WebView, đặt User-Agent có tên Quan1Tourism. Không prefetch/bulk download/offline tiles.
- Dịch vụ tile cộng đồng không có SLA, dành cho lượt xem tương tác quy mô demo. Khi mở rộng lượng người dùng cần chọn nhà cung cấp phù hợp.
- Request nền bản đồ đi trực tiếp tới nhà cung cấp tile, không qua backend của app; IP và vùng bản đồ đang xem có thể được nhà cung cấp nhận. GPS chính xác chỉ dùng để vẽ dấu vị trí trong WebView; không đưa tọa độ chính xác vào URL tile.
- Không thể đảm bảo bản đồ hiển thị nếu điện thoại không có mạng hoặc dịch vụ tile bị chặn. Trạng thái lỗi cho phép thử lại và dùng danh sách.

Tài liệu: https://docs.expo.dev/versions/latest/sdk/webview/ ; https://leafletjs.com/reference-1.9.4.html ; https://operations.osmfoundation.org/policies/tiles/.

## Kiểm tra trên điện thoại của bạn

Mở tab bản đồ trên Wi-Fi và 4G; kiểm tra nền bản đồ, kéo/zoom, bấm POI, bật GPS rồi bấm nút GPS để về vị trí. Tắt GPS phải mất dấu người dùng. Đổi ngôn ngữ UI để kiểm tra nhãn địa điểm. Chuyển nền rồi trở lại. Tắt mạng để kiểm tra trạng thái lỗi và nút tải lại.
