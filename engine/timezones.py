"""Xử lý múi giờ lịch sử của Việt Nam qua các thời kỳ.

Lịch sử múi giờ pháp định tại Việt Nam:
1. Trước 01/05/1911: Chưa có múi giờ pháp định toàn quốc (thường quy ước UTC+7).
2. 01/05/1911 - 31/12/1942: UTC+7 (Toàn cõi Đông Dương áp dụng kinh tuyến 105° Đông).
3. 01/01/1943 - 13/03/1945: UTC+8 (Chính quyền thực dân Pháp đổi sang UTC+8).
4. 14/03/1945 - 02/09/1945: UTC+9 (Phát xít Nhật đảo chính Pháp, áp dụng giờ Tokyo UTC+9).
5. 03/09/1945 - 31/12/1959: UTC+7 (Chính phủ VNDCCH ban bố trở về UTC+7; miền Nam cũng dùng UTC+7).
6. 01/01/1960 - 30/04/1975:
   - Miền Bắc (từ vĩ tuyến 17 trở ra Bắc): UTC+7
   - Miền Nam (từ Thừa Thiên Huế trở vào Nam, chế độ VNCH): Đổi sang UTC+8 từ 01/01/1960.
7. 01/05/1975 đến nay: Toàn quốc thống nhất sử dụng UTC+7 (Asia/Ho_Chi_Minh).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, time, timezone, timedelta

# Danh sách từ khóa các tỉnh / thành phố miền Nam (từ Thừa Thiên Huế trở vào Nam)
SOUTH_VIETNAM_KEYWORDS = [
    "thua thien", "hue", "da nang", "quang nam", "quang ngai", "binh dinh",
    "phu yen", "khanh hoa", "nha trang", "ninh thuan", "phan rang", "binh thuan",
    "phan thiet", "kon tum", "gia lai", "pleiku", "dak lak", "buon ma thuot",
    "dak nong", "lam dong", "da lat", "bao loc", "binh phuoc", "dong nai",
    "bien hoa", "tay ninh", "binh duong", "thu dau mot", "sai gon", "sai-gon",
    "saigon", "ho chi minh", "hcm", "tphcm", "gia dinh", "ba ria", "vung tau",
    "long an", "tan an", "tien giang", "my tho", "ben tre", "tra vinh",
    "vinh long", "dong thap", "cao lanh", "sa dec", "an giang", "long xuyen",
    "chau doc", "kien giang", "rach gia", "ha tien", "can tho", "hau giang",
    "soc trang", "bac lieu", "ca mau", "phu quoc", "vinh binh", "dinh tuong",
    "phuoc tuy", "long khanh", "kien hoa", "phong dinh", "an xuyen", "ba xuyen"
]


def _normalize_text(s: str) -> str:
    """Loại bỏ dấu tiếng Việt và chuyển sang chữ thường không dấu để so khớp từ khóa."""
    s = s.lower().strip()
    s = s.replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


def is_south_vietnam(birth_place: str) -> bool:
    """Xác định nơi sinh có thuộc miền Nam (từ vĩ tuyến 17 trở vào Nam) hay không."""
    normalized = _normalize_text(birth_place)
    for kw in SOUTH_VIETNAM_KEYWORDS:
        if kw in normalized:
            return True
    return False


@dataclass(frozen=True)
class TimezoneInfo:
    utc_offset_hours: int
    note: str | None = None


def get_vietnam_utc_offset(birth_date: date, birth_place: str = "") -> TimezoneInfo:
    """Xác định múi giờ UTC lịch sử tại Việt Nam vào thời điểm `birth_date` và `birth_place`.
    
    Trả về TimezoneInfo gồm:
        - utc_offset_hours: số giờ lệch UTC (+7, +8, hoặc +9)
        - note: ghi chú giải thích nếu rơi vào giai đoạn múi giờ đặc biệt lịch sử.
    """
    d = birth_date

    # 1. Giai đoạn Nhật đảo chính: 14/03/1945 - 02/09/1945
    if date(1945, 3, 14) <= d <= date(1945, 9, 2):
        return TimezoneInfo(
            utc_offset_hours=9,
            note="Thời kỳ Nhật chiếm đóng (14/03/1945 - 02/09/1945) áp dụng múi giờ Tokyo UTC+9. "
                 "Đã tự động quy đổi giờ sinh sang giờ chuẩn thiên văn."
        )

    # 2. Giai đoạn Pháp áp dụng giờ mùa hè: 01/01/1943 - 13/03/1945
    if date(1943, 1, 1) <= d <= date(1945, 3, 13):
        return TimezoneInfo(
            utc_offset_hours=8,
            note="Thời kỳ toàn Đông Dương áp dụng múi giờ UTC+8 (01/01/1943 - 13/03/1945). "
                 "Đã tự động quy đổi giờ sinh sang giờ chuẩn thiên văn."
        )

    # 3. Giai đoạn chia cắt 1960 - 30/04/1975:
    if date(1960, 1, 1) <= d <= date(1975, 4, 30):
        if is_south_vietnam(birth_place):
            return TimezoneInfo(
                utc_offset_hours=8,
                note="Tại miền Nam thời kỳ 1960 - 30/04/1975 áp dụng múi giờ UTC+8 (nhanh hơn giờ miền Bắc 1 giờ). "
                     "Đã tự động quy đổi giờ sinh về múi giờ chuẩn UTC+7 để tính toán chính xác."
            )
        # Miền Bắc hoặc không rõ nơi sinh
        return TimezoneInfo(
            utc_offset_hours=7,
            note="Thời kỳ 1960 - 1975: miền Bắc áp dụng múi giờ UTC+7."
        )

    # Tất cả các thời kỳ còn lại (bao gồm từ 01/05/1975 đến nay): UTC+7
    return TimezoneInfo(utc_offset_hours=7, note=None)


def local_birth_to_utc(birth_date: date, birth_time: time, birth_place: str = "") -> tuple[datetime, TimezoneInfo]:
    """Chuyển đổi ngày và giờ sinh địa phương ở Việt Nam sang datetime UTC có timezone."""
    tz_info = get_vietnam_utc_offset(birth_date, birth_place)
    local_dt = datetime.combine(birth_date, birth_time)
    # Trừ đi số giờ offset để ra UTC
    utc_dt = local_dt - timedelta(hours=tz_info.utc_offset_hours)
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt, tz_info
