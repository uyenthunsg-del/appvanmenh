"""Bộ kiểm thử cho Bát Tự (Tứ Trụ) với các ca thực tế có đối chiếu đáp án đã biết."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
import pytest

import bazi
import solar_terms
import timezones


def test_case_1_lichun_boundary_2024():
    """Ca 1: Kiểm tra ranh giới Lập Xuân năm 2024 (ngày 04/02/2024).
    
    Lập Xuân 2024 diễn ra lúc khoảng 15:27 UTC+7 (08:27 UTC).
    - Sinh lúc 07:00 sáng (trước Lập Xuân): vẫn thuộc năm Quý Mão (2023), tháng Ất Sửu.
    - Sinh lúc 17:00 chiều (sau Lập Xuân): đã sang năm Giáp Thìn (2024), tháng Bính Dần.
    """
    # 1. Trước Lập Xuân
    res_before = bazi.calculate_bazi("Test Before", "male", date(2024, 2, 4), time(7, 0), "Hà Nội")
    p_year_before = res_before["pillars"][0]["can_chi"]
    p_month_before = res_before["pillars"][1]["can_chi"]
    assert p_year_before == "Quý Mão", f"Trước Lập Xuân phải là Quý Mão, kết quả: {p_year_before}"
    assert p_month_before == "Ất Sửu", f"Trước Lập Xuân phải là tháng Ất Sửu, kết quả: {p_month_before}"

    # 2. Sau Lập Xuân
    res_after = bazi.calculate_bazi("Test After", "male", date(2024, 2, 4), time(17, 0), "Hà Nội")
    p_year_after = res_after["pillars"][0]["can_chi"]
    p_month_after = res_after["pillars"][1]["can_chi"]
    assert p_year_after == "Giáp Thìn", f"Sau Lập Xuân phải là Giáp Thìn, kết quả: {p_year_after}"
    assert p_month_after == "Bính Dần", f"Sau Lập Xuân phải là tháng Bính Dần, kết quả: {p_month_after}"


def test_case_2_classical_bazi_1990():
    """Ca 2: Ngày 15/05/1990 lúc 10:30 sáng, Nam tại Hà Nội.
    
    Đáp án đối chiếu chuẩn:
    - Năm: Canh Ngọ (Dương Kim, Lộ Bàng Thổ)
    - Tháng: Sau Lập Hạ (05/05) nên là tháng Tị. Năm Canh khởi Mậu Dần -> tháng Tị là Tân Tị.
    - Ngày: Canh Thìn (Dương Kim, Bạch Lạp Kim)
    - Giờ: 10:30 là giờ Tị. Ngày Canh khởi Bính Tý -> giờ Tị là Tân Tị.
    - Nhật chủ: Canh. Canh năm là Tỷ Kiên, Tân tháng là Kiếp Tài, Tân giờ là Kiếp Tài.
    - Chiều đại vận: Dương Nam -> Thuận hành. Tháng Tân Tị -> bước 1 là Nhâm Ngọ.
    """
    res = bazi.calculate_bazi("Nguyễn Nam", "male", date(1990, 5, 15), time(10, 30), "Hà Nội")
    pillars = {p["key"]: p for p in res["pillars"]}

    assert pillars["year"]["can_chi"] == "Canh Ngọ"
    assert pillars["month"]["can_chi"] == "Tân Tị"
    assert pillars["day"]["can_chi"] == "Canh Thìn"
    assert pillars["hour"]["can_chi"] == "Tân Tị"

    assert pillars["year"]["ten_god"] == "Tỷ Kiên"
    assert pillars["month"]["ten_god"] == "Kiếp Tài"
    assert pillars["day"]["ten_god"] == "Nhật Chủ"
    assert pillars["hour"]["ten_god"] == "Kiếp Tài"

    # Đại vận thuận
    assert res["major_cycles_info"]["direction"] == "Thuận"
    assert res["major_cycles"][0]["can_chi"] == "Nhâm Ngọ"
    assert res["major_cycles"][0]["ten_god"] == "Thực Thần"


def test_case_3_zi_hour_modes():
    """Ca 3: Kiểm tra xử lý giờ Tý đêm (23:00 - 23:59:59).
    
    Ngày 20/05/2020:
    - Ban ngày ngày 20/05/2020 là Quý Hợi (vị trí 59 trong Lục thập hoa giáp).
    - Ngày tiếp theo 21/05/2020 là Giáp Tý (vị trí 0 trong Lục thập hoa giáp).
    - Lúc 23:30:
      + zi_mode='next_day' (chuẩn Tử Bình): Đã sang ngày mới 21/05 -> Trụ ngày là Giáp Tý, trụ giờ là Giáp Tý.
      + zi_mode='early_late' (Dạ Tý): Vẫn tính ngày 20/05 -> Trụ ngày là Quý Hợi, trụ giờ tính theo ngày Quý là Nhâm Tý.
    """
    # next_day
    res_next = bazi.calculate_bazi("Zi Test", "male", date(2020, 5, 20), time(23, 30), "Hà Nội", zi_mode="next_day")
    p_day_next = [p for p in res_next["pillars"] if p["key"] == "day"][0]["can_chi"]
    p_hour_next = [p for p in res_next["pillars"] if p["key"] == "hour"][0]["can_chi"]
    assert p_day_next == "Giáp Tý", f"next_day ngày phải là Giáp Tý, nhận được: {p_day_next}"
    assert p_hour_next == "Giáp Tý", f"next_day giờ phải là Giáp Tý, nhận được: {p_hour_next}"

    # early_late
    res_early = bazi.calculate_bazi("Zi Test", "male", date(2020, 5, 20), time(23, 30), "Hà Nội", zi_mode="early_late")
    p_day_early = [p for p in res_early["pillars"] if p["key"] == "day"][0]["can_chi"]
    p_hour_early = [p for p in res_early["pillars"] if p["key"] == "hour"][0]["can_chi"]
    assert p_day_early == "Quý Hợi", f"early_late ngày phải là Quý Hợi, nhận được: {p_day_early}"
    assert p_hour_early == "Nhâm Tý", f"early_late giờ phải là Nhâm Tý, nhận được: {p_hour_early}"


def test_case_4_historical_saigon_timezone_1968():
    """Ca 4: Kiểm tra chuyển đổi múi giờ lịch sử tại miền Nam (Sài Gòn) năm 1968.
    
    Tại miền Nam (1960 - 30/04/1975) áp dụng múi giờ UTC+8.
    - Một người sinh lúc 08:30 sáng giờ Sài Gòn (UTC+8) -> giờ thực thiên văn là 07:30 (UTC+7).
    - Canh giờ: 07:30 vẫn là giờ Thìn (07:00 - 08:59).
    - Hệ thống phải nhận diện được và trả về timezone_note phù hợp.
    """
    res = bazi.calculate_bazi("Miền Nam 1968", "female", date(1968, 6, 15), time(8, 30), "Sài Gòn")
    assert res["timezone_note"] is not None
    assert "UTC+8" in res["timezone_note"]
    assert "Sài Gòn" in res["birth_place"]


def test_case_5_life_stage_tu_modes():
    """Ca 5: Kiểm tra trường phái vòng Tràng Sinh của can Thổ (Mậu, Kỷ).
    
    Can Mậu tại chi Dần:
    - Nếu Hỏa Thổ đồng cung (tu_mode='fire'): Dần là Trường Sinh của Mậu (như Bính).
    - Nếu Thủy Thổ đồng cung (tu_mode='water'): Thân là Trường Sinh của Mậu -> Dần là cung Bệnh.
    """
    stage_fire = bazi.get_life_stage("Mậu", "Dần", tu_mode="fire")
    stage_water = bazi.get_life_stage("Mậu", "Dần", tu_mode="water")
    assert stage_fire == "Trường Sinh", f"Hỏa Thổ đồng cung: Mậu tại Dần phải là Trường Sinh, nhận được: {stage_fire}"
    assert stage_water == "Bệnh", f"Thủy Thổ đồng cung: Mậu tại Dần phải là Bệnh, nhận được: {stage_water}"


def test_case_6_yin_female_major_cycle_direction():
    """Ca 6: Kiểm tra chiều Đại Vận và Thần Sát.
    
    Năm 1995: Ất Hợi (Ất là Âm Mộc).
    - Giới tính: Nữ (Âm Nữ).
    - Quy tắc: Âm Nữ thì Đại Vận đi THUẬN.
    - Nếu là Nam (Âm Nam) thì Đại Vận đi NGHỊCH.
    """
    res_female = bazi.calculate_bazi("Bé Gái", "female", date(1995, 8, 20), time(14, 0), "Đà Nẵng")
    assert res_female["major_cycles_info"]["direction"] == "Thuận"

    res_male = bazi.calculate_bazi("Bé Trai", "male", date(1995, 8, 20), time(14, 0), "Đà Nẵng")
    assert res_male["major_cycles_info"]["direction"] == "Nghịch"
