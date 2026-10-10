# Kiến trúc bản Expo pilot

```mermaid
flowchart TD
  A[React Native / Expo Go] -->|REST / Bearer session| B[FastAPI]
  A --> L[GPS foreground và geofence cục bộ]
  A --> T[Giọng TTS thiết bị]
  A --> O[Cache văn bản và tọa độ]
  B --> D[(PostgreSQL)]
  W[Wikipedia worker] --> D
  W --> S[Wikipedia API]
```

Luồng khách không gửi stream GPS lên backend. POI published được tải về, so khoảng cách cục bộ và phát voice trên thiết bị.

```mermaid
flowchart TD
  A[Admin nhập nguồn] --> B[Job PENDING]
  B --> C[Worker lấy revision và văn bản]
  C --> D[Nháp chờ biên tập Việt / Anh]
  D --> E[Admin duyệt]
  E --> F[Admin xuất bản]
  F --> G[Khách đọc / nghe]
  C -->|Lỗi| H[Retry tối đa 3 lần]
  H --> C
```

Bản nháp immutable theo hướng tạo bản mới cho mỗi lần lưu. POI chỉ giữ con trỏ published_version; sửa nháp không đổi nội dung công khai. Bản seed demo là ngoại lệ được đánh dấu rõ, không có human review thật.

## Bảng dữ liệu

| Bảng | Mục đích |
|---|---|
| users | Email unique, tên, Argon2 password hash |
| auth_sessions | Hash token, role, FK user/admin, hạn phiên |
| favorites | Khóa chính ghép user_id + poi_id |
| admins | Email unique, Argon2 password hash |
| pois | Tọa độ, radius, thông tin địa điểm, con trỏ bản xuất bản, archive |
| content_versions | Việt/Anh/Trung/Pháp/Nhật, trạng thái, metadata nguồn, người duyệt |
| jobs | Hàng đợi nhập Wikipedia, idempotency, attempts, lỗi, kết quả |
| consents | Hash token thiết bị, trạng thái và policy |
| analytics_events | Sự kiện bắt đầu/kết thúc, id chống trùng, không có GPS |
| audit_logs | Người thao tác, hành động và đối tượng |

## Mô hình bảo mật pilot

- Password hash Argon2, token phiên ngẫu nhiên; server chỉ lưu SHA256. Admin hết hạn 8 giờ, user 30 ngày; logout thu hồi phiên trong PostgreSQL.
- Token admin và consent lưu SecureStore, không AsyncStorage.
- Schema input giới hạn tọa độ, bán kính, độ dài và URL Wikipedia allowlist.
- Query SQL dùng SQLAlchemy bind parameters.
- Consent row khóa trong transaction khi thu hồi/nhận event, tránh nhận event sau thu hồi đã commit.
- API bind LAN để điện thoại truy cập; PostgreSQL cài trực tiếp trên Windows, kết nối local từ backend.
- Trước khi đưa lên internet: HTTPS, shared rate limit, secret management, migration, backups và production tests.
