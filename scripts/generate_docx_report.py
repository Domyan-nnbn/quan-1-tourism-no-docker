import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text_lines, title="LƯU Ý KỸ THUẬT:"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F2F4F7")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border thick navy
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24') # 3pt
    left.set(qn('w:color'), '1F4E79')
    tcBorders.append(left)
    for b in ['top', 'bottom', 'right']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"📌 {title} ")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    for idx, line in enumerate(text_lines):
        if idx > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for b in ['top', 'bottom', 'left', 'right']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'single')
        node.set(qn('w:sz'), '4')
        node.set(qn('w:color'), 'D0D5DD')
        tcBorders.append(node)
    tcPr.append(tcBorders)
    
    lines = code_str.strip().split('\n')
    for idx, line in enumerate(lines):
        p = cell.paragraphs[0] if idx == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = "Calibri"
            run.font.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    # Data rows
    for r_idx, row_data in enumerate(data):
        row = table.add_row()
        fill_color = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = cell_value
            set_cell_background(cell, fill_color)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
                
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

def build_document():
    doc = Document()
    
    # Page setup (A4, 1 inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    
    # Header & Footer
    footer = section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = f_p.add_run("Báo Cáo Kỹ Thuật Backend — Dự Án Quận 1 Tourism | Trang ")
    f_run.font.name = "Calibri"
    f_run.font.size = Pt(9)
    f_run.font.color.rgb = RGBColor(0x8C, 0x8C, 0x8C)
    
    # Title Section
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = title_p.add_run("ĐỒ ÁN PHÁT TRIỂN HỆ THỐNG PHẦN MỀM / BACKEND ENGINEERING\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    
    r_main = title_p.add_run("BÁO CÁO THUYẾT TRÌNH KỸ THUẬT BACKEND\nQUẬN 1 TOURISM")
    r_main.font.name = "Calibri"
    r_main.font.size = Pt(22)
    r_main.font.bold = True
    r_main.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_before = Pt(4)
    meta_p.paragraph_format.space_after = Pt(18)
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = meta_p.add_run("Chuyên đề: Thiết kế Services, Giao tiếp Liên Services & Pipeline CI/CD Không Docker\nPhiên bản: 1.3.2 | Tech Stack: FastAPI, PostgreSQL 16/17, Linux systemd, GitHub Actions")
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(10.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
        return h

    def add_p(text, bold_prefix=None, space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        return p

    # --- PHẦN 1 ---
    add_h1("PHẦN 1: TRIẾT LÝ KIẾN TRÚC BACKEND")
    add_p("Một lỗi thiết kế thường gặp trong các dự án công nghệ hiện nay là việc lạm dụng kiến trúc Microservices và Container hóa (Docker) quá sớm. Điều này phát sinh chi phí quản lý hạ tầng lớn, overhead tài nguyên (CPU/RAM ảo hóa), network latency giữa các container và phức tạp hóa tính toàn vẹn dữ liệu (phải dùng distributed transactions/Saga).")
    add_p("Để giải quyết triệt để bài toán của hệ thống Thuyết minh Du lịch Quận 1, đội ngũ phát triển quyết định áp dụng triết lý:", "Quyết định Kiến trúc: ")
    add_bullet(" Toàn bộ các module nghiệp vụ chạy trong cùng một tiến trình API hoặc Worker, phân chia ranh giới theo tầng (Layered Architecture: Routers -> Services -> Repositories -> Database). Giao tiếp nội vùng qua lời gọi hàm Python giúp độ trễ đạt mức microsecond và cho phép áp dụng ACID transactions trọn vẹn.", "1. Modular Monolith: ")
    add_bullet(" Triển khai trực tiếp trên hệ điều hành host (Windows môi trường Dev và Ubuntu 24.04 LTS môi trường Production) thông qua systemd. Không có lớp ảo hóa mạng của Docker, PostgreSQL chạy native tận dụng triệt để bộ nhớ đệm và I/O đĩa cứng của nhân Linux.", "2. Native Deployment (Không Docker): ")
    add_bullet(" Thay vì dựng thêm cụm Redis và worker riêng biệt (RQ/Celery), hệ thống dùng bảng PostgreSQL kết hợp cơ chế locking SKIP LOCKED làm hàng đợi bền vững.", "3. Giảm thiểu Dependency bên ngoài: ")

    # --- PHẦN 2 ---
    add_h1("PHẦN 2: PHÂN RÃ SERVICES & RANH GIỚI NGHIỆP VỤ")
    add_p("Backend được phân tách thành 6 domain services chuyên biệt, tuân thủ nguyên tắc Single Responsibility Principle (SRP):")
    
    table_services = doc.add_table(rows=1, cols=4)
    format_table(
        table_services,
        [Inches(1.4), Inches(1.5), Inches(2.2), Inches(1.4)],
        ["Domain Service", "Đầu vào (Input DTO)", "Trách nhiệm cốt lõi", "Quản lý dữ liệu"],
        [
            ["AccountsService", "RegisterInput, LoginInput, PasswordChange", "Xác thực người dùng, băm mật khẩu Argon2id, cấp phát phiên Bearer Token, thu hồi session.", "users, admins, auth_sessions"],
            ["CatalogService", "POIInput, Filters, Tọa độ Lat/Lng", "Quản lý vòng đời POI công khai, tính toán khoảng cách danh sách địa điểm, kiểm tra con trỏ published_version.", "pois (chỉ đọc bài đã duyệt)"],
            ["ContentService", "DraftInput, ImportWikipedia, version_id", "Quản lý bản nháp thuyết minh 5 thứ tiếng (vi, en, zh, fr, ja), kiểm duyệt và xuất bản bài viết.", "content_versions, audit_logs"],
            ["FavoritesService", "user_id, poi_id", "Thêm, xóa và truy vấn danh sách địa điểm yêu thích của từng tài khoản du khách.", "favorites (Composite PK: user_id + poi_id)"],
            ["OperationsService", "System requests", "Liveness, Readiness probe, thống kê số liệu jobs, HTTP request latency & worker heartbeat.", "schema_migrations, checks"],
            ["WikipediaWorker", "Job claim từ hàng đợi", "Xử lý tác vụ nền crawl Wikipedia, parse nội dung theo đúng revision id, tạo bản nháp.", "jobs, content_versions (DRAFT)"]
        ]
    )

    add_callout(doc, [
        "Toàn bộ truy cập cơ sở dữ liệu đều được đóng gói trong tầng Repositories (AccountRepo, CatalogRepo, ContentRepo, QueueRepo).",
        "API Routers chỉ làm nhiệm vụ parse HTTP, validate schema Pydantic và xác thực quyền; không bao giờ gọi trực tiếp SQL."
    ], "NGUYÊN TẮC THIẾT KẾ LAYERED:")

    # --- PHẦN 3 ---
    add_h1("PHẦN 3: CƠ CHẾ GIAO TIẾP LIÊN SERVICES")
    add_h2("3.1. Giao tiếp Đồng bộ (In-Process Service Calls)")
    add_p("Giữa các service trong cùng tiến trình API, hệ thống sử dụng cơ chế Dependency Injection của FastAPI để inject Database Session (`SessionDep`). Các service gọi hàm trực tiếp của nhau, chia sẻ chung một Database Transaction context:")
    add_bullet(" Khi xóa hoặc đổi mật khẩu tài khoản trong AccountsService, sự kiện thu hồi toàn bộ phiên đăng nhập cũ diễn ra ngay trong transaction.", "Atomic Session Revocation: ")
    add_bullet(" Client gửi kèm Bearer Token -> Middleware giải mã và hash SHA-256 -> Tra cứu trong bảng auth_sessions. Tốc độ xác thực cực nhanh mà không cần gọi network bên ngoài.", "Session Verification: ")

    add_h2("3.2. Giao tiếp Bất đồng bộ: Hàng đợi Bền vững qua PostgreSQL SKIP LOCKED")
    add_p("Tác vụ bóc tách dữ liệu từ Wikipedia là tác vụ nặng I/O mạng (2-10 giây). Hệ thống sử dụng mô hình Producer - Consumer bền vững trên PostgreSQL:")
    
    add_code_block(doc, """-- Câu lệnh SQL Claim Job độc quyền trong QueueRepository:
SELECT id, poi_id, source_url, attempts 
FROM jobs
WHERE state = 'PENDING' OR (state = 'PROCESSING' AND lease_expires_at < NOW())
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 1;""")

    add_p("Quy trình giao tiếp bất đồng bộ bao gồm 4 bước nghiêm ngặt:", "Luồng Xử Lý Khép Kín: ")
    add_bullet(" Admin gửi yêu cầu Import Wikipedia kèm Header Idempotency-Key (8-100 ký tự). ContentService chèn 1 bản ghi vào bảng jobs với trạng thái PENDING và commit ngay. API phản hồi HTTP 202 Accepted trong <15ms.", "Bước 1 (Producer): ")
    add_bullet(" Worker chạy vòng lặp claim job bằng câu lệnh SKIP LOCKED, sinh lease_owner (UUID ngẫu nhiên) và gán thời hạn lease 120s. Worker COMMIT ngay transaction claim này để giải phóng lock hàng cơ sở dữ liệu.", "Bước 2 (Claim & Lease): ")
    add_bullet(" Worker tiến hành gọi HTTPS sang Wikipedia API ngoài transaction, tránh việc giữ kết nối DB lâu gây nghẽn Connection Pool.", "Bước 3 (External Fetch): ")
    add_bullet(" Sau khi có dữ liệu, Worker mở transaction mới, kiểm tra lease_owner có còn thuộc về nó không. Nếu hợp lệ: INSERT content_versions (DRAFT), UPDATE jobs (COMPLETED) và Commit.", "Bước 4 (Complete Atomic): ")

    # --- PHẦN 4 ---
    add_h1("PHẦN 4: QUẢN LÝ TRANSACTION, ĐỒNG THỜI & ACID")
    add_h2("4.1. Chống Race Condition khi Xuất Bản (Publish Gate)")
    add_p("Để đảm bảo không bao giờ có 2 Admin cùng xuất bản đè 2 phiên bản khác nhau lên cùng 1 địa điểm:")
    add_bullet(" Hệ thống thực hiện Pessimistic Row Lock (SELECT FOR UPDATE) trên bản ghi bảng pois.", "Khóa dòng nghiêm ngặt: ")
    add_bullet(" Bắt buộc phiên bản được duyệt phải có đầy đủ 5 ngôn ngữ (vi, en, zh, fr, ja), mỗi bài thuyết minh phải đạt tối thiểu >=20 ký tự.", "Kiểm tra tính toàn vẹn 5 ngôn ngữ: ")
    add_bullet(" Sau khi kiểm tra thành công, con trỏ pois.published_version_id được cập nhật và version.state chuyển sang PUBLISHED trong cùng transaction.", "Cập nhật nguyên tử: ")

    add_h2("4.2. Khả năng Tự Phục Hồi Lỗi (Fault Tolerance & Backoff)")
    add_p("Hệ thống được thiết kế theo tư duy chịu lỗi (Design for Failure):")
    add_bullet(" Nếu Wikipedia API gặp sự cố, Worker tự tăng attempts. Sau 2 lần thử, hệ thống áp dụng Exponential Backoff (chờ 10s, 20s). Quá 3 lần lỗi, job chuyển FAILED để Admin xem xét.", "Retry & Backoff: ")
    add_bullet(" Nếu tiến trình Worker bị crash hoặc mất điện, sau 120 giây (JOB_LEASE_SECONDS), lease hết hạn. Lần quét tiếp theo, worker mới sẽ thu hồi và chạy lại job.", "Crash Recovery: ")

    # --- PHẦN 5 ---
    add_h1("PHẦN 5: BẢO MẬT & QUẢN LÝ PHIÊN")
    add_bullet(" Mật khẩu tài khoản được mã hóa bằng thuật toán Argon2id (Time=2, Memory=64MB, Parallelism=8), có khả năng chống lại tấn công brute-force phần cứng GPU/ASIC.", "1. Mã hóa Argon2id: ")
    add_bullet(" Token được sinh ngẫu nhiên (32 bytes). Phía Server CHỈ LƯU bản băm SHA-256 của token. Nếu database bị rò rỉ, kẻ tấn công cũng không thể khôi phục token phiên.", "2. Server-side Session Hashing: ")
    add_bullet(" Giới hạn số lần đăng nhập sai theo IP/tài khoản (Rate Limiting). Quá 5 lần thất bại liên tiếp sẽ trả về HTTP 429 Too Many Requests trong 15 phút.", "3. Chống Brute-force: ")
    add_bullet(" Hệ thống hoàn toàn không lưu trữ tọa độ GPS của du khách lên máy chủ. Việc tính toán geofence diễn ra 100% tại Mobile Client.", "4. Quyền riêng tư (Zero-GPS on Server): ")

    # --- PHẦN 6 ---
    add_h1("PHẦN 6: TIẾN HÓA CƠ SỞ DỮ LIỆU (MIGRATION CÓ CHECKSUM)")
    add_p("Hệ thống tự xây dựng công cụ db:migrate (app/migrate.py) với các cơ chế bảo vệ cấp doanh nghiệp:")
    add_bullet(" Sử dụng PostgreSQL Transaction Advisory Lock (khóa 0x5131544f) để ngăn chặn 2 tiến trình migrate cùng lúc gây tranh chấp.", "Advisory Lock: ")
    add_bullet(" Tính mã băm SHA-256 của toàn bộ nội dung file SQL (chuẩn hóa ký tự xuống dòng). Lưu vết trong bảng schema_migrations. Nếu một file SQL đã chạy trong quá khứ bị chỉnh sửa nội dung, runner lập tức dừng lại và báo động.", "SHA-256 Checksum: ")
    add_bullet(" Nghiêm cấm các lệnh tự ý xóa bảng/cột (auto-down). Việc thay đổi lược đồ tuân thủ nguyên tắc Expand - Contract để đảm bảo tương thích ngược.", "Bảo tồn dữ liệu: ")

    # --- PHẦN 7 ---
    add_h1("PHẦN 7: PIPELINE CI/CD TOÀN DIỆN KHÔNG DOCKER")
    add_p("Toàn bộ quy trình Build, Test, Deploy và Rollback được cấu hình tự động thông qua GitHub Actions (.github/workflows/):")

    add_h2("7.1. CI Workflow (ci.yml)")
    add_bullet(" Khởi chạy trực tiếp PostgreSQL native trên Ubuntu Runner 24.04 (sudo systemctl start postgresql).", "Khởi tạo Native DB: ")
    add_bullet(" Chạy pytest trên database kiểm thử độc lập (tourism_test), kiểm tra toàn bộ luồng tích hợp, phân quyền, xử lý đồng thời và worker lease.", "Test Automation: ")
    add_bullet(" Chạy script export_openapi.py để xuất schema openapi.json làm artifact lưu trữ kiểm tra breaking change.", "API Contract Export: ")

    add_h2("7.2. CD Workflow (cd.yml) & Kỹ thuật Atomic Symlink Swap")
    add_bullet(" Đóng gói git archive thành file nén release.tar.gz kèm mã băm release.sha256 theo đúng commit SHA.", "Immutable Bundle: ")
    add_bullet(" Kết nối SSH an toàn qua khóa Ed25519 được xác thực qua KNOWN_HOSTS.", "Secure Transport: ")
    add_bullet(" Giải nén vào thư mục /opt/quan1-<env>/releases/<sha>. Chạy db:migrate trên DB Prod.", "Giải nén & Migrate: ")
    add_bullet(" Tráo đổi symlink nguyên tử: /opt/quan1-<env>/current -> releases/<sha>. Khởi động lại service bằng sudo systemctl restart quan1-api@env quan1-worker@env.", "Atomic Symlink Swap: ")

    add_h2("7.3. Health Readiness Gate & Tự động Rollback")
    add_p("Sau khi restart, script deployment thăm dò liên tục tới endpoint /health/ready. Endpoint này yêu cầu đồng thời cả 3 điều kiện:")
    add_bullet(" Kết nối cơ sở dữ liệu PostgreSQL bình thường.", "1. Database Check: ")
    add_bullet(" Checksum và số lượng cột trong DB khớp 100% với phiên bản code mới.", "2. Schema Check: ")
    add_bullet(" Worker Heartbeat còn mới trong vòng 90 giây (WORKER_STALE_SECONDS).", "3. Worker Freshness: ")
    add_callout(doc, [
        "Nếu sau 40 giây kiểm tra mà endpoint /health/ready không đạt, script release.py lập tức tráo ngược symlink về phiên bản Git SHA cũ và restart lại services.",
        "Quy trình rollback tự động diễn ra trong 2-3 giây, đảm bảo người dùng không bao giờ gặp lỗi gián đoạn dịch vụ."
    ], "CƠ CHẾ AUTO-ROLLBACK AN TOÀN:")

    # --- PHẦN 8 ---
    add_h1("PHẦN 8: BỘ CÂU HỎI PHẢN BIỆN KỸ THUẬT (BACKEND Q&A)")
    
    qa_list = [
        (
            "Câu 1: Tại sao không dùng Microservices và Docker ngay từ đầu?",
            "Quy mô nghiệp vụ du lịch Quận 1 phục vụ hàng chục nghìn lượt tra cứu, chưa có bài toán hàng triệu RPS hay đội ngũ hàng trăm kỹ sư phát triển độc lập. Dùng microservices sẽ phát sinh overhead về network latency giữa các container, serialize JSON liên tục và phức tạp hóa tính toàn vẹn dữ liệu. Kiến trúc Modular Monolith native cho phép đạt hiệu năng tối đa trên nhân Linux, giảm 40% RAM/CPU và giữ trọn tính ACID."
        ),
        (
            "Câu 2: Bảng 'jobs' dùng làm hàng đợi có bị bloat và làm chậm database lâu dài không?",
            "Hệ thống đã đánh index phức hợp trên (state, created_at) và (lease_expires_at). Câu lệnh SKIP LOCKED chỉ quét các bản ghi PENDING hoặc hết hạn lease (thường chỉ vài bản ghi nhờ LIMIT 1). Ngoài ra, hệ thống áp dụng cơ chế Housekeeping định kỳ dọn dẹp các job COMPLETED quá 30 ngày sang bảng lưu trữ jobs_history và chạy VACUUM định kỳ."
        ),
        (
            "Câu 3: Cơ chế chống gọi trùng (Idempotency) hoạt động ra sao khi mạng client chập chờn?",
            "Client gửi kèm Header Idempotency-Key (8-100 ký tự) cho các thao tác mutation. ContentService kiểm tra xem key này đã tồn tại trong bảng jobs chưa. Nếu đã có, hệ thống không tạo job thứ hai mà trả về ngay trạng thái của job đang xử lý. Đối với danh sách yêu thích, bảng favorites dùng Composite Primary Key (user_id, poi_id) kết hợp ON CONFLICT DO NOTHING, đảm bảo gọi 1 lần hay nhiều lần thì dữ liệu vẫn toàn vẹn."
        ),
        (
            "Câu 4: Làm thế nào đảm bảo Zero-Downtime khi Migrate database?",
            "Hệ thống tuân thủ nguyên tắc Expand - Contract: (1) Bước Expand chỉ thêm bảng hoặc cột mới cho phép NULL; code cũ vẫn chạy bình thường; (2) Deploy code mới để bắt đầu đọc/ghi cột mới; (3) Bước Contract sau khi hệ thống ổn định mới gán ràng buộc NOT NULL hoặc dọn cột cũ. Tuyệt đối không dùng các câu lệnh lock toàn bảng trong giờ cao điểm."
        ),
        (
            "Câu 5: Nếu Worker bị sập đột ngột khi đang crawl Wikipedia thì xử lý thế nào?",
            "Worker đã giải phóng DB lock trước khi gọi mạng ra ngoài, nên việc sập không gây treo DB. Job vẫn ở trạng thái PROCESSING với lease 120s. Sau 120s, worker dự phòng quét thấy lease_expires_at < NOW() sẽ tự động claim lại job, tăng số lần thử attempts và tiếp tục xử lý. Sau 3 lần thất bại, job mới chuyển sang FAILED để Admin xử lý."
        )
    ]

    for q, a in qa_list:
        add_p(q, bold_prefix="❓ ", space_after=2)
        add_p(a, bold_prefix="💡 Trả lời: ", space_after=6)

    # Save document
    output_path = os.path.abspath("BAO_CAO_THUYET_TRINH_BACKEND_QUAN1_TOURISM.docx")
    doc.save(output_path)
    print(f"SUCCESS: Document generated at {output_path}")

if __name__ == "__main__":
    build_document()

