"""Bảng tra cứu tọa độ địa lý (Kinh độ, Vĩ độ) và múi giờ cho 63 tỉnh/thành Việt Nam và các thành phố quốc tế.

Không phụ thuộc API bên ngoài, hoạt động offline hoàn toàn, tra cứu tức thì theo chuỗi không dấu.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class LocationInfo:
    name: str
    latitude: float
    longitude: float
    timezone: str = "Asia/Ho_Chi_Minh"


def _normalize(s: str) -> str:
    """Chuẩn hóa chuỗi: chữ thường, bỏ dấu tiếng Việt, bỏ ký tự đặc biệt."""
    s = s.lower().strip()
    s = s.replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


# Danh bạ 63 tỉnh/thành Việt Nam (tọa độ trung tâm hành chính)
# Định dạng: từ khóa chuẩn hóa -> LocationInfo(Tên hiển thị, Vĩ độ Bắc, Kinh độ Đông)
VIETNAM_LOCATIONS: dict[str, LocationInfo] = {
    # Miền Bắc
    "ha noi": LocationInfo("Hà Nội", 21.028511, 105.854167),
    "hanoi": LocationInfo("Hà Nội", 21.028511, 105.854167),
    "hai phong": LocationInfo("Hải Phòng", 20.844912, 106.688084),
    "haiphong": LocationInfo("Hải Phòng", 20.844912, 106.688084),
    "quang ninh": LocationInfo("Quảng Ninh", 20.950454, 107.073357),
    "ha long": LocationInfo("Hạ Long", 20.950454, 107.073357),
    "hai duong": LocationInfo("Hải Dương", 20.937243, 106.314583),
    "hung yen": LocationInfo("Hưng Yên", 20.646171, 106.051125),
    "bac ninh": LocationInfo("Bắc Ninh", 21.186096, 106.076317),
    "bac giang": LocationInfo("Bắc Giang", 21.273078, 106.194603),
    "vinh phuc": LocationInfo("Vĩnh Phúc", 21.308944, 105.604935),
    "vinh yen": LocationInfo("Vĩnh Yên", 21.308944, 105.604935),
    "phu tho": LocationInfo("Phú Thọ", 21.322744, 105.401863),
    "viet tri": LocationInfo("Việt Trì", 21.322744, 105.401863),
    "thai nguyen": LocationInfo("Thái Nguyên", 21.594225, 105.848152),
    "tuyen quang": LocationInfo("Tuyên Quang", 21.823439, 105.214470),
    "yen bai": LocationInfo("Yên Bái", 21.716766, 104.911308),
    "lao cai": LocationInfo("Lào Cai", 22.485627, 103.970665),
    "sa pa": LocationInfo("Sa Pa", 22.336361, 103.843785),
    "ha giang": LocationInfo("Hà Giang", 22.823333, 104.983889),
    "cao bang": LocationInfo("Cao Bằng", 22.666667, 106.250000),
    "bac kan": LocationInfo("Bắc Kạn", 22.147028, 105.834833),
    "lang son": LocationInfo("Lạng Sơn", 21.853706, 106.762024),
    "hoa binh": LocationInfo("Hòa Bình", 20.817167, 105.337583),
    "son la": LocationInfo("Sơn La", 21.328333, 103.916667),
    "dien bien": LocationInfo("Điện Biên", 21.386944, 103.022778),
    "lai chau": LocationInfo("Lai Châu", 22.396111, 103.458889),
    "ha nam": LocationInfo("Hà Nam", 20.545361, 105.912667),
    "phu ly": LocationInfo("Phủ Lý", 20.545361, 105.912667),
    "nam dinh": LocationInfo("Nam Định", 20.434444, 106.168889),
    "ninh binh": LocationInfo("Ninh Bình", 20.250614, 105.974453),
    "thai binh": LocationInfo("Thái Bình", 20.446344, 106.336586),

    # Bắc Trung Bộ & Duyên hải miền Trung
    "thanh hoa": LocationInfo("Thanh Hóa", 19.806692, 105.785181),
    "nghe an": LocationInfo("Nghệ An", 18.673394, 105.681328),
    "vinh": LocationInfo("Vinh", 18.673394, 105.681328),
    "ha tinh": LocationInfo("Hà Tĩnh", 18.342978, 105.905817),
    "quang binh": LocationInfo("Quảng Bình", 17.469144, 106.622514),
    "dong hoi": LocationInfo("Đồng Hới", 17.469144, 106.622514),
    "quang tri": LocationInfo("Quảng Trị", 16.816667, 107.100000),
    "dong ha": LocationInfo("Đông Hà", 16.816667, 107.100000),
    "thua thien hue": LocationInfo("Thừa Thiên Huế", 16.463714, 107.590866),
    "hue": LocationInfo("Huế", 16.463714, 107.590866),
    "da nang": LocationInfo("Đà Nẵng", 16.054407, 108.202167),
    "danang": LocationInfo("Đà Nẵng", 16.054407, 108.202167),
    "quang nam": LocationInfo("Quảng Nam", 15.564756, 108.481544),
    "tam ky": LocationInfo("Tam Kỳ", 15.564756, 108.481544),
    "hoi an": LocationInfo("Hội An", 15.880058, 108.338047),
    "quang ngai": LocationInfo("Quảng Ngãi", 15.120469, 108.792275),
    "binh dinh": LocationInfo("Bình Định", 13.782967, 109.219664),
    "quy nhon": LocationInfo("Quy Nhơn", 13.782967, 109.219664),
    "phu yen": LocationInfo("Phú Yên", 13.088189, 109.314947),
    "tuy hoa": LocationInfo("Tuy Hòa", 13.088189, 109.314947),
    "khanh hoa": LocationInfo("Khánh Hòa", 12.238791, 109.196749),
    "nha trang": LocationInfo("Nha Trang", 12.238791, 109.196749),
    "cam ranh": LocationInfo("Cam Ranh", 11.921389, 109.159167),
    "ninh thuan": LocationInfo("Ninh Thuận", 11.565342, 108.995961),
    "phan rang": LocationInfo("Phan Rang", 11.565342, 108.995961),
    "binh thuan": LocationInfo("Bình Thuận", 10.927292, 108.101897),
    "phan thiet": LocationInfo("Phan Thiết", 10.927292, 108.101897),

    # Tây Nguyên
    "kon tum": LocationInfo("Kon Tum", 14.350000, 108.000000),
    "gia lai": LocationInfo("Gia Lai", 13.983333, 108.000000),
    "pleiku": LocationInfo("Pleiku", 13.983333, 108.000000),
    "dak lak": LocationInfo("Đắk Lắk", 12.666667, 108.050000),
    "buon ma thuot": LocationInfo("Buôn Ma Thuột", 12.666667, 108.050000),
    "dak nong": LocationInfo("Đắk Nông", 12.003333, 107.690833),
    "gia nghia": LocationInfo("Gia Nghĩa", 12.003333, 107.690833),
    "lam dong": LocationInfo("Lâm Đồng", 11.940419, 108.458313),
    "da lat": LocationInfo("Đà Lạt", 11.940419, 108.458313),
    "bao loc": LocationInfo("Bảo Lộc", 11.547500, 107.808056),

    # Đông Nam Bộ & TP. Hồ Chí Minh
    "ho chi minh": LocationInfo("TP. Hồ Chí Minh", 10.823099, 106.629664),
    "tp ho chi minh": LocationInfo("TP. Hồ Chí Minh", 10.823099, 106.629664),
    "tphcm": LocationInfo("TP. Hồ Chí Minh", 10.823099, 106.629664),
    "hcm": LocationInfo("TP. Hồ Chí Minh", 10.823099, 106.629664),
    "sai gon": LocationInfo("Sài Gòn", 10.823099, 106.629664),
    "saigon": LocationInfo("Sài Gòn", 10.823099, 106.629664),
    "gia dinh": LocationInfo("Gia Định", 10.823099, 106.629664),
    "ba ria": LocationInfo("Bà Rịa - Vũng Tàu", 10.496256, 107.168344),
    "vung tau": LocationInfo("Vũng Tàu", 10.345989, 107.084261),
    "dong nai": LocationInfo("Đồng Nai", 10.946006, 106.824397),
    "bien hoa": LocationInfo("Biên Hòa", 10.946006, 106.824397),
    "binh duong": LocationInfo("Bình Dương", 11.166667, 106.666667),
    "thu dau mot": LocationInfo("Thủ Dầu Một", 10.980486, 106.651878),
    "binh phuoc": LocationInfo("Bình Phước", 11.750000, 106.900000),
    "dong xoai": LocationInfo("Đồng Xoài", 11.533333, 106.883333),
    "tay ninh": LocationInfo("Tây Ninh", 11.310278, 106.098333),

    # Đồng bằng Sông Cửu Long (Miền Tây)
    "can tho": LocationInfo("Cần Thơ", 10.045162, 105.746857),
    "long an": LocationInfo("Long An", 10.536944, 106.411389),
    "tan an": LocationInfo("Tân An", 10.536944, 106.411389),
    "tien giang": LocationInfo("Tiền Giang", 10.428611, 106.341944),
    "my tho": LocationInfo("Mỹ Tho", 10.354444, 106.364444),
    "ben tre": LocationInfo("Bến Tre", 10.243333, 106.375556),
    "tra vinh": LocationInfo("Trà Vinh", 9.934722, 106.345833),
    "vinh long": LocationInfo("Vĩnh Long", 10.253611, 105.972222),
    "dong thap": LocationInfo("Đồng Tháp", 10.463889, 105.632778),
    "cao lanh": LocationInfo("Cao Lãnh", 10.463889, 105.632778),
    "sa dec": LocationInfo("Sa Đéc", 10.298056, 105.759444),
    "an giang": LocationInfo("An Giang", 10.383333, 105.416667),
    "long xuyen": LocationInfo("Long Xuyên", 10.383333, 105.416667),
    "chau doc": LocationInfo("Châu Đốc", 10.702778, 105.116667),
    "kien giang": LocationInfo("Kiên Giang", 10.012500, 105.080556),
    "rach gia": LocationInfo("Rạch Giá", 10.012500, 105.080556),
    "phu quoc": LocationInfo("Phú Quốc", 10.228889, 103.957222),
    "ha tien": LocationInfo("Hà Tiên", 10.383333, 104.483333),
    "hau giang": LocationInfo("Hậu Giang", 9.784444, 105.470000),
    "vi thanh": LocationInfo("Vị Thanh", 9.784444, 105.470000),
    "soc trang": LocationInfo("Sóc Trăng", 9.603333, 105.980000),
    "bac lieu": LocationInfo("Bạc Liêu", 9.294167, 105.727778),
    "ca mau": LocationInfo("Cà Mau", 9.176944, 105.150000),

    # Quốc tế thông dụng
    "paris": LocationInfo("Paris, Pháp", 48.856614, 2.352222, "Europe/Paris"),
    "london": LocationInfo("London, Anh", 51.507351, -0.127758, "Europe/London"),
    "new york": LocationInfo("New York, Mỹ", 40.712776, -74.005974, "America/New_York"),
    "los angeles": LocationInfo("Los Angeles, Mỹ", 34.052235, -118.243683, "America/Los_Angeles"),
    "tokyo": LocationInfo("Tokyo, Nhật Bản", 35.676192, 139.650311, "Asia/Tokyo"),
    "seoul": LocationInfo("Seoul, Hàn Quốc", 37.566535, 126.977969, "Asia/Seoul"),
    "beijing": LocationInfo("Bắc Kinh, Trung Quốc", 39.904200, 116.407396, "Asia/Shanghai"),
    "bac kinh": LocationInfo("Bắc Kinh, Trung Quốc", 39.904200, 116.407396, "Asia/Shanghai"),
    "shanghai": LocationInfo("Thượng Hải, Trung Quốc", 31.230416, 121.473701, "Asia/Shanghai"),
    "thuong hai": LocationInfo("Thượng Hải, Trung Quốc", 31.230416, 121.473701, "Asia/Shanghai"),
    "singapore": LocationInfo("Singapore", 1.352083, 103.819836, "Asia/Singapore"),
    "bangkok": LocationInfo("Bangkok, Thái Lan", 13.756331, 100.501765, "Asia/Bangkok"),
    "vientiane": LocationInfo("Viêng Chăn, Lào", 17.975706, 102.633104, "Asia/Vientiane"),
    "phnom penh": LocationInfo("Phnôm Pênh, Campuchia", 11.556374, 104.928210, "Asia/Phnom_Penh"),
    "sydney": LocationInfo("Sydney, Úc", -33.868820, 151.209296, "Australia/Sydney"),
    "berlin": LocationInfo("Berlin, Đức", 52.520008, 13.404954, "Europe/Berlin"),
    "moscow": LocationInfo("Moscow, Nga", 55.755826, 37.617300, "Europe/Moscow"),
}

# Điểm mặc định nếu không tra cứu được nơi sinh (Tọa độ Hà Nội)
DEFAULT_LOCATION = LocationInfo("Hà Nội (Mặc định)", 21.028511, 105.854167)


def resolve_location(birth_place: str) -> LocationInfo:
    """Tra cứu kinh độ, vĩ độ và tên chuẩn từ chuỗi người dùng nhập."""
    if not birth_place or not birth_place.strip():
        return DEFAULT_LOCATION

    norm = _normalize(birth_place)

    # 1. Khớp chính xác hoàn toàn
    if norm in VIETNAM_LOCATIONS:
        return VIETNAM_LOCATIONS[norm]

    # 2. Khớp từ khóa chứa trong chuỗi (ưu tiên từ khóa dài hơn trước)
    sorted_keys = sorted(VIETNAM_LOCATIONS.keys(), key=len, reverse=True)
    for k in sorted_keys:
        if k in norm:
            return VIETNAM_LOCATIONS[k]

    # Fallback mặc định
    return DEFAULT_LOCATION
