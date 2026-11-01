"""Unit test cho numerology.py.

Mọi đáp án dưới đây do tôi tính tay từ chính các quy tắc đã chốt (Pythagoras,
rút gọn từng thành phần, giữ 11/22/33), chứ KHÔNG đối chiếu với máy tính thần
số học bên ngoài. Vì các trường phái cho kết quả khác nhau, đáp án đúng ở đây
nghĩa là "đúng theo quy tắc đã chọn", không phải "đúng tuyệt đối".
"""
from datetime import date

import pytest

import numerology as n


# --- Bỏ dấu tiếng Việt -------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Nguyễn Văn Đạt", "Nguyen Van Dat"),
        ("Đặng Phương", "Dang Phuong"),
        ("Trần Thị Thùy", "Tran Thi Thuy"),
        ("Ngô Quyền", "Ngo Quyen"),
        ("ĐỖ HOÀNG", "DO HOANG"),
        ("đ", "d"),
        ("Nguyễn", "Nguyen"),  # ễ ở dạng tổ hợp (NFD)
    ],
)
def test_remove_accents(raw, expected):
    assert n.remove_accents(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  nguyễn   văn-a. ", "NGUYEN VAN A"),
        ("Đặng Phương", "DANG PHUONG"),
        ("anh", "ANH"),
        ("A1B", "A B"),
        ("---", ""),
    ],
)
def test_normalize_name(raw, expected):
    assert n.normalize_name(raw) == expected


# --- Bảng quy đổi chữ cái ----------------------------------------------------
@pytest.mark.parametrize(
    "letter, value",
    [("A", 1), ("J", 1), ("S", 1), ("B", 2), ("K", 2), ("T", 2), ("E", 5), ("I", 9),
     ("R", 9), ("Y", 7), ("Z", 8), ("H", 8)],
)
def test_letter_values(letter, value):
    assert n.LETTER_VALUES[letter] == value


def test_letter_table_covers_26_letters():
    assert len(n.LETTER_VALUES) == 26
    # Hai vòng đầy đủ 1..9 (45 + 45) cộng vòng cuối chỉ có 1..8 (36) = 126.
    assert sum(n.LETTER_VALUES.values()) == 126


# --- Rút gọn số --------------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected",
    [(9, 9), (10, 1), (19, 1), (28, 1), (29, 11), (38, 11), (47, 11), (22, 22),
     (33, 33), (44, 8), (55, 1), (99, 9), (0, 0)],
)
def test_reduce_number(value, expected):
    assert n.reduce_number(value) == expected


# --- Số chủ đạo ----------------------------------------------------------------
@pytest.mark.parametrize(
    "birth, expected",
    [
        (date(1990, 1, 1), 3),    # 1 + 1 + (1+9+9+0=19->1) = 3
        (date(2000, 1, 1), 4),    # 1 + 1 + 2 = 4
        (date(1985, 11, 29), 9),  # 11 + 11 + 5 = 27 -> 9
        (date(1971, 1, 1), 11),   # 1 + 1 + 9 = 11 (giữ nguyên)
        (date(1971, 4, 9), 22),   # 9 + 4 + 9 = 22 (giữ nguyên)
        (date(1910, 11, 11), 33), # 11 + 11 + 11 = 33 (giữ nguyên)
        (date(1995, 7, 15), 1),   # 6 + 7 + 6 = 19 -> 1
        (date(1988, 8, 8), 6),    # 8 + 8 + 8 = 24 -> 6
    ],
)
def test_life_path(birth, expected):
    assert n.life_path_number(birth) == expected


def test_life_path_parts():
    assert n.life_path_parts(date(1985, 11, 29)) == (11, 11, 5, 27)


# --- Số ngày sinh --------------------------------------------------------------
@pytest.mark.parametrize(
    "day, expected",
    [(1, 1), (7, 7), (10, 1), (11, 11), (15, 6), (19, 1), (22, 22), (28, 1), (29, 11), (31, 4)],
)
def test_birth_day(day, expected):
    assert n.birth_day_number(date(1990, 1, day)) == expected


# --- Số biểu đạt / linh hồn / nhân cách (Y = auto) ----------------------------
# (tên, biểu đạt, linh hồn, nhân cách)
NAME_CASES = [
    ("ANH", 5, 1, 4),               # 14->5 ; A=1 ; 5+8=13->4
    ("MINH", 8, 9, 8),              # 26->8 ; I=9 ; 4+5+8=17->8
    ("HOA", 6, 7, 8),               # 15->6 ; O6+A1=7 ; H=8
    ("JOHN SMITH", 8, 6, 11),       # 44->8 ; 6+9=15->6 ; 29->11
    ("LE", 8, 5, 3),                # 8 ; E=5 ; L=3
    ("NGUYEN VAN A", 7, 1, 33),     # 43->7 ; 10->1 ; 33 (giữ nguyên)
    ("Đặng Phương", 8, 1, 7),       # 53->8 ; 10->1 ; 43->7
    ("anh", 5, 1, 4),               # không phân biệt hoa thường
]


@pytest.mark.parametrize("name, expression, soul, personality", NAME_CASES)
def test_name_numbers(name, expression, soul, personality):
    assert n.expression_number(name) == expression
    assert n.soul_urge_number(name) == soul
    assert n.personality_number(name) == personality


# --- Quy tắc chữ Y --------------------------------------------------------------
@pytest.mark.parametrize(
    "name, mode, soul, personality",
    [
        ("LY", "auto", 7, 3),          # Y sau phụ âm, cuối từ -> nguyên âm
        ("YEN", "auto", 5, 3),         # Y đầu từ, cạnh E -> phụ âm; 12->3
        ("THUY", "auto", 3, 8),        # Y sau U -> phụ âm; 17->8
        ("THUY", "vowel", 1, 1),       # ép nguyên âm: 3+7=10->1 ; 2+8=10->1
        ("THUY", "consonant", 3, 8),
        ("SYD", "auto", 7, 5),         # Y giữa hai phụ âm -> nguyên âm ; 1+4=5
        ("MAYA", "auto", 2, 11),       # Y giữa hai nguyên âm -> phụ âm ; 4+7=11 (giữ nguyên)
        ("NGUYEN VAN A", "vowel", 8, 8),  # linh hồn 17->8, nhân cách 26->8
    ],
)
def test_y_rule(name, mode, soul, personality):
    assert n.soul_urge_number(name, mode) == soul
    assert n.personality_number(name, mode) == personality


def test_expression_does_not_depend_on_y_mode():
    for mode in n.Y_MODES:
        assert n.expression_number("NGUYEN VAN A", mode) == 7


# --- Lỗi đầu vào và cấu trúc kết quả ---------------------------------------------
@pytest.mark.parametrize("bad", ["", "   ", "123", "---"])
def test_name_without_letters_is_rejected(bad):
    with pytest.raises(ValueError):
        n.analyze_name(bad)


def test_invalid_y_mode_is_rejected():
    with pytest.raises(ValueError):
        n.analyze_name("ANH", "sometimes")


def test_calculate_structure():
    result = n.calculate("Nguyễn Văn A", date(1990, 1, 1))
    assert result["input"]["normalized_name"] == "NGUYEN VAN A"
    assert result["life_path"]["value"] == 3
    assert result["life_path"]["parts"] == {"day": 1, "month": 1, "year": 1}
    assert result["expression"] == {"value": 7, "total": 43, "master": False}
    assert result["soul_urge"]["value"] == 1
    assert result["personality"] == {"value": 33, "total": 33, "master": True}
    assert result["birth_day"] == {"value": 1, "day": 1, "master": False}
    assert [w["word"] for w in result["name_breakdown"]] == ["NGUYEN", "VAN", "A"]


# --- Số Thái độ (ngày rút gọn + tháng rút gọn) ----------------------------------
# Đáp án tính tay theo quy tắc đã chọn. Mẫu 2005-10-21 = 4 cũng khớp một trang web khác.
@pytest.mark.parametrize(
    "birth, expected",
    [
        (date(2005, 10, 21), 4),   # 3 + 1
        (date(1990, 1, 1), 2),     # 1 + 1
        (date(1988, 8, 8), 7),     # 8 + 8 = 16 -> 7
        (date(1971, 4, 9), 4),     # 9 + 4 = 13 -> 4
        (date(1995, 7, 15), 4),    # 6 + 7 = 13 -> 4
        (date(2000, 12, 31), 7),   # 4 + 3
        (date(1985, 11, 29), 22),  # 11 + 11 = 22 (giữ nguyên)
    ],
)
def test_attitude(birth, expected):
    assert n.attitude_number(birth) == expected


# --- Số Trưởng thành (số chủ đạo + số biểu đạt) ----------------------------------
@pytest.mark.parametrize(
    "name, birth, expected",
    [
        ("Nguyễn Lê Uyên Thư", date(2005, 10, 21), 3),  # 11 + 1 = 12 -> 3 (khớp trang web mẫu)
        ("Nguyễn Văn A", date(1990, 1, 1), 1),          # 3 + 7 = 10 -> 1
        ("Anh", date(1990, 1, 1), 8),                   # 3 + 5
        ("Minh", date(1995, 7, 15), 9),                 # 1 + 8
        ("John Smith", date(1971, 4, 9), 3),            # 22 + 8 = 30 -> 3
        ("Hoa", date(1988, 8, 8), 3),                   # 6 + 6 = 12 -> 3
    ],
)
def test_maturity(name, birth, expected):
    assert n.maturity_number(name, birth) == expected


# --- Năm cá nhân ------------------------------------------------------------------
# (ngày sinh, năm xem, value, single)
PERSONAL_YEAR_CASES = [
    (date(2005, 10, 21), 2021, 9, 9),    # 3 + 1 + 5
    (date(2005, 10, 21), 2026, 5, 5),    # 3 + 1 + 1
    (date(2005, 10, 21), 2023, 11, 2),   # 3 + 1 + 7 = 11 (bậc thầy), vẽ biểu đồ ở số 2
    (date(1990, 1, 1), 2026, 3, 3),      # 1 + 1 + 1
    (date(1985, 11, 29), 2025, 4, 4),    # 2 + 2 + 9 = 13 -> 4 (ngày/tháng bậc thầy rút về 1 chữ số)
    (date(1971, 4, 9), 2026, 5, 5),      # 9 + 4 + 1 = 14 -> 5
    (date(1988, 8, 8), 2022, 22, 4),     # 8 + 8 + 6 = 22
    (date(2000, 12, 31), 2020, 11, 2),   # 4 + 3 + 4 = 11
]


@pytest.mark.parametrize("birth, year, value, single", PERSONAL_YEAR_CASES)
def test_personal_year(birth, year, value, single):
    py = n.personal_year(birth, year)
    assert (py["value"], py["single"]) == (value, single)
    assert py["master"] == (value in (11, 22, 33))


def test_personal_year_cycle_matches_reference_site():
    # Chu kỳ 2021-2031 của mẫu 21/10/2005, đối chiếu biểu đồ trên trang web mẫu:
    # 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1 (năm 2023 trang đó ghi 2, bên mình là 11 vẽ ở vị trí 2).
    cycle = n.personal_year_cycle(date(2005, 10, 21), 2026)
    assert [c["year"] for c in cycle] == list(range(2021, 2032))
    assert [c["single"] for c in cycle] == [9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]


def test_personal_year_cycle_always_steps_by_one():
    cycle = n.personal_year_cycle(date(1990, 3, 14), 2026)
    singles = [c["single"] for c in cycle]
    for a, b in zip(singles, singles[1:]):
        assert b == a % 9 + 1


def test_personal_year_cycle_skips_years_before_birth():
    cycle = n.personal_year_cycle(date(2024, 5, 5), 2026)
    assert cycle[0]["year"] == 2024 and cycle[-1]["year"] == 2031


def test_calculate_new_fields():
    r = n.calculate("Nguyễn Lê Uyên Thư", date(2005, 10, 21), year=2026)
    assert r["attitude"]["value"] == 4 and r["attitude"]["parts"] == {"day": 3, "month": 1}
    assert r["maturity"]["value"] == 3 and r["maturity"]["parts"] == {"life_path": 11, "expression": 1}
    assert r["personal_year"]["year"] == 2026
    assert r["personal_year"]["current"]["value"] == 5
    assert len(r["personal_year"]["cycle"]) == 11
