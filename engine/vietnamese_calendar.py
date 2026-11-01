"""Chuyển đổi Dương lịch sang Âm lịch Việt Nam chuẩn xác thiên văn (Thuật toán Hồ Ngọc Đức).

Tính toán sóc (New Moon) và trung khí theo kinh tuyến 105°E (Múi giờ UTC+7 - Giờ chuẩn Việt Nam).
Xác định chính xác ngày, tháng, năm âm lịch, tháng nhuận và Can Chi cho 4 trụ (Năm, Tháng, Ngày, Giờ).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, time

PI = math.pi

# 10 Thiên Can
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
STEM_ELEMENTS = ["Mộc", "Mộc", "Hỏa", "Hỏa", "Thổ", "Thổ", "Kim", "Kim", "Thủy", "Thủy"]
STEM_YIN_YANG = ["Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm"]

# 12 Địa Chi
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
BRANCH_ELEMENTS = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa", "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]
BRANCH_YIN_YANG = ["Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm"]
BRANCH_ANIMALS = ["Chuột", "Trâu", "Hổ", "Mèo", "Rồng", "Rắn", "Ngựa", "Dê", "Khỉ", "Gà", "Chó", "Lợn"]

# 60 Hoa Giáp Nạp Âm
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


def jd_from_date(day: int, month: int, year: int) -> int:
    """Tính Julian Day Number từ ngày/tháng/năm Dương lịch tại 12h trưa."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045


def jd_to_date(jd: int) -> tuple[int, int, int]:
    """Chuyển Julian Day Number sang ngày/tháng/năm Dương lịch."""
    a = jd + 32044
    b = (4 * a + 3) // 146097
    c = a - ((146097 * b) // 4)
    d = (4 * c + 3) // 1461
    e = c - ((1461 * d) // 4)
    m = (5 * e + 2) // 153
    day = e - ((153 * m + 2) // 5) + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + (m // 10)
    return day, month, year


def get_new_moon_day(k: int, time_zone: float = 7.0) -> int:
    """Tính ngày sóc (New Moon) thứ k tính từ sóc đầu năm 1900."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = PI / 180.0
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mprime = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 -= 0.4068 * math.sin(Mprime * dr) + 0.0161 * math.sin(2 * dr * Mprime)
    C1 -= 0.0004 * math.sin(3 * dr * Mprime)
    C1 += 0.0104 * math.sin(2 * dr * F) - 0.0051 * math.sin((M + Mprime) * dr)
    C1 -= 0.0074 * math.sin((M - Mprime) * dr) + 0.0004 * math.sin((2 * F + M) * dr)
    C1 -= 0.0004 * math.sin((2 * F - M) * dr) - 0.0006 * math.sin((2 * F + Mprime) * dr)
    C1 += 0.0010 * math.sin((2 * F - Mprime) * dr) + 0.0005 * math.sin((2 * Mprime + M) * dr)
    if T < -11:
        deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        deltat = -0.000078 + 0.000099 * T + 0.00000057 * T2
    JdNew = Jd1 + C1 - deltat
    return int(JdNew + 0.5 + time_zone / 24.0)


def get_sun_longitude(jdn: int, time_zone: float = 7.0) -> int:
    """Tính kinh độ mặt trời tại thời điểm nửa đêm (tính theo số nguyên từ 0 đến 11)."""
    T = (jdn - 0.5 - time_zone / 24.0 - 2451545.0) / 36525.0
    T2 = T * T
    dr = PI / 180.0
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = L0 + DL
    L = L * dr
    L = L - 2 * PI * int(L / (2 * PI))
    return int(L / (PI / 6))


def get_lunar_month_11(yy: int, time_zone: float = 7.0) -> int:
    """Tìm ngày bắt đầu tháng 11 âm lịch của năm Dương lịch yy."""
    off = jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = get_new_moon_day(k, time_zone)
    sun_long = get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11: int, time_zone: float = 7.0) -> int:
    """Tìm xem tháng nhuận là tháng thứ mấy sau tháng 11 âm lịch của năm trước."""
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)
    while True:
        last = arc
        i += 1
        arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)
        if arc == last or i >= 14:
            break
    return i - 1


def solar_to_lunar(day: int, month: int, year: int, time_zone: float = 7.0) -> tuple[int, int, int, bool]:
    """Chuyển ngày Dương lịch sang Âm lịch Việt Nam (ngày, tháng, năm, có phải tháng nhuận không)."""
    day_number = jd_from_date(day, month, year)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = get_new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = get_new_moon_day(k, time_zone)
    a11 = get_lunar_month_11(year, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = get_lunar_month_11(year - 1, time_zone)
    else:
        lunar_year = year + 1
        b11 = get_lunar_month_11(year + 1, time_zone)
    lunar_day = day_number - month_start + 1
    diff = int((month_start - a11) / 29)
    lunar_leap = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_day, lunar_month, lunar_year, lunar_leap


@dataclass(frozen=True)
class LunarDate:
    day: int
    month: int
    year: int
    is_leap: bool
    stem_year: str
    branch_year: str
    stem_month: str
    branch_month: str
    stem_day: str
    branch_day: str
    stem_hour: str
    branch_hour: str
    na_yin_year: str
    yin_yang_year: str  # "Dương" hoặc "Âm"


def get_hour_branch_index(t: time | None, zi_mode: str = "next_day") -> int:
    """Xác định chi giờ sinh (0=Tý, 1=Sửu, ..., 11=Hợi).

    Mặc định: 23h - 0h59 là giờ Tý.
    Nếu zi_mode == "next_day", 23h đã tính sang giờ Tý của ngày hôm sau.
    """
    if t is None:
        return 0  # mặc định giờ Tý nếu không có giờ sinh
    hour = t.hour
    minute = t.minute
    total_minutes = hour * 60 + minute

    # 23h00 (1380m) đến 00h59 (59m) là giờ Tý
    if total_minutes >= 1380 or total_minutes < 60:
        return 0  # Tý
    # Từ 1h00 trở đi, mỗi 2 tiếng là 1 canh giờ
    return ((total_minutes + 60) // 120) % 12


def calculate_lunar_info(
    solar_d: date,
    solar_t: time | None = None,
    time_zone: float = 7.0,
    zi_mode: str = "next_day",
) -> LunarDate:
    """Tính toán đầy đủ thông tin Âm lịch và Can Chi cho ngày giờ sinh."""
    # Xử lý giờ Tý (23h - 24h)
    target_date = solar_d
    hour_branch_idx = get_hour_branch_index(solar_t, zi_mode)

    if solar_t is not None and solar_t.hour >= 23 and zi_mode == "next_day":
        # Từ 23h đã sang ngày mới theo chuẩn phong thủy / Tử Vi
        target_date = date.fromordinal(solar_d.toordinal() + 1)

    lunar_day, lunar_month, lunar_year, is_leap = solar_to_lunar(
        target_date.day, target_date.month, target_date.year, time_zone
    )

    # 1. Can Chi Năm Âm Lịch
    stem_year_idx = (lunar_year + 6) % 10
    branch_year_idx = (lunar_year + 8) % 12
    stem_year = STEMS[stem_year_idx]
    branch_year = BRANCHES[branch_year_idx]
    yin_yang_year = STEM_YIN_YANG[stem_year_idx]
    na_yin_year = NA_YIN.get((stem_year, branch_year), "Không rõ")

    # 2. Can Chi Tháng Âm Lịch
    # Chi tháng âm lịch là cố định: tháng 1 là Dần (2), tháng 2 là Mão (3)...
    branch_month_idx = (lunar_month + 1) % 12
    branch_month = BRANCHES[branch_month_idx]
    # Can tháng theo Ngũ Hổ Độn: khởi từ tháng Dần
    start_month_stem = ((stem_year_idx % 5) * 2 + 2) % 10
    stem_month_idx = (start_month_stem + (lunar_month - 1)) % 10
    stem_month = STEMS[stem_month_idx]

    # 3. Can Chi Ngày
    jdn = jd_from_date(target_date.day, target_date.month, target_date.year)
    idx_60_day = (jdn + 49) % 60
    stem_day_idx = idx_60_day % 10
    branch_day_idx = idx_60_day % 12
    stem_day = STEMS[stem_day_idx]
    branch_day = BRANCHES[branch_day_idx]

    # 4. Can Chi Giờ (theo Ngũ Thử Độn)
    start_hour_stem = ((stem_day_idx % 5) * 2) % 10
    stem_hour_idx = (start_hour_stem + hour_branch_idx) % 10
    stem_hour = STEMS[stem_hour_idx]
    branch_hour = BRANCHES[hour_branch_idx]

    return LunarDate(
        day=lunar_day,
        month=lunar_month,
        year=lunar_year,
        is_leap=is_leap,
        stem_year=stem_year,
        branch_year=branch_year,
        stem_month=stem_month,
        branch_month=branch_month,
        stem_day=stem_day,
        branch_day=branch_day,
        stem_hour=stem_hour,
        branch_hour=branch_hour,
        na_yin_year=na_yin_year,
        yin_yang_year=yin_yang_year,
    )
