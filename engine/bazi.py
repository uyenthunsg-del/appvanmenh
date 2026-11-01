"""Module Bát Tự (Tứ Trụ) Tử Bình chính xác cao.

Tính toán:
- Tứ trụ: Can Chi của Năm, Tháng, Ngày, Giờ (kèm Ngũ Hành, Âm Dương, Nạp Âm).
- Phân tích ranh giới năm/tháng theo Tiết Khí thiên văn chính xác đến từng phút.
- Thập Thần đối với Nhật Can (Can Ngày) cho cả Thiên Can và Tàng Can trong Địa Chi.
- Vòng Tràng Sinh (12 cung) cho Nhật Can (hỗ trợ trường phái Hỏa Thổ và Thủy Thổ đồng cung).
- Thần Sát cơ bản: Quý Nhân, Lộc Thần, Kình Dương, Dịch Mã, Đào Hoa, Hoa Cái, Tướng Tinh, Cô Thần, Quả Tú, Kiếp Sát, Không Vong...
- Đại Vận (8 - 10 bước vận): chiều vận, tuổi khởi vận chính xác đến tháng, Can Chi và Thập Thần từng đại vận.
- Thống kê tỷ lệ và năng lượng Ngũ Hành.
- Hỗ trợ tùy chọn Giờ Tý (23h sang ngày mới hoặc phân biệt Dạ Tý).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal

import solar_terms
import timezones

# 10 Thiên Can
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
STEM_ELEMENTS = ["Mộc", "Mộc", "Hỏa", "Hỏa", "Thổ", "Thổ", "Kim", "Kim", "Thủy", "Thủy"]
STEM_YIN_YANG = ["Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm"]

# 12 Địa Chi
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
BRANCH_ELEMENTS = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa", "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]
BRANCH_YIN_YANG = ["Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm"]
BRANCH_ANIMALS = ["Chuột", "Trâu", "Hổ", "Mèo", "Rồng", "Rắn", "Ngựa", "Dê", "Khỉ", "Gà", "Chó", "Lợn"]

# Tàng Can trong 12 Địa Chi: (Tên can, Loại khí, Tỷ trọng tương đối)
HIDDEN_STEMS: dict[str, list[tuple[str, str, float]]] = {
    "Tý": [("Quý", "Chính khí", 1.0)],
    "Sửu": [("Kỷ", "Chính khí", 0.6), ("Quý", "Trung khí", 0.3), ("Tân", "Dư khí", 0.1)],
    "Dần": [("Giáp", "Chính khí", 0.6), ("Bính", "Trung khí", 0.3), ("Mậu", "Dư khí", 0.1)],
    "Mão": [("Ất", "Chính khí", 1.0)],
    "Thìn": [("Mậu", "Chính khí", 0.6), ("Ất", "Trung khí", 0.3), ("Quý", "Dư khí", 0.1)],
    "Tị": [("Bính", "Chính khí", 0.6), ("Canh", "Trung khí", 0.3), ("Mậu", "Dư khí", 0.1)],
    "Ngọ": [("Đinh", "Chính khí", 0.7), ("Kỷ", "Trung khí", 0.3)],
    "Mùi": [("Kỷ", "Chính khí", 0.6), ("Đinh", "Trung khí", 0.3), ("Ất", "Dư khí", 0.1)],
    "Thân": [("Canh", "Chính khí", 0.6), ("Nhâm", "Trung khí", 0.3), ("Mậu", "Dư khí", 0.1)],
    "Dậu": [("Tân", "Chính khí", 1.0)],
    "Tuất": [("Mậu", "Chính khí", 0.6), ("Tân", "Trung khí", 0.3), ("Đinh", "Dư khí", 0.1)],
    "Hợi": [("Nhâm", "Chính khí", 0.7), ("Giáp", "Trung khí", 0.3)],
}

# 12 Cung Vòng Tràng Sinh theo thứ tự chuẩn
LIFE_STAGES = [
    "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng",
    "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"
]

# Vị trí khởi Trường Sinh của 10 Can và chiều đi (1=thuận, -1=nghịch)
# Chi index: 0=Tý, 1=Sửu, 2=Dần, 3=Mão, 4=Thìn, 5=Tị, 6=Ngọ, 7=Mùi, 8=Thân, 9=Dậu, 10=Tuất, 11=Hợi
LIFE_STAGE_START = {
    # Can: (chi_bat_dau_hoa_tho, chieu, chi_bat_dau_thuy_tho)
    "Giáp": (11, 1),   # Hợi, thuận
    "Ất": (6, -1),     # Ngọ, nghịch
    "Bính": (2, 1),    # Dần, thuận
    "Đinh": (9, -1),   # Dậu, nghịch
    "Mậu": (2, 1, 8),  # Hỏa Thổ: Dần; Thủy Thổ: Thân, thuận
    "Kỷ": (9, -1, 3),  # Hỏa Thổ: Dậu; Thủy Thổ: Mão, nghịch
    "Canh": (5, 1),    # Tị, thuận
    "Tân": (0, -1),    # Tý, nghịch
    "Nhâm": (8, 1),    # Thân, thuận
    "Quý": (3, -1),    # Mão, nghịch
}

# Lục Thập Hoa Giáp Nạp Âm (60 cặp Can Chi)
NA_YIN = {
    ("Giáp", "Tý"): "Hải Trung Kim", ("Ất", "Sửu"): "Hải Trung Kim",
    ("Bính", "Dần"): "Lư Trung Hỏa", ("Đinh", "Mão"): "Lư Trung Hỏa",
    ("Mậu", "Thìn"): "Đại Lâm Mộc", ("Kỷ", "Tị"): "Đại Lâm Mộc",
    ("Canh", "Ngọ"): "Lộ Bàng Thổ", ("Tân", "Mùi"): "Lộ Bàng Thổ",
    ("Nhâm", "Thân"): "Kiếm Phong Kim", ("Quý", "Dậu"): "Kiếm Phong Kim",
    ("Giáp", "Tuất"): "Sơn Đầu Hỏa", ("Ất", "Hợi"): "Sơn Đầu Hỏa",
    ("Bính", "Tý"): "Giản Hạ Thủy", ("Đinh", "Sửu"): "Giản Hạ Thủy",
    ("Mậu", "Dần"): "Thành Đầu Thổ", ("Kỷ", "Mão"): "Thành Đầu Thổ",
    ("Canh", "Thìn"): "Bạch Lạp Kim", ("Tân", "Tị"): "Bạch Lạp Kim",
    ("Nhâm", "Ngọ"): "Dương Liễu Mộc", ("Quý", "Mùi"): "Dương Liễu Mộc",
    ("Giáp", "Thân"): "Tuyền Trung Thủy", ("Ất", "Dậu"): "Tuyền Trung Thủy",
    ("Bính", "Tuất"): "Ốc Thượng Thổ", ("Đinh", "Hợi"): "Ốc Thượng Thổ",
    ("Mậu", "Tý"): "Tích Lịch Hỏa", ("Kỷ", "Sửu"): "Tích Lịch Hỏa",
    ("Canh", "Dần"): "Tùng Bách Mộc", ("Tân", "Mão"): "Tùng Bách Mộc",
    ("Nhâm", "Thìn"): "Trường Lưu Thủy", ("Quý", "Tị"): "Trường Lưu Thủy",
    ("Giáp", "Ngọ"): "Sa Trung Kim", ("Ất", "Mùi"): "Sa Trung Kim",
    ("Bính", "Thân"): "Sơn Hạ Hỏa", ("Đinh", "Dậu"): "Sơn Hạ Hỏa",
    ("Mậu", "Tuất"): "Bình Địa Mộc", ("Kỷ", "Hợi"): "Bình Địa Mộc",
    ("Canh", "Tý"): "Bích Thượng Thổ", ("Tân", "Sửu"): "Bích Thượng Thổ",
    ("Nhâm", "Dần"): "Kim Bạch Kim", ("Quý", "Mão"): "Kim Bạch Kim",
    ("Giáp", "Thìn"): "Phúc Đăng Hỏa", ("Ất", "Tị"): "Phúc Đăng Hỏa",
    ("Bính", "Ngọ"): "Thiên Hà Thủy", ("Đinh", "Mùi"): "Thiên Hà Thủy",
    ("Mậu", "Thân"): "Đại Trạch Thổ", ("Kỷ", "Dậu"): "Đại Trạch Thổ",
    ("Canh", "Tuất"): "Thoa Xuyến Kim", ("Tân", "Hợi"): "Thoa Xuyến Kim",
    ("Nhâm", "Tý"): "Tang Đố Mộc", ("Quý", "Sửu"): "Tang Đố Mộc",
    ("Giáp", "Dần"): "Đại Khê Thủy", ("Ất", "Mão"): "Đại Khê Thủy",
    ("Bính", "Thìn"): "Sa Trung Thổ", ("Đinh", "Tị"): "Sa Trung Thổ",
    ("Mậu", "Ngọ"): "Thiên Thượng Hỏa", ("Kỷ", "Mùi"): "Thiên Thượng Hỏa",
    ("Canh", "Thân"): "Thạch Lựu Mộc", ("Tân", "Dậu"): "Thạch Lựu Mộc",
    ("Nhâm", "Tuất"): "Đại Hải Thủy", ("Quý", "Hợi"): "Đại Hải Thủy",
}

# Bảng sinh / khắc ngũ hành: element_index (0: Kim, 1: Thủy, 2: Mộc, 3: Hỏa, 4: Thổ)
ELEMENT_ORDER = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]
# Mộc sinh Hỏa sinh Thổ sinh Kim sinh Thủy sinh Mộc
# Mộc khắc Thổ khắc Thủy khắc Hỏa khắc Kim khắc Mộc


def get_ten_god(day_master_stem: str, target_stem: str) -> str:
    """Xác định Thập Thần của `target_stem` so với Nhật Can `day_master_stem`."""
    dm_idx = STEMS.index(day_master_stem)
    t_idx = STEMS.index(target_stem)

    dm_elem = STEM_ELEMENTS[dm_idx]
    t_elem = STEM_ELEMENTS[t_idx]
    same_polarity = (STEM_YIN_YANG[dm_idx] == STEM_YIN_YANG[t_idx])

    if dm_elem == t_elem:
        return "Tỷ Kiên" if same_polarity else "Kiếp Tài"

    dm_pos = ELEMENT_ORDER.index(dm_elem)
    t_pos = ELEMENT_ORDER.index(t_elem)

    # Sinh: Nhật can sinh target (dm sinh t)
    if (dm_pos + 1) % 5 == t_pos:
        return "Thực Thần" if same_polarity else "Thương Quan"

    # Được sinh: Target sinh nhật can (t sinh dm)
    if (t_pos + 1) % 5 == dm_pos:
        return "Thiên Ấn" if same_polarity else "Chính Ấn"

    # Khắc: Nhật can khắc target (dm khắc t)
    if (dm_pos + 2) % 5 == t_pos:
        return "Thiên Tài" if same_polarity else "Chính Tài"

    # Bị khắc: Target khắc nhật can (t khắc dm)
    if (t_pos + 2) % 5 == dm_pos:
        return "Thất Sát" if same_polarity else "Chính Quan"

    return "Tỷ Kiên"


def get_life_stage(stem: str, branch: str, tu_mode: Literal["fire", "water"] = "fire") -> str:
    """Tính vị trí cung Tràng Sinh của thiên can `stem` tại địa chi `branch`."""
    info = LIFE_STAGE_START[stem]
    start_branch = info[0]
    direction = info[1]
    if len(info) > 2 and tu_mode == "water":
        start_branch = info[2]

    target_branch_idx = BRANCHES.index(branch)
    # Khoảng cách từ start_branch tới target_branch_idx theo chiều direction
    if direction == 1:
        step = (target_branch_idx - start_branch) % 12
    else:
        step = (start_branch - target_branch_idx) % 12

    return LIFE_STAGES[step]


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Chuyển ngày dương lịch (lịch Gregory) sang Julian Day Number tại 12h trưa."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def get_day_can_chi(dt_date: date) -> tuple[str, str, int]:
    """Tính Can Chi ngày theo chu kỳ 60 hoa giáp liên tục.
    
    Hệ quy chiếu chuẩn xác:
    2000-01-01 là ngày Mậu Ngọ (Can 4, Chi 6, vị trí 54 trong 60 hoa giáp).
    """
    jdn = gregorian_to_jdn(dt_date.year, dt_date.month, dt_date.day)
    # JDN của 2000-01-01 là 2451545. (2451545 + 49) % 60 = 54 (Mậu Ngọ)
    idx_60 = (jdn + 49) % 60
    stem = STEMS[idx_60 % 10]
    branch = BRANCHES[idx_60 % 12]
    return stem, branch, idx_60


def get_hour_branch_idx(hour: int, minute: int) -> int:
    """Xác định chi của giờ theo 12 canh giờ chuẩn (Tý: 23h-1h, Sửu: 1h-3h...)."""
    # 23:00 - 00:59 -> Tý (0)
    # 01:00 - 02:59 -> Sửu (1)
    # ...
    # 21:00 - 22:59 -> Hợi (11)
    if hour == 23 or hour == 0:
        return 0
    return (hour + 1) // 2


def get_hour_can_chi(day_stem: str, hour_branch_idx: int) -> tuple[str, str]:
    """Tính Can Chi giờ theo quy tắc Ngũ Thử Độn:
    
    - Giáp, Kỷ: Tý là Giáp Tý (0)
    - Ất, Canh: Tý là Bính Tý (2)
    - Bính, Tân: Tý là Mậu Tý (4)
    - Đinh, Nhâm: Tý là Canh Tý (6)
    - Mậu, Quý: Tý là Nhâm Tý (8)
    """
    day_stem_idx = STEMS.index(day_stem)
    first_hour_stem_idx = (day_stem_idx * 2) % 10
    hour_stem_idx = (first_hour_stem_idx + hour_branch_idx) % 10
    return STEMS[hour_stem_idx], BRANCHES[hour_branch_idx]


def get_month_can_chi(bazi_year_stem: str, month_branch_idx: int) -> tuple[str, str]:
    """Tính Can Chi tháng theo quy tắc Ngũ Hổ Độn:
    
    - Giáp, Kỷ: tháng Dần (tháng 1 Bát tự) là Bính Dần (2)
    - Ất, Canh: tháng Dần là Mậu Dần (4)
    - Bính, Tân: tháng Dần là Canh Dần (6)
    - Đinh, Nhâm: tháng Dần là Nhâm Dần (8)
    - Mậu, Quý: tháng Dần là Giáp Dần (0)
    """
    year_stem_idx = STEMS.index(bazi_year_stem)
    first_month_stem_idx = (year_stem_idx * 2 + 2) % 10
    # Tháng Dần là branch_idx = 2
    offset = (month_branch_idx - 2) % 12
    month_stem_idx = (first_month_stem_idx + offset) % 10
    return STEMS[month_stem_idx], BRANCHES[month_branch_idx]


def get_symbolic_stars(
    day_stem: str,
    day_branch: str,
    year_stem: str,
    year_branch: str,
    month_branch: str,
    hour_branch: str,
    day_60_idx: int,
) -> dict[str, list[str]]:
    """Tính các thần sát cho 4 trụ (Năm, Tháng, Ngày, Giờ)."""
    stars_by_pillar: dict[str, list[str]] = {
        "year": [],
        "month": [],
        "day": [],
        "hour": [],
    }

    pillars = [
        ("year", year_branch, year_stem),
        ("month", month_branch, None),
        ("day", day_branch, day_stem),
        ("hour", hour_branch, None),
    ]

    # 1. Thiên Ất Quý Nhân (theo Nhật Can hoặc Niên Can)
    # Giáp Mậu Canh: Sửu, Mùi; Ất Kỷ: Tý, Thân; Bính Đinh: Hợi, Dậu; Tân: Ngọ, Dần; Nhâm Quý: Mão, Tị
    thien_at_map = {
        "Giáp": ["Sửu", "Mùi"], "Mậu": ["Sửu", "Mùi"], "Canh": ["Sửu", "Mùi"],
        "Ất": ["Tý", "Thân"], "Kỷ": ["Tý", "Thân"],
        "Bính": ["Hợi", "Dậu"], "Đinh": ["Hợi", "Dậu"],
        "Tân": ["Ngọ", "Dần"],
        "Nhâm": ["Mão", "Tị"], "Quý": ["Mão", "Tị"],
    }
    thien_at_targets = set(thien_at_map[day_stem] + thien_at_map[year_stem])
    for p_name, p_branch, _ in pillars:
        if p_branch in thien_at_targets:
            stars_by_pillar[p_name].append("Thiên Ất Quý Nhân")

    # 2. Văn Xương Quý Nhân (theo Nhật Can)
    van_xuong_map = {
        "Giáp": "Tị", "Ất": "Ngọ", "Bính": "Thân", "Đinh": "Dậu",
        "Mậu": "Thân", "Kỷ": "Dậu", "Canh": "Hợi", "Tân": "Tý",
        "Nhâm": "Dần", "Quý": "Mão"
    }
    vx_branch = van_xuong_map[day_stem]
    for p_name, p_branch, _ in pillars:
        if p_branch == vx_branch:
            stars_by_pillar[p_name].append("Văn Xương")

    # 3. Lộc Thần (Lâm Quan của Nhật Can)
    loc_than_map = {
        "Giáp": "Dần", "Ất": "Mão", "Bính": "Tị", "Đinh": "Ngọ",
        "Mậu": "Tị", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
        "Nhâm": "Hợi", "Quý": "Tý"
    }
    lt_branch = loc_than_map[day_stem]
    for p_name, p_branch, _ in pillars:
        if p_branch == lt_branch:
            stars_by_pillar[p_name].append("Lộc Thần")

    # 4. Kình Dương (Đế Vượng của Dương Can; Âm can theo Lộc hậu nhất vị)
    kinh_duong_map = {
        "Giáp": "Mão", "Ất": "Thìn", "Bính": "Ngọ", "Đinh": "Mùi",
        "Mậu": "Ngọ", "Kỷ": "Mùi", "Canh": "Dậu", "Tân": "Tuất",
        "Nhâm": "Tý", "Quý": "Sửu"
    }
    kd_branch = kinh_duong_map[day_stem]
    for p_name, p_branch, _ in pillars:
        if p_branch == kd_branch:
            stars_by_pillar[p_name].append("Kình Dương")

    # 5. Dịch Mã, Đào Hoa, Hoa Cái, Tướng Tinh, Kiếp Sát (xét theo Chi Ngày hoặc Chi Năm)
    # Tam hợp cục:
    # Thân Tý Thìn (Thủy cục)
    # Dần Ngọ Tuất (Hỏa cục)
    # Tị Dậu Sửu (Kim cục)
    # Hợi Mão Mùi (Mộc cục)
    def get_group_stars(base_branch: str) -> dict[str, str]:
        if base_branch in ["Thân", "Tý", "Thìn"]:
            return {"Dịch Mã": "Dần", "Đào Hoa": "Dậu", "Hoa Cái": "Thìn", "Tướng Tinh": "Tý", "Kiếp Sát": "Tị"}
        if base_branch in ["Dần", "Ngọ", "Tuất"]:
            return {"Dịch Mã": "Thân", "Đào Hoa": "Mão", "Hoa Cái": "Tuất", "Tướng Tinh": "Ngọ", "Kiếp Sát": "Hợi"}
        if base_branch in ["Tị", "Dậu", "Sửu"]:
            return {"Dịch Mã": "Hợi", "Đào Hoa": "Ngọ", "Hoa Cái": "Sửu", "Tướng Tinh": "Dậu", "Kiếp Sát": "Dần"}
        # Hợi, Mão, Mùi
        return {"Dịch Mã": "Tị", "Đào Hoa": "Tý", "Hoa Cái": "Mùi", "Tướng Tinh": "Mão", "Kiếp Sát": "Thân"}

    day_group = get_group_stars(day_branch)
    year_group = get_group_stars(year_branch)

    for star_name in ["Dịch Mã", "Đào Hoa", "Hoa Cái", "Tướng Tinh", "Kiếp Sát"]:
        target_branches = {day_group[star_name], year_group[star_name]}
        for p_name, p_branch, _ in pillars:
            if p_branch in target_branches and star_name not in stars_by_pillar[p_name]:
                stars_by_pillar[p_name].append(star_name)

    # 6. Cô Thần, Quả Tú (theo Chi Năm)
    # Hợi Tý Sửu -> Dần, Tuất
    # Dần Mão Thìn -> Tị, Sửu
    # Tị Ngọ Mùi -> Thân, Thìn
    # Thân Dậu Tuất -> Hợi, Mùi
    co_qua_map = {
        "Hợi": ("Dần", "Tuất"), "Tý": ("Dần", "Tuất"), "Sửu": ("Dần", "Tuất"),
        "Dần": ("Tị", "Sửu"), "Mão": ("Tị", "Sửu"), "Thìn": ("Tị", "Sửu"),
        "Tị": ("Thân", "Thìn"), "Ngọ": ("Thân", "Thìn"), "Mùi": ("Thân", "Thìn"),
        "Thân": ("Hợi", "Mùi"), "Dậu": ("Hợi", "Mùi"), "Tuất": ("Hợi", "Mùi"),
    }
    co_branch, qua_branch = co_qua_map[year_branch]
    for p_name, p_branch, _ in pillars:
        if p_branch == co_branch:
            stars_by_pillar[p_name].append("Cô Thần")
        if p_branch == qua_branch:
            stars_by_pillar[p_name].append("Quả Tú")

    # 7. Tuần Không (Không Vong) theo Tuần của Trụ Ngày
    # Mỗi tuần có 10 can và 12 chi, 2 chi còn lại bị Không Vong
    # Tuần xác định bởi day_60_idx // 10
    tuan_idx = (day_60_idx // 10) * 10
    # Can chi đầu tuần là Giáp X:
    tuan_head_branch_idx = (day_60_idx - (day_60_idx % 10)) % 12
    # 2 chi Không Vong là 2 chi trước Giáp X (tức branch_idx - 2 và branch_idx - 1)
    kong_wang_branches = [
        BRANCHES[(tuan_head_branch_idx - 2) % 12],
        BRANCHES[(tuan_head_branch_idx - 1) % 12],
    ]
    for p_name, p_branch, _ in pillars:
        if p_branch in kong_wang_branches:
            stars_by_pillar[p_name].append("Không Vong")

    # Loại bỏ trùng lặp trong từng trụ
    for k in stars_by_pillar:
        stars_by_pillar[k] = list(dict.fromkeys(stars_by_pillar[k]))

    return stars_by_pillar


def calculate_major_cycles(
    gender: Literal["male", "female"],
    bazi_year_stem: str,
    month_stem: str,
    month_branch: str,
    birth_utc: datetime,
    prev_jie: solar_terms.SolarTermEvent,
    next_jie: solar_terms.SolarTermEvent,
    day_master_stem: str,
    tu_mode: Literal["fire", "water"] = "fire",
    num_cycles: int = 8,
) -> tuple[dict, list[dict]]:
    """Tính Đại Vận (chiều vận, tuổi khởi vận, và các bước vận).
    
    Quy tắc:
    - Dương Nam / Âm Nữ: Thuận hành.
    - Âm Nam / Dương Nữ: Nghịch hành.
    - 3 ngày = 1 năm, 1 ngày = 4 tháng, 1 giờ = 5 ngày, 12 phút = 1 ngày.
    """
    year_stem_idx = STEMS.index(bazi_year_stem)
    is_yang_year = (STEM_YIN_YANG[year_stem_idx] == "Dương")
    is_male = (gender == "male")

    # Thuận nếu (Dương Nam hoặc Âm Nữ)
    is_forward = (is_yang_year and is_male) or ((not is_yang_year) and (not is_male))

    if is_forward:
        delta = next_jie.utc_time - birth_utc
        target_jie_name = next_jie.name
    else:
        delta = birth_utc - prev_jie.utc_time
        target_jie_name = prev_jie.name

    total_seconds = max(0.0, delta.total_seconds())
    days_float = total_seconds / 86400.0

    # 3 ngày = 1 năm (360 ngày / 12 tháng)
    # Số năm = days_float // 3
    # Số ngày dư * 4 tháng
    years = int(days_float // 3)
    remaining_days = days_float % 3
    months = int((remaining_days * 4) // 1)
    if months >= 12:
        years += months // 12
        months %= 12

    # Tuổi làm tròn để hiển thị mốc (thường tính từ tuổi mụ hoặc tuổi tròn, tối thiểu là 1 tuổi)
    rounded_start_age = max(1, round(years + months / 12.0))

    info = {
        "direction": "Thuận" if is_forward else "Nghịch",
        "target_solar_term": target_jie_name,
        "delta_days": round(days_float, 2),
        "start_age_years": years,
        "start_age_months": months,
        "start_age_rounded": rounded_start_age,
        "display": f"{years} tuổi {months} tháng" if months > 0 else f"{years} tuổi",
    }

    # Bắt đầu tính dãy đại vận xuất phát từ trụ tháng
    current_stem_idx = STEMS.index(month_stem)
    current_branch_idx = BRANCHES.index(month_branch)

    step = 1 if is_forward else -1
    cycles: list[dict] = []

    birth_solar_year = birth_utc.year

    for i in range(1, num_cycles + 1):
        current_stem_idx = (current_stem_idx + step) % 10
        current_branch_idx = (current_branch_idx + step) % 12

        c_stem = STEMS[current_stem_idx]
        c_branch = BRANCHES[current_branch_idx]
        c_na_yin = NA_YIN.get((c_stem, c_branch), "")
        ten_god = get_ten_god(day_master_stem, c_stem)
        life_stage = get_life_stage(day_master_stem, c_branch, tu_mode)

        start_age = rounded_start_age + (i - 1) * 10
        end_age = start_age + 9
        calendar_year_start = birth_solar_year + start_age

        cycles.append({
            "step": i,
            "stem": c_stem,
            "branch": c_branch,
            "can_chi": f"{c_stem} {c_branch}",
            "element_stem": STEM_ELEMENTS[current_stem_idx],
            "element_branch": BRANCH_ELEMENTS[current_branch_idx],
            "ten_god": ten_god,
            "life_stage": life_stage,
            "na_yin": c_na_yin,
            "age_range": f"{start_age} - {end_age}",
            "start_age": start_age,
            "end_age": end_age,
            "calendar_year_start": calendar_year_start,
        })

    return info, cycles


def calculate_five_elements_count(pillars: list[dict]) -> dict[str, dict]:
    """Thống kê tỷ trọng ngũ hành từ Can, Chi và Tàng Can của 4 trụ."""
    counts = {"Kim": 0.0, "Mộc": 0.0, "Thủy": 0.0, "Hỏa": 0.0, "Thổ": 0.0}

    # 1. Điểm từ 4 Thiên Can: mỗi can 1.0 điểm
    for p in pillars:
        counts[p["stem_element"]] += 1.0

    # 2. Điểm từ Tàng Can trong 4 Địa Chi: phân bổ theo tỷ trọng khí
    for p in pillars:
        for hidden in p["hidden_stems"]:
            counts[hidden["element"]] += hidden["weight"]

    total = sum(counts.values()) or 1.0
    result = {}
    for elem, val in counts.items():
        pct = round((val / total) * 100, 1)
        result[elem] = {
            "score": round(val, 2),
            "percentage": pct,
        }
    return result


def evaluate_day_master_strength(
    day_master_stem: str,
    month_branch: str,
    five_elements: dict[str, dict],
) -> dict:
    """Đánh giá sơ bộ độ vượng suy của Nhật Can (Đắc lệnh, đắc địa, tương trợ)."""
    dm_elem = STEM_ELEMENTS[STEMS.index(day_master_stem)]
    month_elem = BRANCH_ELEMENTS[BRANCHES.index(month_branch)]

    # Mộc: sinh Dần, Mão; sinh tại Hợi; vượng tại Dần Mão
    # Đắc lệnh: Chi tháng cùng hành hoặc sinh cho nhật can
    is_produced = (ELEMENT_ORDER[(ELEMENT_ORDER.index(month_elem) + 1) % 5] == dm_elem)
    is_same = (month_elem == dm_elem)
    dack_lenh = is_same or is_produced

    # Điểm tương trợ từ đồng hành và ấn (sinh ra nhật can)
    producing_elem = ELEMENT_ORDER[(ELEMENT_ORDER.index(dm_elem) - 1) % 5]
    support_pct = five_elements[dm_elem]["percentage"] + five_elements[producing_elem]["percentage"]

    if support_pct >= 55.0 or (dack_lenh and support_pct >= 45.0):
        status = "Thân Vượng"
        desc = "Bản mệnh có năng lượng vững vàng, tự chủ, thích gánh vác việc lớn, hợp với Thực Thương, Tài, Quan Sát."
    elif support_pct <= 35.0 or ((not dack_lenh) and support_pct <= 42.0):
        status = "Thân Nhược"
        desc = "Bản mệnh cần thêm năng lượng tương trợ từ Tỷ Kiên và Chính Ấn/Thiên Ấn để bồi đắp khí lực và sự kiên trì."
    else:
        status = "Trung Hòa"
        desc = "Ngũ hành tương đối cân bằng, tính cách dung hòa, linh hoạt thích ứng với các biến chuyển của đại vận."

    return {
        "status": status,
        "dack_lenh": dack_lenh,
        "support_percentage": round(support_pct, 1),
        "description": desc,
    }


def calculate_bazi(
    full_name: str,
    gender: Literal["male", "female"],
    birth_date: date,
    birth_time: time | None,
    birth_place: str = "",
    zi_mode: Literal["next_day", "early_late"] = "next_day",
    tu_mode: Literal["fire", "water"] = "fire",
) -> dict:
    """Hàm tính toán toàn bộ lá số Bát Tự (Tứ Trụ).
    
    Tham số:
    - full_name: họ tên đầy đủ
    - gender: giới tính ('male' hoặc 'female')
    - birth_date: ngày sinh dương lịch
    - birth_time: giờ sinh (nếu None, mặc định 12:00 trưa và ghi chú trụ giờ)
    - birth_place: nơi sinh để xác định múi giờ lịch sử
    - zi_mode: quy ước giờ Tý ('next_day': 23h sang ngày mới; 'early_late': phân Dạ Tý & Tý sớm)
    - tu_mode: cách tính Tràng Sinh Mậu Kỷ ('fire': Hỏa Thổ đồng cung; 'water': Thủy Thổ đồng cung)
    """
    time_provided = (birth_time is not None)
    actual_time = birth_time if time_provided else time(12, 0)

    # 1. Chuyển đổi múi giờ lịch sử sang UTC
    birth_utc, tz_info = timezones.local_birth_to_utc(birth_date, actual_time, birth_place)

    # 2. Xử lý ranh giới Năm Bát Tự theo Lập Xuân
    bazi_year_val = solar_terms.get_bazi_year(birth_utc)
    year_stem_idx = (bazi_year_val - 4) % 10
    year_branch_idx = (bazi_year_val - 4) % 12
    year_stem = STEMS[year_stem_idx]
    year_branch = BRANCHES[year_branch_idx]

    # 3. Xử lý ranh giới Tháng Bát Tự theo 12 Tiết Khí
    month_num, month_branch_idx, prev_jie, next_jie = solar_terms.get_bazi_month_and_adjacent_jie(birth_utc)
    month_stem, month_branch = get_month_can_chi(year_stem, month_branch_idx)

    # 4. Xử lý Trụ Ngày (kèm kiểm tra Giờ Tý)
    calc_date = birth_date
    h = actual_time.hour
    m = actual_time.minute

    # Nếu sinh lúc 23:00 - 23:59:
    # - Nếu zi_mode == "next_day": đã sang ngày mới -> calc_date + 1 ngày
    # - Nếu zi_mode == "early_late": vẫn là ngày cũ
    is_late_zi = (h == 23)
    if is_late_zi and zi_mode == "next_day":
        calc_date = birth_date + timedelta(days=1)

    day_stem, day_branch, day_60_idx = get_day_can_chi(calc_date)

    # 5. Xử lý Trụ Giờ
    hour_branch_idx = get_hour_branch_idx(h, m)
    hour_branch = BRANCHES[hour_branch_idx]

    # Can giờ tính theo can ngày (nếu early_late và 23h thì can ngày gốc)
    hour_stem, _ = get_hour_can_chi(day_stem, hour_branch_idx)

    # 6. Chuẩn bị thông tin chi tiết từng trụ
    day_master = day_stem

    raw_pillars = [
        ("Năm", year_stem, year_branch, "year"),
        ("Tháng", month_stem, month_branch, "month"),
        ("Ngày", day_stem, day_branch, "day"),
        ("Giờ", hour_stem, hour_branch, "hour"),
    ]

    pillars_output = []
    for title, c_stem, c_branch, p_key in raw_pillars:
        stem_elem = STEM_ELEMENTS[STEMS.index(c_stem)]
        branch_elem = BRANCH_ELEMENTS[BRANCHES.index(c_branch)]
        stem_yy = STEM_YIN_YANG[STEMS.index(c_stem)]
        branch_yy = BRANCH_YIN_YANG[BRANCHES.index(c_branch)]
        na_yin = NA_YIN.get((c_stem, c_branch), "")
        life_stage = get_life_stage(day_master, c_branch, tu_mode)

        # Thập thần của Can
        ten_god = "Nhật Chủ" if p_key == "day" else get_ten_god(day_master, c_stem)

        # Tàng Can
        hidden_list = []
        for h_stem, h_type, h_weight in HIDDEN_STEMS[c_branch]:
            h_elem = STEM_ELEMENTS[STEMS.index(h_stem)]
            h_tg = get_ten_god(day_master, h_stem)
            hidden_list.append({
                "stem": h_stem,
                "type": h_type,
                "weight": h_weight,
                "element": h_elem,
                "ten_god": h_tg,
            })

        pillars_output.append({
            "key": p_key,
            "title": title,
            "stem": c_stem,
            "branch": c_branch,
            "can_chi": f"{c_stem} {c_branch}",
            "stem_element": stem_elem,
            "branch_element": branch_elem,
            "stem_yin_yang": stem_yy,
            "branch_yin_yang": branch_yy,
            "animal": BRANCH_ANIMALS[BRANCHES.index(c_branch)],
            "ten_god": ten_god,
            "life_stage": life_stage,
            "na_yin": na_yin,
            "hidden_stems": hidden_list,
        })

    # 7. Thần Sát
    stars_by_pillar = get_symbolic_stars(
        day_stem=day_stem,
        day_branch=day_branch,
        year_stem=year_stem,
        year_branch=year_branch,
        month_branch=month_branch,
        hour_branch=hour_branch,
        day_60_idx=day_60_idx,
    )

    for p in pillars_output:
        p["symbolic_stars"] = stars_by_pillar.get(p["key"], [])

    # 8. Đại Vận
    major_cycles_info, major_cycles = calculate_major_cycles(
        gender=gender,
        bazi_year_stem=year_stem,
        month_stem=month_stem,
        month_branch=month_branch,
        birth_utc=birth_utc,
        prev_jie=prev_jie,
        next_jie=next_jie,
        day_master_stem=day_master,
        tu_mode=tu_mode,
        num_cycles=8,
    )

    # 9. Thống kê Ngũ Hành & Độ vượng suy
    five_elements_count = calculate_five_elements_count(pillars_output)
    dm_evaluation = evaluate_day_master_strength(day_master, month_branch, five_elements_count)

    # Tùy chọn hiển thị
    options_desc = {
        "zi_hour_mode": "23h tính sang ngày mới (Nhất nhật tị Tý)" if zi_mode == "next_day" else "Phân Dạ Tý (23h-24h ngày cũ) & Tý sớm (0h-1h ngày mới)",
        "tu_life_stage_mode": "Hỏa Thổ đồng cung (Mậu sinh Dần, Kỷ sinh Dậu)" if tu_mode == "fire" else "Thủy Thổ đồng cung (Mậu sinh Thân, Kỷ sinh Mão)",
    }

    return {
        "full_name": full_name,
        "gender": gender,
        "birth_date": birth_date.isoformat(),
        "birth_time": birth_time.strftime("%H:%M") if birth_time else None,
        "time_provided": time_provided,
        "birth_place": birth_place,
        "day_master": {
            "stem": day_master,
            "element": STEM_ELEMENTS[STEMS.index(day_master)],
            "yin_yang": STEM_YIN_YANG[STEMS.index(day_master)],
            "strength": dm_evaluation,
        },
        "pillars": pillars_output,
        "major_cycles_info": major_cycles_info,
        "major_cycles": major_cycles,
        "five_elements": five_elements_count,
        "timezone_note": tz_info.note,
        "solar_term_info": {
            "prev_jie": {
                "name": prev_jie.name,
                "utc_time": prev_jie.utc_time.isoformat(),
            },
            "next_jie": {
                "name": next_jie.name,
                "utc_time": next_jie.utc_time.isoformat(),
            },
        },
        "options": options_desc,
    }
