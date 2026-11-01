"""Tính toán 24 Tiết Khí thiên văn chính xác dùng PyEphem.

Mỗi tiết khí ứng với một góc kinh độ hoàng đạo biểu kiến của Mặt Trời (apparent ecliptic longitude):
- 12 Tiết (Jie): dùng phân định tháng Bát Tự và tính khởi Đại Vận:
    Lập Xuân  (315°): bắt đầu tháng Dần (tháng 1 Bát Tự) và ranh giới năm Bát Tự
    Kinh Trập (345°): bắt đầu tháng Mão (tháng 2)
    Thanh Minh (15°): bắt đầu tháng Thìn (tháng 3)
    Lập Hạ     (45°): bắt đầu tháng Tị (tháng 4)
    Mang Chủng (75°): bắt đầu tháng Ngọ (tháng 5)
    Tiểu Thử  (105°): bắt đầu tháng Mùi (tháng 6)
    Lập Thu   (135°): bắt đầu tháng Thân (tháng 7)
    Bạch Lộ   (165°): bắt đầu tháng Dậu (tháng 8)
    Hàn Lộ    (195°): bắt đầu tháng Tuất (tháng 9)
    Lập Đông  (225°): bắt đầu tháng Hợi (tháng 10)
    Đại Tuyết (255°): bắt đầu tháng Tý (tháng 11)
    Tiểu Hàn  (285°): bắt đầu tháng Sửu (tháng 12)

- 12 Trung Khí (Zhongqi):
    Vũ Thủy (330°), Xuân Phân (0°), Cốc Vũ (30°), Tiểu Mãn (60°), Hạ Chí (90°), Đại Thử (120°),
    Xử Thử (150°), Thu Phân (180°), Sương Giáng (210°), Tiểu Tuyết (240°), Đông Chí (270°), Đại Hàn (300°).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import ephem

# Danh sách 24 tiết khí theo thứ tự bắt đầu từ Xuân Phân (0°)
SOLAR_TERMS_ALL = [
    ("Xuân Phân", 0, False),
    ("Cốc Vũ", 30, False),
    ("Lập Hạ", 45, True),
    ("Tiểu Mãn", 60, False),
    ("Mang Chủng", 75, True),
    ("Hạ Chí", 90, False),
    ("Tiểu Thử", 105, True),
    ("Đại Thử", 120, False),
    ("Lập Thu", 135, True),
    ("Xử Thử", 150, False),
    ("Bạch Lộ", 165, True),
    ("Thu Phân", 180, False),
    ("Hàn Lộ", 195, True),
    ("Sương Giáng", 210, False),
    ("Lập Đông", 225, True),
    ("Tiểu Tuyết", 240, False),
    ("Đại Tuyết", 255, True),
    ("Đông Chí", 270, False),
    ("Tiểu Hàn", 285, True),
    ("Đại Hàn", 300, False),
    ("Lập Xuân", 315, True),
    ("Vũ Thủy", 330, False),
    ("Kinh Trập", 345, True),
    ("Thanh Minh", 15, True),
]

# 12 Tiết phân định tháng Bát Tự (theo thứ tự tháng 1 -> 12 Bát Tự, tức Dần -> Sửu)
# (Tên, Góc hoàng đạo, Tháng Bát tự 1..12, Chi tháng 0..11 với Tý=0, Sửu=1, Dần=2...)
JIE_TERMS = [
    ("Lập Xuân", 315, 1, 2),    # Tháng Dần
    ("Kinh Trập", 345, 2, 3),   # Tháng Mão
    ("Thanh Minh", 15, 3, 4),   # Tháng Thìn
    ("Lập Hạ", 45, 4, 5),       # Tháng Tị
    ("Mang Chủng", 75, 5, 6),   # Tháng Ngọ
    ("Tiểu Thử", 105, 6, 7),    # Tháng Mùi
    ("Lập Thu", 135, 7, 8),     # Tháng Thân
    ("Bạch Lộ", 165, 8, 9),     # Tháng Dậu
    ("Hàn Lộ", 195, 9, 10),     # Tháng Tuất
    ("Lập Đông", 225, 10, 11),  # Tháng Hợi
    ("Đại Tuyết", 255, 11, 0),  # Tháng Tý
    ("Tiểu Hàn", 285, 12, 1),   # Tháng Sửu
]


@dataclass(frozen=True)
class SolarTermEvent:
    name: str
    target_deg: int
    is_jie: bool
    utc_time: datetime
    month_num: int | None = None  # 1..12 nếu là Tiết
    branch_idx: int | None = None  # 0..11 nếu là Tiết


def get_apparent_solar_longitude_deg(dt_utc: datetime) -> float:
    """Tính kinh độ hoàng đạo biểu kiến của Mặt Trời tại thời điểm UTC (tọa độ equinox of date)."""
    # Chuyển sang định dạng của ephem (YYYY/MM/DD HH:MM:SS)
    ephem_date = ephem.Date(dt_utc.strftime("%Y/%m/%d %H:%M:%S"))
    sun = ephem.Sun()
    sun.compute(ephem_date)
    ecl = ephem.Ecliptic(sun, epoch=ephem_date)
    deg = float(ecl.lon) * 180.0 / math.pi
    return deg % 360.0


_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _dt_to_seconds(dt: datetime) -> float:
    """Chuyển datetime UTC sang số giây từ epoch (an toàn trên Windows cho cả năm trước 1970)."""
    return (dt - _EPOCH).total_seconds()


def _seconds_to_dt(sec: float) -> datetime:
    """Chuyển số giây từ epoch sang datetime UTC (an toàn trên Windows cho cả năm trước 1970)."""
    return _EPOCH + timedelta(seconds=sec)


def _find_exact_term_time(rough_dt_utc: datetime, target_deg: float) -> datetime:
    """Tìm thời điểm chính xác khi kinh độ biểu kiến của Mặt Trời đạt target_deg bằng phương pháp chia đôi (Bisection)."""
    target_rad = math.radians(target_deg)

    # Tìm khoảng thời gian quanh rough_dt_utc (+- 3 ngày)
    t_low = _dt_to_seconds(rough_dt_utc - timedelta(days=3))
    t_high = _dt_to_seconds(rough_dt_utc + timedelta(days=3))

    def diff_rad(ts: float) -> float:
        dt = _seconds_to_dt(ts)
        ephem_d = ephem.Date(dt.strftime("%Y/%m/%d %H:%M:%S"))
        sun = ephem.Sun()
        sun.compute(ephem_d)
        lon_rad = float(ephem.Ecliptic(sun, epoch=ephem_d).lon)
        # Hiệu số góc trong khoảng [-pi, pi]
        d = (lon_rad - target_rad + math.pi) % (2 * math.pi) - math.pi
        return d

    # 28 lần chia đôi cho độ chính xác dưới 0.1 giây
    for _ in range(28):
        t_mid = (t_low + t_high) / 2.0
        d = diff_rad(t_mid)
        if d < 0:
            t_low = t_mid
        else:
            t_high = t_mid

    best_ts = (t_low + t_high) / 2.0
    return _seconds_to_dt(best_ts)


# Ngày xấp xỉ trong năm dương lịch cho 24 tiết khí (tháng, ngày)
_ROUGH_DATES = {
    "Xuân Phân": (3, 20),
    "Cốc Vũ": (4, 20),
    "Lập Hạ": (5, 5),
    "Tiểu Mãn": (5, 21),
    "Mang Chủng": (6, 5),
    "Hạ Chí": (6, 21),
    "Tiểu Thử": (7, 7),
    "Đại Thử": (7, 23),
    "Lập Thu": (8, 7),
    "Xử Thử": (8, 23),
    "Bạch Lộ": (9, 7),
    "Thu Phân": (9, 23),
    "Hàn Lộ": (10, 8),
    "Sương Giáng": (10, 23),
    "Lập Đông": (11, 7),
    "Tiểu Tuyết": (11, 22),
    "Đại Tuyết": (12, 7),
    "Đông Chí": (12, 21),
    "Tiểu Hàn": (1, 5),
    "Đại Hàn": (1, 20),
    "Lập Xuân": (2, 4),
    "Vũ Thủy": (2, 19),
    "Kinh Trập": (3, 5),
    "Thanh Minh": (4, 4),
}


def get_solar_term_time(year: int, term_name: str) -> datetime:
    """Lấy thời điểm chính xác (UTC) của một tiết khí trong năm dương lịch `year`."""
    target_deg = None
    for name, deg, _ in SOLAR_TERMS_ALL:
        if name == term_name:
            target_deg = deg
            break
    if target_deg is None:
        raise ValueError(f"Không tìm thấy tiết khí: {term_name}")

    m, d = _ROUGH_DATES[term_name]
    rough_dt = datetime(year, m, d, 12, 0, tzinfo=timezone.utc)
    return _find_exact_term_time(rough_dt, float(target_deg))


def get_all_jie_terms_for_bazi(year: int) -> list[SolarTermEvent]:
    """Trả về 12 Tiết khí của năm Bát Tự bắt đầu từ Lập Xuân năm `year` đến trước Lập Xuân năm `year + 1`.
    
    Lưu ý: Tiểu Hàn (tháng 12 Bát Tự) nằm ở đầu tháng 1 của năm dương lịch `year + 1`.
    """
    events: list[SolarTermEvent] = []
    for name, deg, month_num, branch_idx in JIE_TERMS:
        # Nếu là Tiểu Hàn thì nằm ở tháng 1 năm sau (year + 1)
        term_year = year + 1 if name == "Tiểu Hàn" else year
        dt_utc = get_solar_term_time(term_year, name)
        events.append(SolarTermEvent(
            name=name,
            target_deg=deg,
            is_jie=True,
            utc_time=dt_utc,
            month_num=month_num,
            branch_idx=branch_idx,
        ))
    events.sort(key=lambda e: e.utc_time)
    return events


def get_bazi_month_and_adjacent_jie(dt_utc: datetime) -> tuple[int, int, SolarTermEvent, SolarTermEvent]:
    """Xác định tháng Bát Tự (1..12), chi tháng (0..11 với Tý=0, Sửu=1, Dần=2...), và 2 Tiết khí liền kề (trước và sau) cho thời điểm dt_utc.
    
    Trả về:
        (month_num, branch_idx, prev_jie, next_jie)
        - month_num: 1 (Dần) .. 12 (Sửu)
        - branch_idx: 0 (Tý) .. 11 (Hợi)
        - prev_jie: Tiết khí vừa bước vào trước đó (dùng tính tuổi đại vận nghịch hành)
        - next_jie: Tiết khí sắp tới (dùng tính tuổi đại vận thuận hành)
    """
    year = dt_utc.year
    # Lấy danh sách Tiết khí của 3 năm liền kề (year-1, year, year+1) để bao quát biên giới
    all_jies: list[SolarTermEvent] = []
    for y in (year - 1, year, year + 1):
        all_jies.extend(get_all_jie_terms_for_bazi(y))
    all_jies.sort(key=lambda e: e.utc_time)

    # Tìm Tiết khí ngay trước dt_utc
    prev_jie: SolarTermEvent | None = None
    next_jie: SolarTermEvent | None = None

    for i in range(len(all_jies) - 1):
        if all_jies[i].utc_time <= dt_utc < all_jies[i + 1].utc_time:
            prev_jie = all_jies[i]
            next_jie = all_jies[i + 1]
            break

    if prev_jie is None or next_jie is None:
        # Fallback nếu ở rìa dải thời gian
        prev_jie = all_jies[0]
        next_jie = all_jies[1]

    assert prev_jie.month_num is not None
    assert prev_jie.branch_idx is not None
    return prev_jie.month_num, prev_jie.branch_idx, prev_jie, next_jie


def get_bazi_year(dt_utc: datetime) -> int:
    """Xác định năm Bát Tự (tính theo tiết Lập Xuân của năm).
    
    Nếu sinh trước Lập Xuân của năm dương lịch `dt_utc.year`, thì thuộc năm Bát Tự `dt_utc.year - 1`.
    Ngược lại, thuộc năm Bát Tự `dt_utc.year`.
    """
    lichun_this_year = get_solar_term_time(dt_utc.year, "Lập Xuân")
    if dt_utc < lichun_this_year:
        return dt_utc.year - 1
    return dt_utc.year
