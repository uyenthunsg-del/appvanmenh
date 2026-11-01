# Tử vi web — Giai đoạn 1, 2 & 3: Thần số học + Bát Tự + Bản Đồ Sao (Natal Chart)

Website nhập họ tên, giới tính, ngày giờ sinh, nơi sinh:
- **Giai đoạn 1: Thần số học**: số chủ đạo, sứ mệnh (biểu đạt), linh hồn, thái độ, nhân cách, trưởng thành, ngày sinh và biểu đồ chu kỳ vận số.
- **Giai đoạn 2: Bát Tự (Tứ Trụ)**: bảng 4 cột trụ (Năm, Tháng, Ngày, Giờ), ngũ hành, can chi âm dương, nạp âm, thập thần, tàng can, vòng Tràng Sinh, thần sát cơ bản, đại vận (8 bước vận kèm chiều thuận/nghịch và tuổi khởi vận), thống kê năng lượng ngũ hành.
- **Giai đoạn 3: Bản Đồ Sao (Natal Chart)**:
  * Tính toán vị trí 10 hành tinh (Mặt Trời, Mặt Trăng, Thủy, Kim, Hỏa, Mộc, Thổ, Thiên Vương, Hải Vương, Diêm Vương), 4 góc trục (ASC, MC, DSC, IC), điểm giao hội Mặt Trăng (La Hầu / Kế Đô) và tiểu hành tinh Chiron.
  * Trạng thái nghịch hành (Retrograde `Rx`).
  * 12 Nhà hoàng đạo theo các hệ thống: **Placidus** (mặc định), **Whole Sign** (cung nguyên vẹn), **Equal House** (nhà bằng nhau).
  * 5 góc chiếu chính (Aspects): Trùng tụ (0°), Lục hợp (60°), Vuông góc (90°), Tam hợp (120°), Đối đỉnh (180°) kèm dung sai (orb).
  * Vẽ bánh xe Bản Đồ Sao tròn bằng **SVG vector thuần**, xoay Cung Mọc (AC) chuẩn ở vị trí 9 giờ, tô màu 4 nguyên tố và đường liên kết góc chiếu.
  * Tự động tra cứu kinh độ, vĩ độ và múi giờ cho 63 tỉnh/thành Việt Nam và quốc tế (offline, không phụ thuộc Google API).
- Nút "Xem chi tiết luận giải" đang để chờ, sẽ kích hoạt ở Giai đoạn 5 (AI).

- **PHP 8.2** (PDO, curl): form, giao diện, lưu database, gọi engine.
- **Python / FastAPI** (`engine/`): toàn bộ phần tính toán thiên văn, can chi, trả JSON. PHP không tự tính.
- **MariaDB**: bảng `users`, `profiles`, `readings`.

## Các lựa chọn trường phái đã triển khai

| Môn | Điểm | Lựa chọn & Cách xử lý |
| --- | --- | --- |
| **Bản Đồ Sao** | Hệ thống Nhà | Mặc định: **Placidus**; có nút bấm chuyển sang **Whole Sign** và **Equal House** |
| **Bản Đồ Sao** | Góc chiếu & Dung sai | 5 góc chính (0°, 60°, 90°, 120°, 180°); orb 8°-10° cho Sun/Moon, 6°-8° cho các hành tinh khác |
| **Bản Đồ Sao** | Bánh xe SVG | ASC cố định tại 9 giờ; đường nối góc màu xanh (thuận lợi) và màu đỏ (thử thách); chống đè lấn khi trùng tụ |
| **Bát Tự** | Tiết khí tháng | Tính theo 12 Tiết khí thiên văn thực tế (apparent solar longitude) bằng PyEphem, ranh giới năm theo Lập Xuân |
| **Bát Tự** | Giờ Tý (23h-1h) | Mặc định: từ 23h đã sang ngày mới (Nhất nhật tị Tý - chuẩn Tử Bình); có nút chuyển sang Dạ Tý để đối chiếu |
| **Bát Tự** | Tràng Sinh Can Thổ | Mặc định: Hỏa Thổ đồng cung; có nút chuyển sang Thủy Thổ đồng cung |
| **Bát Tự** | Tuổi khởi Đại vận | Tính theo khoảng cách ngày/giờ từ lúc sinh tới Tiết khí kề cận (3 ngày = 1 năm, 1 ngày = 4 tháng, 1 giờ = 5 ngày) |
| **Bát Tự** | Múi giờ lịch sử VN | Tự động nhận diện thời kỳ chia cắt 1960-1975 (miền Nam UTC+8) và 1943-1945 để quy đổi về giờ thực UTC+7 |
| **Thần số** | Quy đổi chữ cái | Pythagoras (A=1 … I=9, J=1 … R=9, S=1 … Z=8) |
| **Thần số** | Chữ Y | Tự động: nguyên âm khi đứng sau phụ âm và không cạnh nguyên âm nào; có nút đổi sang "luôn nguyên âm" / "luôn phụ âm" |
| **Thần số** | Số chủ đạo | Rút gọn riêng ngày, tháng, năm (giữ 11/22/33) rồi cộng lại và rút gọn (giữ 11/22/33) |

## Cài đặt trên FlyEnv (Windows)

Giải nén toàn bộ vào `E:\tuvi` (có các thư mục `public`, `src`, `engine`, `data`, `database`).

**1. Site.** Thư mục gốc của site `tuvi.test` phải là `E:\tuvi\public`, không phải `E:\tuvi`
(để không ai mở được `src/`, `engine/` hay `.env`).

**2. Database.** Trong FlyEnv, mục MariaDB, đã tạo database `tuvi` (utf8mb4) và user `tuvi`.
Nạp bảng bằng phpMyAdmin: chọn database `tuvi`, tab *Import*, chọn `E:\tuvi\database\schema.sql`.
File có thể chạy lại nhiều lần.

**3. File `.env`.** Trong PowerShell:

```
cd E:\tuvi
Copy-Item .env.example .env
```

Mở `.env` bằng VS Code, điền `DB_PASS` (mật khẩu user `tuvi`) và kiểm tra `DB_PORT`
(cổng MariaDB trong FlyEnv). Không gửi `.env` cho ai và không đưa lên git.

**4. Engine Python.** Tạo môi trường ảo và cài thư viện (dùng đường dẫn Python của FlyEnv):

```
cd E:\tuvi\engine
& "D:\FlyEnv-Data\app\python-3.14.7\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Chạy test:

```
.\.venv\Scripts\python.exe -m pytest
```

Chạy engine (để cửa sổ này mở):

```
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000/health, kết quả đúng là `{"status":"ok", ...}`.
Trang http://127.0.0.1:8000/docs cho thử API trực tiếp. Engine không có xác thực nên
luôn để `--host 127.0.0.1`, không đổi sang `0.0.0.0`.

**5. Dùng thử.** Mở http://tuvi.test, nhập thông tin, bấm *Xem kết quả*.

## Cấu trúc

```
public/    index.php (form), submit.php (nhận form), result.php (kết quả), assets/ (css, js, img/stars.svg)
src/       bootstrap, Env, Database, ApiClient (curl), Csrf, Validator, ProfileRepository,
           Content (đọc data/), Chart (vẽ biểu đồ SVG), Controllers/, views/
engine/    main.py (FastAPI), numerology.py, bazi.py, solar_terms.py, timezones.py,
           geocoding.py, natal.py, natal_svg.py, tests/, requirements*.txt, pytest.ini
data/      numerology.json, bazi.json, natal.json
database/  schema.sql
```

## Bảo mật đã làm ở giai đoạn này

- Truy vấn dùng prepared statement thật (`ATTR_EMULATE_PREPARES = false`).
- Mọi dữ liệu in ra HTML đi qua `e()` (htmlspecialchars).
- Form có token CSRF; dữ liệu được validate ở PHP và validate lại ở engine.
- Khóa/mật khẩu chỉ nằm trong `.env`, đọc ở phía server.

Chưa có đăng nhập: ai biết số `id` trong `result.php?id=...` đều xem được hồ sơ đó. Phần này xử lý ở Giai đoạn 6.

## Nếu gặp lỗi

- **Trang kết quả báo "Không kết nối được engine"**: engine chưa chạy hoặc sai `ENGINE_URL` trong `.env`.
- **Engine đang chạy bản cũ (trang kết quả báo thiếu `attitude`/`personal_year`)**: tắt cửa sổ uvicorn cũ rồi chạy lại,
  vì engine không tự nạp lại code mới.
- **Lỗi kết nối database**: kiểm tra `DB_PASS`, `DB_PORT` và dịch vụ MariaDB đã bật.
- **`pip install` lỗi khi cài FastAPI/pydantic với Python 3.14**: cài thêm Python 3.12 trong FlyEnv,
  tạo lại `.venv` bằng bản đó.
