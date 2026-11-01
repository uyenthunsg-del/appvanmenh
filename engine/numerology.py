"""Thần số học theo hệ quy đổi Pythagoras.

Các lựa chọn trường phái (đã chốt với người dùng, xem README):
  1. Bảng chữ cái: Pythagoras, A=1 ... I=9, J=1 ... R=9, S=1 ... Z=8.
  2. Chữ Y: chế độ "auto" coi Y là nguyên âm khi đứng sau một phụ âm và không
     cạnh nguyên âm nào; còn lại là phụ âm. Có thể ép "vowel" / "consonant".
  3. Số chủ đạo: rút gọn riêng ngày, tháng, năm (giữ 11/22/33), cộng ba số lại
     rồi rút gọn một lần nữa (vẫn giữ 11/22/33).
  4. Số ngày sinh: trả về cả số gốc (1-31) và số đã rút gọn.
  5. Họ tên: tính theo toàn bộ chuỗi nhập, đúng thứ tự.
  6. Số Thái độ = ngày sinh rút gọn + tháng sinh rút gọn. Số Trưởng thành =
     số chủ đạo + số biểu đạt. Cả hai rút gọn và giữ 11/22/33.
     (Khớp 1 mẫu đối chiếu từ một trang web khác, chưa đối chiếu nguồn sách.)
  7. Năm cá nhân = ngày + tháng sinh + năm xem; mỗi thành phần rút về 1 chữ số
     (1-9) để chu kỳ luôn tăng đều 1-9. Tổng cuối giữ lại 11/22 trong "value"
     và luôn có thêm "single" (1-9) để vẽ biểu đồ.
  Chưa làm: số Tư duy (chưa rõ công thức chuẩn).

Module này chỉ dùng thư viện chuẩn của Python.
"""
from __future__ import annotations

import unicodedata
from datetime import date

MASTER_NUMBERS: tuple[int, ...] = (11, 22, 33)
VOWELS = frozenset("AEIOU")
Y_MODES = ("auto", "vowel", "consonant")

# A=1, B=2, ... I=9, J=1, ... Z=8 (chỉ số chữ cái chia dư 9, cộng 1).
LETTER_VALUES: dict[str, int] = {chr(ord("A") + i): i % 9 + 1 for i in range(26)}


def remove_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'Nguyễn Văn Đạt' -> 'Nguyen Van Dat'.

    Đ/đ không tách được bằng Unicode NFD nên phải đổi riêng trước.
    """
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalize_name(name: str) -> str:
    """Bỏ dấu, viết hoa, chỉ giữ chữ A-Z; mọi ký tự khác thành dấu cách đơn."""
    upper = remove_accents(name).upper()
    cleaned = "".join(ch if "A" <= ch <= "Z" else " " for ch in upper)
    return " ".join(cleaned.split())


def reduce_number(n: int, keep_master: tuple[int, ...] = MASTER_NUMBERS) -> int:
    """Cộng các chữ số cho tới khi còn 1 chữ số, dừng sớm ở 11, 22, 33."""
    while n > 9 and n not in keep_master:
        n = sum(int(d) for d in str(n))
    return n


def _is_vowel(word: str, i: int, y_mode: str) -> bool:
    """Chữ cái thứ i của từ là nguyên âm hay phụ âm."""
    ch = word[i]
    if ch in VOWELS:
        return True
    if ch != "Y":
        return False
    if y_mode == "vowel":
        return True
    if y_mode == "consonant":
        return False
    # auto: Y là nguyên âm khi đứng sau phụ âm (không phải đầu từ)
    # và phía sau không phải nguyên âm. Ví dụ LY -> nguyên âm, THUY/YEN -> phụ âm.
    after_consonant = i > 0 and word[i - 1] not in VOWELS
    before_nothing_vowel = i + 1 >= len(word) or word[i + 1] not in VOWELS
    return after_consonant and before_nothing_vowel


def analyze_name(name: str, y_mode: str = "auto") -> dict:
    """Tách họ tên thành từng chữ cái kèm giá trị và loại (nguyên âm/phụ âm)."""
    if y_mode not in Y_MODES:
        raise ValueError(f"y_mode phải là một trong {Y_MODES}")
    normalized = normalize_name(name)
    if not normalized:
        raise ValueError("Họ tên phải có ít nhất một chữ cái")

    words = []
    expression = soul = personality = 0
    for word in normalized.split(" "):
        letters = []
        for i, ch in enumerate(word):
            value = LETTER_VALUES[ch]
            vowel = _is_vowel(word, i, y_mode)
            expression += value
            if vowel:
                soul += value
            else:
                personality += value
            letters.append(
                {"letter": ch, "value": value, "kind": "vowel" if vowel else "consonant"}
            )
        words.append({"word": word, "letters": letters})

    return {
        "normalized": normalized,
        "words": words,
        "totals": {"expression": expression, "soul_urge": soul, "personality": personality},
    }


def expression_number(name: str, y_mode: str = "auto") -> int:
    """Số biểu đạt: tổng mọi chữ cái trong họ tên."""
    return reduce_number(analyze_name(name, y_mode)["totals"]["expression"])


def soul_urge_number(name: str, y_mode: str = "auto") -> int:
    """Số linh hồn: tổng các nguyên âm."""
    return reduce_number(analyze_name(name, y_mode)["totals"]["soul_urge"])


def personality_number(name: str, y_mode: str = "auto") -> int:
    """Số nhân cách: tổng các phụ âm."""
    return reduce_number(analyze_name(name, y_mode)["totals"]["personality"])


def life_path_parts(birth: date) -> tuple[int, int, int, int]:
    """Trả về (ngày đã rút gọn, tháng đã rút gọn, năm đã rút gọn, tổng ba số)."""
    day = reduce_number(birth.day)
    month = reduce_number(birth.month)
    year = reduce_number(sum(int(d) for d in str(birth.year)))
    return day, month, year, day + month + year


def life_path_number(birth: date) -> int:
    """Số chủ đạo (đường đời)."""
    return reduce_number(life_path_parts(birth)[3])


def birth_day_number(birth: date) -> int:
    """Số ngày sinh đã rút gọn (số gốc là birth.day)."""
    return reduce_number(birth.day)


def digital_root(n: int) -> int:
    """Rút về 1 chữ số (1-9), KHÔNG giữ số bậc thầy. 0 giữ nguyên 0."""
    return 0 if n == 0 else 1 + (n - 1) % 9


def attitude_number(birth: date) -> int:
    """Số Thái độ: ngày sinh rút gọn + tháng sinh rút gọn (giữ 11/22/33)."""
    return reduce_number(reduce_number(birth.day) + reduce_number(birth.month))


def maturity_number(full_name: str, birth: date, y_mode: str = "auto") -> int:
    """Số Trưởng thành: số chủ đạo + số biểu đạt (giữ 11/22/33)."""
    return reduce_number(life_path_number(birth) + expression_number(full_name, y_mode))


def personal_year(birth: date, year: int) -> dict:
    """Năm cá nhân của `year`.

    Mỗi thành phần (ngày, tháng, năm) rút về 1 chữ số trước khi cộng, nhờ đó
    chu kỳ năm này sang năm khác luôn tăng thêm 1 (9 -> 1).
    value  : kết quả giữ 11/22 nếu tổng đúng bằng 11/22.
    single : kết quả rút về 1-9, dùng để vẽ biểu đồ.
    """
    total = digital_root(birth.day) + digital_root(birth.month) + digital_root(year)
    value = reduce_number(total)
    return {
        "year": year,
        "value": value,
        "single": digital_root(total),
        "master": value in MASTER_NUMBERS,
    }


def personal_year_cycle(birth: date, center_year: int, span: int = 5) -> list[dict]:
    """Chu kỳ năm cá nhân từ center_year - span tới center_year + span.

    Bỏ các năm trước năm sinh (chưa sinh ra thì chưa có năm cá nhân).
    """
    first = max(center_year - span, birth.year)
    return [personal_year(birth, y) for y in range(first, center_year + span + 1)]


def calculate(full_name: str, birth_date: date, y_mode: str = "auto", year: int | None = None) -> dict:
    """Tính đủ các chỉ số, trả về dict sẵn sàng đóng gói thành JSON.

    year: năm dùng cho chu kỳ năm cá nhân; mặc định là năm hiện tại của máy chủ.
    """
    name = analyze_name(full_name, y_mode)
    totals = name["totals"]
    day, month, year_part, life_total = life_path_parts(birth_date)
    if year is None:
        year = date.today().year

    def indicator(total: int, parts: dict | None = None) -> dict:
        value = reduce_number(total)
        item = {"value": value, "total": total, "master": value in MASTER_NUMBERS}
        if parts is not None:
            item["parts"] = parts
        return item

    life = indicator(life_total, {"day": day, "month": month, "year": year_part})
    expression = indicator(totals["expression"])
    attitude_parts = {"day": reduce_number(birth_date.day), "month": reduce_number(birth_date.month)}
    maturity_parts = {"life_path": life["value"], "expression": expression["value"]}
    birth_day = reduce_number(birth_date.day)

    return {
        "method": {
            "letter_system": "pythagoras",
            "y_mode": y_mode,
            "master_numbers": list(MASTER_NUMBERS),
        },
        "input": {
            "full_name": full_name,
            "normalized_name": name["normalized"],
            "birth_date": birth_date.isoformat(),
        },
        "life_path": life,
        "expression": expression,
        "soul_urge": indicator(totals["soul_urge"]),
        "personality": indicator(totals["personality"]),
        "attitude": indicator(sum(attitude_parts.values()), attitude_parts),
        "maturity": indicator(sum(maturity_parts.values()), maturity_parts),
        "birth_day": {
            "value": birth_day,
            "day": birth_date.day,
            "master": birth_day in MASTER_NUMBERS,
        },
        "personal_year": {
            "year": year,
            "current": personal_year(birth_date, year),
            "cycle": personal_year_cycle(birth_date, year),
        },
        "name_breakdown": name["words"],
    }
