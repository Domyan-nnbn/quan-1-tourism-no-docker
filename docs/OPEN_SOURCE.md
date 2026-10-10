# Nguồn mã nguồn mở và phạm vi sử dụng

Dự án được viết mới cho QUẬN 1 TOURISM, không phải bản sao nguyên một ứng dụng du lịch và chưa được đẩy lên tài khoản GitHub của bạn.

| Dự án | Vai trò | License theo repository |
|---|---|---|
| https://github.com/expo/expo | Runtime Expo, Location, Speech, SecureStore, Crypto | MIT |
| https://github.com/expo/examples | Tham khảo tổ chức ứng dụng Expo và ví dụ bản đồ | MIT |
| https://github.com/react-native-maps/react-native-maps | Thư viện bản đồ native thực sự được cài trong mobile | MIT |
| https://github.com/fastapi/full-stack-fastapi-template | Tham khảo kiến trúc FastAPI + PostgreSQL, Docker và auth | MIT |
| https://github.com/fastapi/fastapi | Web API backend | MIT |
| https://github.com/sqlalchemy/sqlalchemy | ORM và truy vấn tham số hóa | MIT |

Không sao chép nguyên khối source từ các template trên. Các dependency được cài qua npm/pip và giữ license đi kèm package. Expo `with-maps` hiện có thể dùng `expo-maps`; app này chọn `react-native-maps` vì mục tiêu Expo Go.

Nguồn chính thức đã tham khảo:
- https://docs.expo.dev/versions/latest/sdk/location/
- https://docs.expo.dev/versions/latest/sdk/map-view/
- https://docs.expo.dev/versions/latest/sdk/speech/
- https://expo.dev/expo-go

## Nội dung

20 kịch bản ngắn trong seed là nội dung minh họa được viết cho bản demo, không phải nội dung Wikipedia đã đồng bộ/kiểm duyệt. Không gán revision giả. Các URL Wikipedia trong seed chỉ là nguồn tham khảo dự kiến; cần kiểm tra khi import.

Worker nhập Wikipedia có lưu article ID, revision ID, link revision, thời điểm, hash, ngôn ngữ và nhãn CC BY-SA 4.0. Nội dung trích xuất/biên tập phải giữ attribution khi phân phối. Không áp dụng license phần mềm cho nội dung bên thứ ba.

Bản đồ do nhà cung cấp bản đồ native cung cấp; không tải hàng loạt tiles hoặc che attribution. Chính sách bản đồ không được thay thế bởi license MIT của thư viện.
