"""Module tính toán Bản Đồ Sao Chiêm Tinh Tây Phương (Natal Chart).

Tính toán:
- Tọa độ hoàng đạo biểu kiến 10 hành tinh + Chiron + North/South Node + ASC, MC, DSC, IC.
- Trạng thái nghịch hành (Retrograde Rx).
- 12 Cung Hoàng Đạo & 4 Nguyên Tố (Lửa, Đất, Khí, Nước), 3 Tính Chất (Tiên Phong, Kiên Định, Linh Hoạt).
- 12 Nhà theo các hệ thống: Placidus (mặc định), Whole Sign, Equal House.
- Các góc chiếu kinh điển (Aspects): Trùng tụ 0°, Lục hợp 60°, Vuông góc 90°, Tam hợp 120°, Đối đỉnh 180°.
- Bảng phân bổ năng lượng Nguyên Tố và Tính Chất.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timezone, timedelta
from typing import Literal

import ephem

import geocoding
import timezones

# 12 Cung Hoàng Đạo
ZODIAC_SIGNS = [
    {
        "id": "aries", "name": "Bạch Dương", "latin": "Aries", "symbol": "♈",
        "element": "Fire", "element_vn": "Lửa",
        "modality": "Cardinal", "modality_vn": "Tiên phong",
        "ruler": "MARS", "start_deg": 0, "end_deg": 30,
        "color": "#ef4444"
    },
    {
        "id": "taurus", "name": "Kim Ngưu", "latin": "Taurus", "symbol": "♉",
        "element": "Earth", "element_vn": "Đất",
        "modality": "Fixed", "modality_vn": "Kiên định",
        "ruler": "VENUS", "start_deg": 30, "end_deg": 60,
        "color": "#10b981"
    },
    {
        "id": "gemini", "name": "Song Tử", "latin": "Gemini", "symbol": "♊",
        "element": "Air", "element_vn": "Khí",
        "modality": "Mutable", "modality_vn": "Linh hoạt",
        "ruler": "MERCURY", "start_deg": 60, "end_deg": 90,
        "color": "#f59e0b"
    },
    {
        "id": "cancer", "name": "Cự Giải", "latin": "Cancer", "symbol": "♋",
        "element": "Water", "element_vn": "Nước",
        "modality": "Cardinal", "modality_vn": "Tiên phong",
        "ruler": "MOON", "start_deg": 90, "end_deg": 120,
        "color": "#3b82f6"
    },
    {
        "id": "leo", "name": "Sư Tử", "latin": "Leo", "symbol": "♌",
        "element": "Fire", "element_vn": "Lửa",
        "modality": "Fixed", "modality_vn": "Kiên định",
        "ruler": "SUN", "start_deg": 120, "end_deg": 150,
        "color": "#ef4444"
    },
    {
        "id": "virgo", "name": "Xử Nữ", "latin": "Virgo", "symbol": "♍",
        "element": "Earth", "element_vn": "Đất",
        "modality": "Mutable", "modality_vn": "Linh hoạt",
        "ruler": "MERCURY", "start_deg": 150, "end_deg": 180,
        "color": "#10b981"
    },
    {
        "id": "libra", "name": "Thiên Bình", "latin": "Libra", "symbol": "♎",
        "element": "Air", "element_vn": "Khí",
        "modality": "Cardinal", "modality_vn": "Tiên phong",
        "ruler": "VENUS", "start_deg": 180, "end_deg": 210,
        "color": "#f59e0b"
    },
    {
        "id": "scorpio", "name": "Bọ Cạp", "latin": "Scorpio", "symbol": "♏",
        "element": "Water", "element_vn": "Nước",
        "modality": "Fixed", "modality_vn": "Kiên định",
        "ruler": "PLUTO", "start_deg": 210, "end_deg": 240,
        "color": "#3b82f6"
    },
    {
        "id": "sagittarius", "name": "Nhân Mã", "latin": "Sagittarius", "symbol": "♐",
        "element": "Fire", "element_vn": "Lửa",
        "modality": "Mutable", "modality_vn": "Linh hoạt",
        "ruler": "JUPITER", "start_deg": 240, "end_deg": 270,
        "color": "#ef4444"
    },
    {
        "id": "capricorn", "name": "Ma Kết", "latin": "Capricorn", "symbol": "♑",
        "element": "Earth", "element_vn": "Đất",
        "modality": "Cardinal", "modality_vn": "Tiên phong",
        "ruler": "SATURN", "start_deg": 270, "end_deg": 300,
        "color": "#10b981"
    },
    {
        "id": "aquarius", "name": "Bảo Bình", "latin": "Aquarius", "symbol": "♒",
        "element": "Air", "element_vn": "Khí",
        "modality": "Fixed", "modality_vn": "Kiên định",
        "ruler": "URANUS", "start_deg": 300, "end_deg": 330,
        "color": "#f59e0b"
    },
    {
        "id": "pisces", "name": "Song Ngư", "latin": "Pisces", "symbol": "♓",
        "element": "Water", "element_vn": "Nước",
        "modality": "Mutable", "modality_vn": "Linh hoạt",
        "ruler": "NEPTUNE", "start_deg": 330, "end_deg": 360,
        "color": "#3b82f6"
    },
]

# Thông tin 10 Hành Tinh & Thiên Thể
PLANET_METADATA = {
    "SUN": {"name": "Mặt Trời", "symbol": "☉", "category": "luminary"},
    "MOON": {"name": "Mặt Trăng", "symbol": "☽", "category": "luminary"},
    "MERCURY": {"name": "Thủy Tinh", "symbol": "☿", "category": "personal"},
    "VENUS": {"name": "Kim Tinh", "symbol": "♀", "category": "personal"},
    "MARS": {"name": "Hỏa Tinh", "symbol": "♂", "category": "personal"},
    "JUPITER": {"name": "Mộc Tinh", "symbol": "♃", "category": "social"},
    "SATURN": {"name": "Thổ Tinh", "symbol": "♄", "category": "social"},
    "URANUS": {"name": "Thiên Vương Tinh", "symbol": "♅", "category": "transpersonal"},
    "NEPTUNE": {"name": "Hải Vương Tinh", "symbol": "♆", "category": "transpersonal"},
    "PLUTO": {"name": "Diêm Vương Tinh", "symbol": "♇", "category": "transpersonal"},
    "NORTH_NODE": {"name": "La Hầu (North Node)", "symbol": "☊", "category": "node"},
    "SOUTH_NODE": {"name": "Kế Đô (South Node)", "symbol": "☋", "category": "node"},
    "CHIRON": {"name": "Chiron", "symbol": "⚷", "category": "asteroid"},
    "ASC": {"name": "Cung Mọc (Ascendant)", "symbol": "AC", "category": "angle"},
    "MC": {"name": "Thiên Đỉnh (Midheaven)", "symbol": "MC", "category": "angle"},
    "DSC": {"name": "Cung Lặn (Descendant)", "symbol": "DC", "category": "angle"},
    "IC": {"name": "Thiên Đế (Imum Coeli)", "symbol": "IC", "category": "angle"},
}

# Thông số 5 Góc Chiếu Chính (Major Ptolemaic Aspects)
ASPECT_DEFINITIONS = [
    {"name": "Trùng tụ", "latin": "Conjunction", "symbol": "☌", "angle": 0.0, "orb_default": 8.0, "orb_luminary": 10.0, "nature": "neutral", "color": "#8b5cf6"},
    {"name": "Lục hợp", "latin": "Sextile", "symbol": "⚹", "angle": 60.0, "orb_default": 6.0, "orb_luminary": 6.0, "nature": "harmonious", "color": "#10b981"},
    {"name": "Vuông góc", "latin": "Square", "symbol": "□", "angle": 90.0, "orb_default": 8.0, "orb_luminary": 8.0, "nature": "challenging", "color": "#ef4444"},
    {"name": "Tam hợp", "latin": "Trine", "symbol": "△", "angle": 120.0, "orb_default": 8.0, "orb_luminary": 8.0, "nature": "harmonious", "color": "#3b82f6"},
    {"name": "Đối đỉnh", "latin": "Opposition", "symbol": "☍", "angle": 180.0, "orb_default": 8.0, "orb_luminary": 10.0, "nature": "challenging", "color": "#dc2626"},
]

CHIRON_DB_LINE = "Chiron,e,6.9341,209.339,339.634,13.689,0.0135,0.3813,38.16,01/01.0/2000,2000,6.5,0.15"


def deg_to_zodiac(lon_deg: float) -> dict:
    """Quy đổi kinh độ hoàng đạo (0..360°) sang Cung Hoàng Đạo, độ, phút, giây."""
    lon = lon_deg % 360.0
    sign_idx = int(lon // 30)
    sign_info = ZODIAC_SIGNS[sign_idx]

    deg_in_sign = lon % 30.0
    deg = int(deg_in_sign)
    rem_min = (deg_in_sign - deg) * 60.0
    minute = int(rem_min)
    second = int((rem_min - minute) * 60.0)

    formatted = f"{deg}°{minute:02d}' {sign_info['name']}"
    formatted_short = f"{deg}°{sign_info['symbol']}{minute:02d}'"

    return {
        "longitude": round(lon, 4),
        "sign_id": sign_info["id"],
        "sign_name": sign_info["name"],
        "sign_latin": sign_info["latin"],
        "sign_symbol": sign_info["symbol"],
        "sign_element": sign_info["element"],
        "sign_element_vn": sign_info["element_vn"],
        "sign_modality": sign_info["modality"],
        "sign_modality_vn": sign_info["modality_vn"],
        "sign_color": sign_info["color"],
        "degrees": deg,
        "minutes": minute,
        "seconds": second,
        "formatted": formatted,
        "formatted_short": formatted_short,
    }


def calculate_mean_lunar_node(jd: float) -> float:
    """Tính kinh độ hoàng đạo của Điểm giao hội Mặt Trăng (Mean North Node / La Hầu) theo công thức thiên văn Jean Meeus."""
    t = (jd - 2451545.0) / 36525.0
    omega = 125.04452 - 1934.136261 * t + 0.0020708 * (t ** 2) + (t ** 3) / 450000.0
    return omega % 360.0


def _get_planet_ecliptic_lon(body, obs: ephem.Observer) -> float:
    """Lấy kinh độ hoàng đạo biểu kiến của thiên thể body tại observer obs."""
    body.compute(obs)
    ecl = ephem.Ecliptic(body, epoch=obs.date)
    return math.degrees(float(ecl.lon)) % 360.0


def calculate_planet_positions(birth_utc: datetime, lat: float, lon: float) -> dict[str, dict]:
    """Tính toán kinh độ hoàng đạo và trạng thái nghịch hành của 10 hành tinh, North/South Node và Chiron."""
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.elevation = 0
    obs.date = birth_utc.strftime("%Y/%m/%d %H:%M:%S")

    # Observer lệch +- 2 giờ để kiểm tra chiều chuyển động (nghịch hành Rx)
    obs_prev = ephem.Observer()
    obs_prev.lat, obs_prev.lon = str(lat), str(lon)
    obs_prev.date = (birth_utc - timedelta(hours=2)).strftime("%Y/%m/%d %H:%M:%S")

    obs_next = ephem.Observer()
    obs_next.lat, obs_next.lon = str(lat), str(lon)
    obs_next.date = (birth_utc + timedelta(hours=2)).strftime("%Y/%m/%d %H:%M:%S")

    bodies_map = {
        "SUN": ephem.Sun(),
        "MOON": ephem.Moon(),
        "MERCURY": ephem.Mercury(),
        "VENUS": ephem.Venus(),
        "MARS": ephem.Mars(),
        "JUPITER": ephem.Jupiter(),
        "SATURN": ephem.Saturn(),
        "URANUS": ephem.Uranus(),
        "NEPTUNE": ephem.Neptune(),
        "PLUTO": ephem.Pluto(),
    }

    chiron = ephem.readdb(CHIRON_DB_LINE)
    chiron_prev = ephem.readdb(CHIRON_DB_LINE)
    chiron_next = ephem.readdb(CHIRON_DB_LINE)

    positions: dict[str, dict] = {}

    for code, body in bodies_map.items():
        curr_lon = _get_planet_ecliptic_lon(body, obs)
        prev_lon = _get_planet_ecliptic_lon(body, obs_prev)
        next_lon = _get_planet_ecliptic_lon(body, obs_next)

        # Tính hiệu số góc giữa next và prev có tính chu kỳ 360°
        diff = (next_lon - prev_lon + 180.0) % 360.0 - 180.0
        # Mặt Trời và Mặt Trăng không bao giờ nghịch hành
        is_rx = (diff < 0) if code not in ("SUN", "MOON") else False

        z_info = deg_to_zodiac(curr_lon)
        meta = PLANET_METADATA[code]
        positions[code] = {
            "code": code,
            "name": meta["name"],
            "symbol": meta["symbol"],
            "category": meta["category"],
            "longitude": z_info["longitude"],
            "zodiac": z_info,
            "is_retrograde": is_rx,
        }

    # Chiron
    chiron_lon = _get_planet_ecliptic_lon(chiron, obs)
    chiron_prev_lon = _get_planet_ecliptic_lon(chiron_prev, obs_prev)
    chiron_next_lon = _get_planet_ecliptic_lon(chiron_next, obs_next)
    c_diff = (chiron_next_lon - chiron_prev_lon + 180.0) % 360.0 - 180.0
    chiron_rx = (c_diff < 0)
    c_zodiac = deg_to_zodiac(chiron_lon)
    c_meta = PLANET_METADATA["CHIRON"]
    positions["CHIRON"] = {
        "code": "CHIRON",
        "name": c_meta["name"],
        "symbol": c_meta["symbol"],
        "category": c_meta["category"],
        "longitude": c_zodiac["longitude"],
        "zodiac": c_zodiac,
        "is_retrograde": chiron_rx,
    }

    # Lunar Nodes (La Hầu / Kế Đô)
    jd = ephem.julian_date(obs.date)
    node_lon = calculate_mean_lunar_node(jd)
    south_node_lon = (node_lon + 180.0) % 360.0

    nn_zodiac = deg_to_zodiac(node_lon)
    sn_zodiac = deg_to_zodiac(south_node_lon)

    positions["NORTH_NODE"] = {
        "code": "NORTH_NODE",
        "name": PLANET_METADATA["NORTH_NODE"]["name"],
        "symbol": PLANET_METADATA["NORTH_NODE"]["symbol"],
        "category": PLANET_METADATA["NORTH_NODE"]["category"],
        "longitude": nn_zodiac["longitude"],
        "zodiac": nn_zodiac,
        "is_retrograde": True,  # Mean node luôn chuyển động lùi
    }

    positions["SOUTH_NODE"] = {
        "code": "SOUTH_NODE",
        "name": PLANET_METADATA["SOUTH_NODE"]["name"],
        "symbol": PLANET_METADATA["SOUTH_NODE"]["symbol"],
        "category": PLANET_METADATA["SOUTH_NODE"]["category"],
        "longitude": sn_zodiac["longitude"],
        "zodiac": sn_zodiac,
        "is_retrograde": True,
    }

    return positions


def calculate_angles_and_houses(
    birth_utc: datetime,
    lat: float,
    lon: float,
    house_system: Literal["placidus", "whole_sign", "equal"] = "placidus",
) -> tuple[dict[str, dict], dict[int, dict]]:
    """Tính toán 4 trục (ASC, MC, DSC, IC) và 12 Nhà hoàng đạo theo hệ thống nhà chỉ định."""
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.elevation = 0
    obs.date = birth_utc.strftime("%Y/%m/%d %H:%M:%S")

    # Giờ thiên văn địa phương (Local Sidereal Time / RAMC) tính bằng radians
    theta = float(obs.sidereal_time())
    # Độ nghiêng hoàng đạo (true obliquity of ecliptic)
    eps = math.radians(23.4392911)

    phi = math.radians(lat)

    # 1. Thiên Đỉnh (MC - Midheaven, Đỉnh Nhà 10)
    # tan(MC) = tan(theta) / cos(eps)
    mc_rad = math.atan2(math.sin(theta), math.cos(theta) * math.cos(eps))
    mc_deg = math.degrees(mc_rad) % 360.0

    # 2. Cung Mọc (ASC - Ascendant, Đỉnh Nhà 1)
    # ASC là giao điểm của đường chân trời phía Đông với mặt phẳng hoàng đạo
    y = math.cos(theta)
    x = -(math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps))
    asc_rad = math.atan2(y, x)
    asc_deg = math.degrees(asc_rad) % 360.0

    # 3. Cung Lặn (DSC) và Thiên Đế (IC)
    dsc_deg = (asc_deg + 180.0) % 360.0
    ic_deg = (mc_deg + 180.0) % 360.0

    angles = {
        "ASC": {"code": "ASC", "name": "Cung Mọc (Ascendant)", "symbol": "AC", "longitude": asc_deg, "zodiac": deg_to_zodiac(asc_deg)},
        "MC": {"code": "MC", "name": "Thiên Đỉnh (Midheaven)", "symbol": "MC", "longitude": mc_deg, "zodiac": deg_to_zodiac(mc_deg)},
        "DSC": {"code": "DSC", "name": "Cung Lặn (Descendant)", "symbol": "DC", "longitude": dsc_deg, "zodiac": deg_to_zodiac(dsc_deg)},
        "IC": {"code": "IC", "name": "Thiên Đế (Imum Coeli)", "symbol": "IC", "longitude": ic_deg, "zodiac": deg_to_zodiac(ic_deg)},
    }

    cusps_deg: dict[int, float] = {}

    if house_system == "whole_sign":
        # Whole Sign: Cung chứa ASC là toàn bộ Nhà 1 (bắt đầu từ 0° của cung đó)
        asc_sign_idx = int(asc_deg // 30)
        for h in range(1, 13):
            sign_h = (asc_sign_idx + (h - 1)) % 12
            cusps_deg[h] = float(sign_h * 30)

    elif house_system == "equal":
        # Equal House: Nhà 1 bắt đầu chính xác từ ASC, mỗi nhà cách nhau 30°
        for h in range(1, 13):
            cusps_deg[h] = (asc_deg + (h - 1) * 30.0) % 360.0

    else:
        # Placidus: Chia ba cung bán nhật và bán dạ
        def solve_placidus_cusp(ramc_offset_deg: float, factor: float, is_below_horizon: bool) -> float:
            target_ra = (theta + math.radians(ramc_offset_deg)) % (2 * math.pi)
            lam = target_ra
            for _ in range(25):
                sin_d = math.sin(lam) * math.sin(eps)
                sin_d = max(-1.0, min(1.0, sin_d))
                tan_d = math.tan(math.asin(sin_d))

                val = math.tan(phi) * tan_d * factor
                val = max(-1.0, min(1.0, val))
                ad = math.asin(val)

                if is_below_horizon:
                    ra_target = (theta + math.radians(ramc_offset_deg) + ad) % (2 * math.pi)
                else:
                    ra_target = (theta + math.radians(ramc_offset_deg) - ad) % (2 * math.pi)

                lam_new = math.atan2(math.sin(ra_target), math.cos(ra_target) * math.cos(eps)) % (2 * math.pi)
                if abs(lam_new - lam) < 1e-6:
                    break
                lam = lam_new
            return math.degrees(lam) % 360.0

        cusp11 = solve_placidus_cusp(30.0, 1.0 / 3.0, False)
        cusp12 = solve_placidus_cusp(60.0, 2.0 / 3.0, False)
        cusp2 = solve_placidus_cusp(120.0, 2.0 / 3.0, True)
        cusp3 = solve_placidus_cusp(150.0, 1.0 / 3.0, True)

        cusps_deg = {
            1: asc_deg,
            2: cusp2,
            3: cusp3,
            4: ic_deg,
            5: (cusp11 + 180.0) % 360.0,
            6: (cusp12 + 180.0) % 360.0,
            7: dsc_deg,
            8: (cusp2 + 180.0) % 360.0,
            9: (cusp3 + 180.0) % 360.0,
            10: mc_deg,
            11: cusp11,
            12: cusp12,
        }

    # Đóng gói dữ liệu 12 Nhà
    houses: dict[int, dict] = {}
    for h in range(1, 13):
        start_lon = cusps_deg[h]
        next_h = 1 if h == 12 else h + 1
        end_lon = cusps_deg[next_h]
        z_info = deg_to_zodiac(start_lon)
        houses[h] = {
            "house": h,
            "cusp_longitude": round(start_lon, 4),
            "next_cusp_longitude": round(end_lon, 4),
            "zodiac": z_info,
        }

    return angles, houses


def find_house_for_longitude(lon: float, houses: dict[int, dict]) -> int:
    """Xác định vị trí kinh độ `lon` nằm trong Nhà nào (từ 1 đến 12)."""
    lon = lon % 360.0
    for h in range(1, 13):
        c1 = houses[h]["cusp_longitude"]
        c2 = houses[h]["next_cusp_longitude"]
        if c1 < c2:
            if c1 <= lon < c2:
                return h
        else:
            # Vượt qua mốc 0°/360° (Bạch Dương)
            if lon >= c1 or lon < c2:
                return h
    return 1


def calculate_aspects(points: dict[str, dict]) -> list[dict]:
    """Tính các góc chiếu giữa các hành tinh và trục theo 5 góc chiếu chính và dung sai (orb)."""
    aspects = []
    keys = list(points.keys())

    # Các thiên thể chính được tính góc chiếu (bỏ bớt South Node vì đối đỉnh North Node)
    active_keys = [k for k in keys if k not in ("SOUTH_NODE", "DSC", "IC")]

    for i in range(len(active_keys)):
        k1 = active_keys[i]
        p1 = points[k1]
        lon1 = p1["longitude"]
        is_luminary1 = (k1 in ("SUN", "MOON"))

        for j in range(i + 1, len(active_keys)):
            k2 = active_keys[j]
            p2 = points[k2]
            lon2 = p2["longitude"]
            is_luminary2 = (k2 in ("SUN", "MOON"))

            diff = abs(lon1 - lon2)
            shortest_dist = min(diff, 360.0 - diff)

            has_luminary = is_luminary1 or is_luminary2

            for asp in ASPECT_DEFINITIONS:
                target_angle = asp["angle"]
                max_orb = asp["orb_luminary"] if has_luminary else asp["orb_default"]
                orb_diff = abs(shortest_dist - target_angle)

                if orb_diff <= max_orb:
                    aspects.append({
                        "point1": k1,
                        "point1_name": p1["name"],
                        "point1_symbol": p1["symbol"],
                        "point2": k2,
                        "point2_name": p2["name"],
                        "point2_symbol": p2["symbol"],
                        "aspect_name": asp["name"],
                        "aspect_latin": asp["latin"],
                        "aspect_symbol": asp["symbol"],
                        "target_angle": target_angle,
                        "actual_angle": round(shortest_dist, 2),
                        "orb": round(orb_diff, 2),
                        "max_orb": max_orb,
                        "nature": asp["nature"],
                        "color": asp["color"],
                    })
                    break  # Mỗi cặp tối đa 1 góc chiếu chính

    # Sắp xếp góc chiếu theo độ chặt chẽ của orb (orb nhỏ nhất lên đầu)
    aspects.sort(key=lambda a: a["orb"])
    return aspects


def calculate_elements_and_modalities(points: dict[str, dict]) -> dict[str, dict]:
    """Thống kê phân bổ 4 Nguyên Tố (Lửa, Đất, Khí, Nước) và 3 Tính Chất (Tiên Phong, Kiên Định, Linh Hoạt)."""
    # 10 hành tinh chính + ASC
    counted_keys = ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO", "ASC"]

    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    elem_vn_map = {"Fire": "Lửa", "Earth": "Đất", "Air": "Khí", "Water": "Nước"}
    mod_vn_map = {"Cardinal": "Tiên phong", "Fixed": "Kiên định", "Mutable": "Linh hoạt"}

    total = 0
    for k in counted_keys:
        if k in points:
            z = points[k]["zodiac"]
            elements[z["sign_element"]] += 1
            modalities[z["sign_modality"]] += 1
            total += 1

    total = total or 1

    elem_res = {}
    for el, count in elements.items():
        elem_res[el] = {
            "name": elem_vn_map[el],
            "count": count,
            "percentage": round((count / total) * 100, 1),
        }

    mod_res = {}
    for mod, count in modalities.items():
        mod_res[mod] = {
            "name": mod_vn_map[mod],
            "count": count,
            "percentage": round((count / total) * 100, 1),
        }

    return {
        "elements": elem_res,
        "modalities": mod_res,
    }


def calculate_natal_chart(
    full_name: str,
    gender: Literal["male", "female"],
    birth_date: date,
    birth_time: time | None,
    birth_place: str = "",
    house_system: Literal["placidus", "whole_sign", "equal"] = "placidus",
) -> dict:
    """Tính toán toàn bộ thông số Bản Đồ Sao Chiêm Tinh (Natal Chart)."""
    time_provided = (birth_time is not None)
    actual_time = birth_time if time_provided else time(12, 0)

    # 1. Geocoding tra cứu vị trí địa lý
    loc_info = geocoding.resolve_location(birth_place)
    lat = loc_info.latitude
    lon = loc_info.longitude

    # 2. Quy đổi sang UTC:
    # Nếu là Việt Nam thì dùng bộ quy tắc múi giờ lịch sử Việt Nam
    # Nếu là quốc tế thì dùng cơ sở dữ liệu múi giờ chuẩn IANA (zoneinfo)
    tz_note = None
    if loc_info.timezone == "Asia/Ho_Chi_Minh":
        birth_utc, tz_info = timezones.local_birth_to_utc(birth_date, actual_time, birth_place)
        tz_note = tz_info.note
    else:
        from zoneinfo import ZoneInfo
        try:
            local_dt = datetime.combine(birth_date, actual_time).replace(tzinfo=ZoneInfo(loc_info.timezone))
            birth_utc = local_dt.astimezone(timezone.utc)
        except Exception:
            birth_utc, tz_info = timezones.local_birth_to_utc(birth_date, actual_time, birth_place)

    # 3. Tính vị trí hành tinh
    planets = calculate_planet_positions(birth_utc, lat, lon)

    # 4. Tính 4 trục và 12 Nhà
    angles, houses = calculate_angles_and_houses(birth_utc, lat, lon, house_system)

    # 5. Gán Nhà cho từng hành tinh
    for p_code, p_data in planets.items():
        h_num = find_house_for_longitude(p_data["longitude"], houses)
        p_data["house"] = h_num

    # Gộp toàn bộ các điểm để tính góc chiếu
    all_points = {**planets, **angles}

    # 6. Tính các góc chiếu (aspects)
    aspects = calculate_aspects(all_points)

    # 7. Thống kê Nguyên Tố & Tính Chất
    balance = calculate_elements_and_modalities(all_points)

    # Tên hiển thị trường phái nhà
    house_system_names = {
        "placidus": "Placidus (Bán nhật bán dạ - Chuẩn quốc tế)",
        "whole_sign": "Whole Sign (Cung nguyên vẹn - Chiêm tinh Cổ điển)",
        "equal": "Equal House (Nhà bằng nhau 30°)",
    }

    return {
        "full_name": full_name,
        "gender": gender,
        "birth_date": birth_date.isoformat(),
        "birth_time": birth_time.strftime("%H:%M") if birth_time else None,
        "time_provided": time_provided,
        "birth_place": birth_place,
        "resolved_location": {
            "name": loc_info.name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
        },
        "timezone_note": tz_note,
        "house_system": house_system,
        "house_system_name": house_system_names.get(house_system, house_system),
        "planets": planets,
        "angles": angles,
        "houses": houses,
        "aspects": aspects,
        "balance": balance,
    }
