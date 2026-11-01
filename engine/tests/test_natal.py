"""Bộ kiểm thử cho module Bản Đồ Sao (Natal Chart) với các dữ liệu đối chiếu chuẩn xác."""
from __future__ import annotations

from datetime import date, time
import pytest

import natal
import natal_svg


def test_case_1_steve_jobs_chart():
    """Ca 1: Steve Jobs (24/02/1955, 19:15 tại San Francisco / Los Angeles múi giờ UTC-8).
    
    Dữ liệu đối chiếu chuẩn (Astro-Databank / Astro.com Rodden Rating AA):
    - Sun: Song Ngư (Pisces) ~5°
    - Moon: Bạch Dương (Aries) ~7°
    - ASC: Xử Nữ (Virgo) ~21°
    - MC: Song Tử (Gemini) ~20°
    """
    res = natal.calculate_natal_chart(
        full_name="Steve Jobs",
        gender="male",
        birth_date=date(1955, 2, 24),
        birth_time=time(19, 15),
        birth_place="Los Angeles",
        house_system="placidus",
    )
    sun = res["planets"]["SUN"]["zodiac"]
    moon = res["planets"]["MOON"]["zodiac"]

    assert sun["sign_id"] == "pisces", f"Sun phải ở Song Ngư, nhận được {sun['sign_name']}"
    assert sun["degrees"] in (5, 6), f"Sun độ số ~5°, nhận được {sun['degrees']}°"

    assert moon["sign_id"] == "aries", f"Moon phải ở Bạch Dương, nhận được {moon['sign_name']}"
    assert moon["degrees"] in (7, 8), f"Moon độ số ~7°, nhận được {moon['degrees']}°"


def test_case_2_einstein_chart():
    """Ca 2: Albert Einstein (14/03/1879, 11:30 tại Ulm / Berlin, Đức).
    
    Dữ liệu đối chiếu chuẩn (Astro-Databank Rodden Rating AA):
    - Sun: Song Ngư (Pisces) ~23°
    - Moon: Nhân Mã (Sagittarius) ~14°
    """
    res = natal.calculate_natal_chart(
        full_name="Albert Einstein",
        gender="male",
        birth_date=date(1879, 3, 14),
        birth_time=time(11, 30),
        birth_place="Berlin",
        house_system="placidus",
    )
    sun = res["planets"]["SUN"]["zodiac"]
    moon = res["planets"]["MOON"]["zodiac"]

    assert sun["sign_id"] == "pisces", f"Sun phải ở Song Ngư, nhận được {sun['sign_name']}"
    assert sun["degrees"] in (23, 24), f"Sun độ số ~23°, nhận được {sun['degrees']}°"

    assert moon["sign_id"] == "sagittarius", f"Moon phải ở Nhân Mã, nhận được {moon['sign_name']}"
    assert moon["degrees"] in (14, 15), f"Moon độ số ~14°, nhận được {moon['degrees']}°"


def test_case_3_house_systems_comparison():
    """Ca 3: Kiểm tra và so sánh 3 hệ thống nhà (Placidus, Whole Sign, Equal House) cho cùng một thời điểm."""
    b_date = date(1990, 5, 15)
    b_time = time(10, 30)

    # 1. Placidus
    res_p = natal.calculate_natal_chart("Test P", "female", b_date, b_time, "Hà Nội", house_system="placidus")
    # 2. Whole Sign
    res_w = natal.calculate_natal_chart("Test W", "female", b_date, b_time, "Hà Nội", house_system="whole_sign")
    # 3. Equal House
    res_e = natal.calculate_natal_chart("Test E", "female", b_date, b_time, "Hà Nội", house_system="equal")

    asc_deg = res_p["angles"]["ASC"]["longitude"]

    # Whole sign: Nhà 1 bắt đầu từ 0° của cung chứa ASC
    asc_sign_idx = int(asc_deg // 30)
    expected_w_h1 = float(asc_sign_idx * 30)
    assert res_w["houses"][1]["cusp_longitude"] == expected_w_h1

    # Equal house: Nhà 1 bắt đầu từ chính xác ASC, Nhà 2 = (ASC + 30) % 360
    assert abs(res_e["houses"][1]["cusp_longitude"] - asc_deg) < 1e-4
    assert abs(res_e["houses"][2]["cusp_longitude"] - ((asc_deg + 30.0) % 360.0)) < 1e-4

    # Cả 3 hệ thống đều có vị trí các hành tinh GIỐNG NHAU (chỉ khác đỉnh nhà)
    assert res_p["planets"]["SUN"]["longitude"] == res_w["planets"]["SUN"]["longitude"]
    assert res_p["planets"]["MOON"]["longitude"] == res_e["planets"]["MOON"]["longitude"]


def test_case_4_aspects_calculation():
    """Ca 4: Kiểm tra tính toán góc chiếu (Aspects)."""
    res = natal.calculate_natal_chart("Aspect Test", "male", date(1990, 5, 15), time(10, 30), "Hà Nội")
    aspects = res["aspects"]
    assert len(aspects) > 0

    aspect_names = {a["aspect_name"] for a in aspects}
    # Phải có các loại góc chiếu chính
    assert any(name in aspect_names for name in ["Trùng tụ", "Lục hợp", "Vuông góc", "Tam hợp", "Đối đỉnh"])

    for a in aspects:
        assert a["orb"] <= a["max_orb"], f"Orb {a['orb']} phải <= max_orb {a['max_orb']}"
        assert a["nature"] in ("harmonious", "challenging", "neutral")


def test_case_5_geocoding_vietnam_saigon():
    """Ca 5: Kiểm tra Geocoding tự động nơi sinh tại Việt Nam và hiệu chỉnh múi giờ lịch sử."""
    res = natal.calculate_natal_chart("Bé Sài Gòn", "female", date(1968, 6, 15), time(8, 30), "Sài Gòn")
    loc = res["resolved_location"]
    assert "Sài Gòn" in loc["name"]
    assert abs(loc["latitude"] - 10.8231) < 0.01
    assert abs(loc["longitude"] - 106.6297) < 0.01
    assert res["timezone_note"] is not None
    assert "UTC+8" in res["timezone_note"]


def test_case_6_svg_generation():
    """Ca 6: Kiểm tra tạo mã vector SVG bánh xe bản đồ sao."""
    res = natal.calculate_natal_chart("SVG Test", "male", date(2000, 1, 1), time(12, 0), "Đà Nẵng")
    svg = natal_svg.generate_natal_chart_svg(res)

    assert "<svg" in svg
    assert "</svg>" in svg
    assert 'viewBox="0 0 600 600"' in svg
    assert "AC" in svg  # Nhãn Cung Mọc
    assert "MC" in svg  # Nhãn Thiên Đỉnh
    assert "♈" in svg  # Ký hiệu cung hoàng đạo
