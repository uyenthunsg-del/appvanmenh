"""Bộ vẽ Bánh Xe Bản Đồ Sao (Natal Chart Wheel) bằng vector SVG thuần.

Chuẩn quốc tế:
- Cung Mọc (ASC) luôn nằm ngang bên trái (vị trí 9 giờ).
- Vòng ngoài: 12 Cung Hoàng Đạo tô màu theo 4 Nguyên Tố (Lửa, Đất, Khí, Nước) kèm ký hiệu Glyph.
- Vòng giữa: 12 Nhà (House cusps) xoay chuẩn xác theo hệ thống nhà chỉ định, đánh số 1-12.
- Tọa độ hành tinh: Đặt chính xác theo độ số, có thuật toán chống đè lấn (collision avoidance) khi các hành tinh trùng tụ, kèm ký hiệu và độ số.
- Vòng trong: Các đường góc chiếu (Aspect lines) liên kết các hành tinh, phân màu xanh (hòa hợp) và đỏ (thử thách).
"""
from __future__ import annotations

import math
from typing import Any


def polar_to_cartesian(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """Chuyển đổi tọa độ cực (bán kính r, góc độ) sang tọa độ Decartes (x, y)."""
    rad = math.radians(angle_deg)
    x = cx + r * math.cos(rad)
    y = cy - r * math.sin(rad)  # SVG y hướng xuống
    return round(x, 2), round(y, 2)


def describe_arc(cx: float, cy: float, r_in: float, r_out: float, start_deg: float, end_deg: float) -> str:
    """Tạo path SVG vẽ hình nan quạt (annular sector) giữa r_in và r_out từ start_deg đến end_deg."""
    # Đảm bảo chiều vẽ ngược chiều kim đồng hồ
    diff = (end_deg - start_deg) % 360.0
    if diff == 0:
        diff = 359.99

    large_arc = 1 if diff > 180 else 0

    x_out_start, y_out_start = polar_to_cartesian(cx, cy, r_out, start_deg)
    x_out_end, y_out_end = polar_to_cartesian(cx, cy, r_out, start_deg + diff)
    x_in_end, y_in_end = polar_to_cartesian(cx, cy, r_in, start_deg + diff)
    x_in_start, y_in_start = polar_to_cartesian(cx, cy, r_in, start_deg)

    path = [
        f"M {x_out_start} {y_out_start}",
        f"A {r_out} {r_out} 0 {large_arc} 0 {x_out_end} {y_out_end}",
        f"L {x_in_end} {y_in_end}",
        f"A {r_in} {r_in} 0 {large_arc} 1 {x_in_start} {y_in_start}",
        "Z"
    ]
    return " ".join(path)


def generate_natal_chart_svg(chart_data: dict[str, Any]) -> str:
    """Sinh chuỗi XML SVG hoàn chỉnh cho bánh xe bản đồ sao."""
    cx, cy = 300.0, 300.0
    r_outer = 285.0
    r_zodiac_in = 235.0
    r_houses_in = 130.0
    r_aspects = 125.0

    asc_deg = chart_data["angles"]["ASC"]["longitude"]

    def lon_to_screen_angle(lon: float) -> float:
        """Quy đổi kinh độ hoàng đạo (0..360°) sang góc màn hình (ASC = 180° / 9 giờ)."""
        return (180.0 - (lon - asc_deg)) % 360.0

    svg_parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="100%" height="100%" class="natal-chart-svg" style="max-width: 600px; font-family: system-ui, -apple-system, sans-serif;">',
        '<defs>',
        '  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
        '    <feGaussianBlur stdDeviation="3" result="blur" />',
        '    <feComposite in="SourceGraphic" in2="blur" operator="over" />',
        '  </filter>',
        '</defs>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="rgba(129, 140, 248, 0.4)" stroke-width="1.5" />',
    ]

    # 1. Vẽ 12 Cung Hoàng Đạo trên vành ngoài (r_zodiac_in -> r_outer)
    # Màu nền mờ theo nguyên tố
    elem_colors = {
        "Fire": "rgba(239, 68, 68, 0.15)",
        "Earth": "rgba(16, 185, 129, 0.15)",
        "Air": "rgba(245, 158, 11, 0.15)",
        "Water": "rgba(59, 130, 246, 0.15)",
    }
    elem_text_colors = {
        "Fire": "#ef4444",
        "Earth": "#10b981",
        "Air": "#f59e0b",
        "Water": "#3b82f6",
    }

    # 12 cung từ 0° đến 360°
    for sign_idx in range(12):
        sign_start_lon = sign_idx * 30.0
        sign_end_lon = (sign_idx + 1) * 30.0
        start_angle = lon_to_screen_angle(sign_start_lon)
        # Trong hệ thống của ta, start_angle đi lùi theo chiều màn hình
        end_angle = lon_to_screen_angle(sign_end_lon)

        # Lấy thông tin cung
        # Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces
        sign_names = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
        sign_symbols = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
        elements = ["Fire", "Earth", "Air", "Water"] * 3
        elem = elements[sign_idx]

        # Vẽ nan quạt từ end_angle tới start_angle (vì end_angle nhỏ hơn start_angle khi đi ngược chiều kim đồng hồ)
        arc_path = describe_arc(cx, cy, r_zodiac_in, r_outer, end_angle, start_angle)
        fill_color = elem_colors[elem]
        svg_parts.append(f'<path d="{arc_path}" fill="{fill_color}" stroke="rgba(129, 140, 248, 0.25)" stroke-width="1" />')

        # Điểm giữa cung để đặt biểu tượng Glyph
        mid_lon = sign_start_lon + 15.0
        mid_angle = lon_to_screen_angle(mid_lon)
        gx, gy = polar_to_cartesian(cx, cy, (r_outer + r_zodiac_in) / 2.0, mid_angle)
        symbol = sign_symbols[sign_idx]
        t_col = elem_text_colors[elem]

        svg_parts.append(
            f'<text x="{gx}" y="{gy + 6}" text-anchor="middle" font-size="20" font-weight="bold" fill="{t_col}">{symbol}</text>'
        )

    # Vòng tròn ngăn cách cung và các nhà
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac_in}" fill="none" stroke="rgba(129, 140, 248, 0.4)" stroke-width="1.5" />')

    # 2. Vẽ 12 Nhà (House cusps)
    houses = chart_data["houses"]
    for h_num in range(1, 13):
        cusp_lon = houses[h_num]["cusp_longitude"]
        screen_angle = lon_to_screen_angle(cusp_lon)

        x_out, y_out = polar_to_cartesian(cx, cy, r_zodiac_in, screen_angle)
        x_in, y_in = polar_to_cartesian(cx, cy, r_aspects, screen_angle)

        is_asc = (h_num == 1)
        is_mc = (h_num == 10)
        is_dsc = (h_num == 7)
        is_ic = (h_num == 4)

        if is_asc or is_dsc:
            stroke = "#8b5cf6"
            stroke_width = "2.2"
        elif is_mc or is_ic:
            stroke = "#3b82f6"
            stroke_width = "2.0"
        else:
            stroke = "rgba(129, 140, 248, 0.3)"
            stroke_width = "1.0"

        svg_parts.append(f'<line x1="{x_in}" y1="{y_in}" x2="{x_out}" y2="{y_out}" stroke="{stroke}" stroke-width="{stroke_width}" />')

        # Đặt số nhà (1..12) ở khoảng giữa cusp nhà hiện tại và nhà kế tiếp
        next_h = 1 if h_num == 12 else h_num + 1
        next_cusp_lon = houses[next_h]["cusp_longitude"]
        diff_h = (next_cusp_lon - cusp_lon) % 360.0
        mid_house_lon = (cusp_lon + diff_h / 2.0) % 360.0
        mid_h_angle = lon_to_screen_angle(mid_house_lon)
        hx, hy = polar_to_cartesian(cx, cy, r_houses_in + 14.0, mid_h_angle)
        svg_parts.append(
            f'<text x="{hx}" y="{hy + 4}" text-anchor="middle" font-size="11" font-weight="600" fill="rgba(156, 163, 175, 0.9)">{h_num}</text>'
        )

    # 3. Vẽ nhãn các góc trục chính: AC (ASC), MC, DC (DSC), IC
    ac_x, ac_y = polar_to_cartesian(cx, cy, r_outer + 16, 180.0)
    svg_parts.append(f'<text x="{ac_x}" y="{ac_y + 5}" text-anchor="middle" font-size="13" font-weight="bold" fill="#8b5cf6">AC</text>')

    dc_x, dc_y = polar_to_cartesian(cx, cy, r_outer + 16, 0.0)
    svg_parts.append(f'<text x="{dc_x}" y="{dc_y + 5}" text-anchor="middle" font-size="13" font-weight="bold" fill="#8b5cf6">DC</text>')

    mc_angle = lon_to_screen_angle(chart_data["angles"]["MC"]["longitude"])
    mc_x, mc_y = polar_to_cartesian(cx, cy, r_outer + 16, mc_angle)
    svg_parts.append(f'<text x="{mc_x}" y="{mc_y + 5}" text-anchor="middle" font-size="13" font-weight="bold" fill="#3b82f6">MC</text>')

    ic_angle = lon_to_screen_angle(chart_data["angles"]["IC"]["longitude"])
    ic_x, ic_y = polar_to_cartesian(cx, cy, r_outer + 16, ic_angle)
    svg_parts.append(f'<text x="{ic_x}" y="{ic_y + 5}" text-anchor="middle" font-size="13" font-weight="bold" fill="#3b82f6">IC</text>')

    # Vòng tròn tâm Aspect
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_aspects}" fill="rgba(255, 255, 255, 0.03)" stroke="rgba(129, 140, 248, 0.35)" stroke-width="1.2" />'
    )

    # 4. Vẽ các đường góc chiếu (Aspect lines) ở tâm
    # Lấy tọa độ tâm của các hành tinh để nối dây
    planets = chart_data["planets"]
    planet_aspect_coords: dict[str, tuple[float, float]] = {}
    for code, p_data in planets.items():
        s_angle = lon_to_screen_angle(p_data["longitude"])
        px, py = polar_to_cartesian(cx, cy, r_aspects, s_angle)
        planet_aspect_coords[code] = (px, py)

    aspects = chart_data.get("aspects", [])
    for asp in aspects:
        p1 = asp["point1"]
        p2 = asp["point2"]
        if p1 in planet_aspect_coords and p2 in planet_aspect_coords:
            x1, y1 = planet_aspect_coords[p1]
            x2, y2 = planet_aspect_coords[p2]
            col = asp["color"]
            # Độ đậm nhạt theo dung sai orb (orb càng nhỏ đường càng rõ)
            opacity = max(0.25, round(1.0 - (asp["orb"] / (asp["max_orb"] or 8.0)) * 0.65, 2))
            width = "1.5" if asp["orb"] <= 2.0 else "1.0"
            dash = ' stroke-dasharray="3 3"' if asp["nature"] == "neutral" else ""
            svg_parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{width}" stroke-opacity="{opacity}"{dash} />'
            )

    # 5. Vẽ các Hành Tinh trên vành nhà (r_houses_in + 20 -> r_zodiac_in - 10)
    # Thuật toán chống đè lấn: sắp xếp theo góc màn hình và so le bán kính nếu góc lệch < 7°
    planet_items = []
    for code, p_data in planets.items():
        s_angle = lon_to_screen_angle(p_data["longitude"])
        planet_items.append({
            "code": code,
            "data": p_data,
            "angle": s_angle,
            "lon": p_data["longitude"],
        })
    planet_items.sort(key=lambda item: item["angle"])

    # Phân tầng bán kính nếu trùng nhau
    radii_levels = [165.0, 190.0, 215.0]
    assigned_radius = [radii_levels[1]] * len(planet_items)

    for i in range(len(planet_items)):
        prev_i = (i - 1) % len(planet_items)
        diff_ang = abs(planet_items[i]["angle"] - planet_items[prev_i]["angle"])
        if diff_ang > 180.0:
            diff_ang = 360.0 - diff_ang
        if diff_ang < 7.5:
            # Đổi tầng bán kính để không đè
            assigned_radius[i] = radii_levels[2] if assigned_radius[prev_i] == radii_levels[1] else radii_levels[0]

    for idx, item in enumerate(planet_items):
        p_data = item["data"]
        s_angle = item["angle"]
        r_planet = assigned_radius[idx]

        px, py = polar_to_cartesian(cx, cy, r_planet, s_angle)
        # Đường gạch nhỏ chỉ ra mép cung
        tx, ty = polar_to_cartesian(cx, cy, r_zodiac_in - 2, s_angle)
        svg_parts.append(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="rgba(156, 163, 175, 0.4)" stroke-width="0.75" />')

        # Vòng tròn nhỏ nền cho ký hiệu hành tinh
        svg_parts.append(f'<circle cx="{px}" cy="{py}" r="11" fill="rgba(30, 27, 75, 0.85)" stroke="rgba(129, 140, 248, 0.6)" stroke-width="1" />')

        # Ký hiệu hành tinh
        sym = p_data["symbol"]
        svg_parts.append(f'<text x="{px}" y="{py + 4}" text-anchor="middle" font-size="12" font-weight="bold" fill="#fff">{sym}</text>')

        # Độ số trong cung (ví dụ: 15°)
        z_deg = p_data["zodiac"]["degrees"]
        deg_txt = f"{z_deg}°"
        rx_txt = "Rx" if p_data.get("is_retrograde") else ""

        dx, dy = polar_to_cartesian(cx, cy, r_planet - 16, s_angle)
        svg_parts.append(f'<text x="{dx}" y="{dy + 3}" text-anchor="middle" font-size="9" font-weight="600" fill="rgba(229, 231, 235, 0.9)">{deg_txt}</text>')
        if rx_txt:
            svg_parts.append(f'<text x="{dx + 9}" y="{dy - 2}" text-anchor="middle" font-size="7" font-weight="bold" fill="#ef4444">{rx_txt}</text>')

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)
