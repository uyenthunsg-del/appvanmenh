"""Engine Tử Vi Đẩu Số (Lá Số Tử Vi) chuẩn xác kinh điển Việt Nam.

Tính toán và an sao:
- Cung Mệnh, Cung Thân, 12 Cung Chức Năng (Địa Bàn).
- Ngũ Hành Cục (Thủy Nhị Cục, Mộc Tam Cục, Kim Tứ Cục, Thổ Ngũ Cục, Hỏa Lục Cục).
- Bản Mệnh, Âm Dương Nam/Nữ, Mệnh Cục tương sinh khắc, Âm Dương thuận nghịch lý.
- Chủ Mệnh, Chủ Thân.
- 14 Chính Tinh (Hệ Tử Vi, Hệ Thiên Phủ) kèm trạng thái Miếu, Vượng, Đắc, Hãm (M, V, Đ, H).
- Vòng Tràng Sinh (12 sao), Vòng Thái Tuế (12 sao), Vòng Bác Sĩ / Lộc Tồn (12 sao).
- Tứ Hóa: Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ.
- Lục Cát Tinh (Tả Phù, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt).
- Lục Sát Tinh (Kình Dương, Đà La, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp).
- 70+ Phụ tinh, bàng tinh quan trọng (Thiên Mã, Đào Hoa, Hồng Loan, v.v.).
- Sao Tuần Trung Không Vong và Triệt Lộ Không Vong.
- Đại Hạn (10 năm từng cung) và Tiểu Hạn.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Literal

import vietnamese_calendar as vc

# 12 Địa Chi theo thứ tự 0..11
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
BRANCH_ELEMENTS = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa", "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]

# 10 Thiên Can
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

# Tên 12 Cung chức năng chuẩn
PALACE_NAMES = [
    "Mệnh",
    "Phụ Mẫu",
    "Phúc Đức",
    "Điền Trạch",
    "Quan Lộc",
    "Nô Bộc",
    "Thiên Di",
    "Tật Ách",
    "Tài Bạch",
    "Tử Tức",
    "Phu Thê",
    "Huynh Đệ",
]

# Bảng trạng thái Miếu (M), Vượng (V), Đắc (Đ), Hãm (H), Bình (B) của 14 Chính Tinh tại 12 Cung (Tý..Hợi)
MAIN_STAR_BRIGHTNESS: dict[str, list[str]] = {
    # Tý, Sửu, Dần, Mão, Thìn, Tị, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi
    "Tử Vi":      ["B", "Đ", "M", "V", "Đ", "V", "M", "Đ", "M", "V", "Đ", "V"],
    "Thiên Cơ":   ["Đ", "H", "V", "M", "M", "B", "Đ", "H", "V", "M", "M", "B"],
    "Thái Dương": ["H", "Đ", "V", "M", "V", "V", "M", "Đ", "Đ", "H", "H", "H"],
    "Vũ Khúc":    ["V", "M", "V", "Đ", "M", "B", "V", "M", "V", "Đ", "M", "B"],
    "Thiên Đồng": ["V", "H", "M", "Đ", "B", "Đ", "H", "H", "V", "Đ", "B", "Đ"],
    "Liêm Trinh": ["B", "Đ", "V", "B", "M", "H", "V", "Đ", "V", "B", "M", "H"],
    "Thiên Phủ":  ["M", "M", "M", "Đ", "M", "Đ", "M", "M", "M", "Đ", "M", "Đ"],
    "Thái Âm":    ["M", "Đ", "H", "H", "H", "H", "H", "Đ", "Đ", "V", "M", "M"],
    "Tham Lang":  ["H", "M", "Đ", "B", "M", "H", "H", "M", "Đ", "B", "M", "H"],
    "Cự Môn":     ["V", "H", "V", "M", "H", "H", "V", "H", "V", "M", "H", "Đ"],
    "Thiên Tướng":["V", "Đ", "M", "H", "Đ", "Đ", "V", "Đ", "M", "H", "Đ", "Đ"],
    "Thiên Lương":["M", "V", "M", "M", "V", "H", "M", "V", "H", "Đ", "M", "H"],
    "Thất Sát":   ["M", "Đ", "M", "H", "B", "Đ", "M", "Đ", "M", "H", "B", "Đ"],
    "Phá Quân":   ["M", "V", "H", "H", "V", "Đ", "M", "V", "H", "H", "V", "Đ"],
}

# Ngũ Hành và Cát/Hung của từng sao
STAR_INFO: dict[str, dict[str, str]] = {
    # 14 Chính tinh
    "Tử Vi": {"element": "Thổ", "type": "chinh_tinh", "nature": "cat", "role": "Đế tinh, phúc lộc danh thọ"},
    "Thiên Cơ": {"element": "Mộc", "type": "chinh_tinh", "nature": "cat", "role": "Mưu trí, thiện tinh, mưu sĩ"},
    "Thái Dương": {"element": "Hỏa", "type": "chinh_tinh", "nature": "cat", "role": "Quang minh, danh vọng, cha/chồng"},
    "Vũ Khúc": {"element": "Kim", "type": "chinh_tinh", "nature": "cat", "role": "Tài tinh, dũng mãnh, tiền bạc"},
    "Thiên Đồng": {"element": "Thủy", "type": "chinh_tinh", "nature": "cat", "role": "Phúc tinh, an nhàn, hài hòa"},
    "Liêm Trinh": {"element": "Hỏa", "type": "chinh_tinh", "nature": "trung", "role": "Tù tinh, nghiêm nghị, đào hoa thứ"},
    "Thiên Phủ": {"element": "Thổ", "type": "chinh_tinh", "nature": "cat", "role": "Lệnh tinh, kho trời, quý phái"},
    "Thái Âm": {"element": "Thủy", "type": "chinh_tinh", "nature": "cat", "role": "Phú tinh, tài lộc, mẹ/vợ"},
    "Tham Lang": {"element": "Thủy", "type": "chinh_tinh", "nature": "trung", "role": "Đào hoa tinh, ham muốn, tài nghệ"},
    "Cự Môn": {"element": "Thủy", "type": "chinh_tinh", "nature": "trung", "role": "Ám tinh, ngôn ngữ, biện tài"},
    "Thiên Tướng": {"element": "Thủy", "type": "chinh_tinh", "nature": "cat", "role": "Ấn tinh, trung thực, công danh"},
    "Thiên Lương": {"element": "Mộc", "type": "chinh_tinh", "nature": "cat", "role": "Ấm tinh, thọ tinh, nguyên tắc"},
    "Thất Sát": {"element": "Kim", "type": "chinh_tinh", "nature": "trung", "role": "Quyền tinh, sát phạt, dũng khí"},
    "Phá Quân": {"element": "Thủy", "type": "chinh_tinh", "nature": "trung", "role": "Hao tinh, tiên phong, phá cũ tạo mới"},

    # Lục Cát Tinh
    "Tả Phù": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Phò trợ, bạn bè giúp đỡ"},
    "Hữu Bật": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Hỗ trợ, đồng lòng tương trợ"},
    "Văn Xương": {"element": "Kim", "type": "cat_tinh", "nature": "cat", "role": "Văn chương, thi cử đỗ đạt"},
    "Văn Khúc": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Tài nghệ, ăn nói, nghệ thuật"},
    "Thiên Khôi": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Đứng đầu, quý nhân tương trợ"},
    "Thiên Việt": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Khôi việt, ngầm giúp đỡ, bề trên nâng đỡ"},

    # Lục Sát Tinh
    "Kình Dương": {"element": "Kim", "type": "sat_tinh", "nature": "hung", "role": "Hung bạo, cương trực, va chạm"},
    "Đà La": {"element": "Kim", "type": "sat_tinh", "nature": "hung", "role": "Trì trệ, trở ngại, kéo dài"},
    "Hỏa Tinh": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Nóng nảy, phát tác nhanh, tai họa bất ngờ"},
    "Linh Tinh": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Trầm uất, mờ ám, âm thầm bộc phát"},
    "Địa Không": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Hư vô, mất mát, ngộ đạo, cách tân"},
    "Địa Kiếp": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Trắc trở, cướp đoạt, thăng trầm sóng gió"},

    # Tứ Hóa
    "Hóa Lộc": {"element": "Mộc", "type": "tu_hoa", "nature": "cat", "role": "Tài lộc, may mắn, thuận lợi dồi dào"},
    "Hóa Quyền": {"element": "Mộc", "type": "tu_hoa", "nature": "cat", "role": "Quyền uy, chủ động, chỉ huy nắm quyền"},
    "Hóa Khoa": {"element": "Thủy", "type": "tu_hoa", "nature": "cat", "role": "Danh tiếng, khoa bảng, cứu giải tai ách"},
    "Hóa Kỵ": {"element": "Thủy", "type": "tu_hoa", "nature": "hung", "role": "Thị phi, trở ngại, trói buộc, lo âu"},

    # Lộc Tồn & Vòng Bác Sĩ
    "Lộc Tồn": {"element": "Thổ", "type": "phu_tinh", "nature": "cat", "role": "Lộc trời ban, bảo trợ tài chính vững chắc"},
    "Bác Sĩ": {"element": "Thủy", "type": "phu_tinh", "nature": "cat", "role": "Thông minh, hiểu biết, nho nhã"},
    "Lực Sĩ": {"element": "Hỏa", "type": "phu_tinh", "nature": "cat", "role": "Sức lực dồi dào, hăng hái"},
    "Thanh Long": {"element": "Thủy", "type": "phu_tinh", "nature": "cat", "role": "May mắn, vui vẻ, giải trừ xui xẻo"},
    "Tiểu Hao": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Hao tán tiền bạc nhỏ, chi tiêu nhiều"},
    "Tướng Quân": {"element": "Mộc", "type": "phu_tinh", "nature": "cat", "role": "Oai phong, can đảm, tinh thần tiên phong"},
    "Tấu Thư": {"element": "Kim", "type": "phu_tinh", "nature": "cat", "role": "Khéo ăn nói, giấy tờ bằng cấp thuận lợi"},
    "Phi Liêm": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Nhanh chóng, bay nhảy, thị phi bất ngờ"},
    "Hỷ Thần": {"element": "Hỏa", "type": "phu_tinh", "nature": "cat", "role": "Tin vui, hỷ sự, tiếng cười"},
    "Bệnh Phù": {"element": "Thổ", "type": "phu_tinh", "nature": "hung", "role": "Đau ốm, mệt mỏi, hao mòn thể lực"},
    "Đại Hao": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Hao tốn lớn, biến động tài chính mạnh"},
    "Phục Binh": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Tiểu nhân rình rập, ngấm ngầm cản trở"},
    "Quan Phủ (BS)": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Cửa quan, kiện tụng rắc rối"},

    # Vòng Thái Tuế
    "Thái Tuế": {"element": "Hỏa", "type": "phu_tinh", "nature": "trung", "role": "Chính danh, đạo đức, nói năng khẳng khái"},
    "Thiếu Dương": {"element": "Hỏa", "type": "phu_tinh", "nature": "cat", "role": "Thông minh, vui vẻ, hướng thượng"},
    "Tang Môn": {"element": "Mộc", "type": "phu_tinh", "nature": "hung", "role": "Buồn bã, tang chế, suy tư lo âu"},
    "Thiếu Âm": {"element": "Thủy", "type": "phu_tinh", "nature": "cat", "role": "Nhu hòa, nhường nhịn, nhân từ"},
    "Quan Phù (TT)": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Pháp luật, lý lẽ, tranh chấp"},
    "Tử Phù": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Buồn bực, trở ngại nhỏ"},
    "Tuế Phá": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Chống đối, bất mãn, ngang bướng"},
    "Long Đức": {"element": "Thủy", "type": "phu_tinh", "nature": "cat", "role": "Đức độ, phúc hậu, giải ách"},
    "Bạch Hổ": {"element": "Kim", "type": "phu_tinh", "nature": "hung", "role": "Mạnh mẽ, quả cảm, tai nạn huyết quang"},
    "Phúc Đức": {"element": "Thổ", "type": "phu_tinh", "nature": "cat", "role": "Phước lành, thiện tâm, từ hòa"},
    "Điếu Khách": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Nói nhiều, cờ bạc ham chơi, phân trần"},
    "Trực Phù": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Thiệt thòi, ngay thẳng chịu phần kém"},

    # Vòng Tràng Sinh
    "Trường Sinh": {"element": "Thủy", "type": "trang_sinh", "nature": "cat", "role": "Sinh sôi, dồi dào sức sống, khởi đầu thuận"},
    "Mộc Dục": {"element": "Thủy", "type": "trang_sinh", "nature": "trung", "role": "Tắm gội, tình cảm phong phú, thích làm đẹp"},
    "Quan Đới": {"element": "Kim", "type": "trang_sinh", "nature": "cat", "role": "Trưởng thành, danh vị, gánh vác trách nhiệm"},
    "Lâm Quan": {"element": "Kim", "type": "trang_sinh", "nature": "cat", "role": "Thời kỳ làm việc, đắc tài đắc lộc"},
    "Đế Vượng": {"element": "Kim", "type": "trang_sinh", "nature": "cat", "role": "Đỉnh cao phong độ, cường tráng vượng thịnh"},
    "Suy": {"element": "Thủy", "type": "trang_sinh", "nature": "trung", "role": "Bớt hăng say, hướng nội, giữ gìn"},
    "Bệnh": {"element": "Hỏa", "type": "trang_sinh", "nature": "hung", "role": "Suy yếu, ốm mệt, thiếu nhuệ khí"},
    "Tử": {"element": "Hỏa", "type": "trang_sinh", "nature": "hung", "role": "Trầm lắng, suy ngẫm sâu kín"},
    "Mộ": {"element": "Thổ", "type": "trang_sinh", "nature": "trung", "role": "Chôn cất, tích trữ, kín kẽ gìn giữ"},
    "Tuyệt": {"element": "Thổ", "type": "trang_sinh", "nature": "hung", "role": "Khô cạn, dứt đoạn, chuyển giao"},
    "Thai": {"element": "Kim", "type": "trang_sinh", "nature": "cat", "role": "Ấp ủ, thụ thai, hình thành dự định"},
    "Dưỡng": {"element": "Mộc", "type": "trang_sinh", "nature": "cat", "role": "Nuôi dưỡng, tích lũy nội lực sẵn sàng"},

    # Cát tinh & Phụ tinh khác
    "Thiên Mã": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Năng động, di chuyển, thành công phương xa"},
    "Đào Hoa": {"element": "Mộc", "type": "cat_tinh", "nature": "cat", "role": "Duyên dáng, thu hút, tài hoa nghệ thuật"},
    "Hồng Loan": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Hôn nhân, nhân duyên tốt, xinh đẹp"},
    "Thiên Hỷ": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Vui vẻ, may mắn, cưới xin sinh con"},
    "Hoa Cái": {"element": "Kim", "type": "cat_tinh", "nature": "cat", "role": "Thanh cao, lọng che quý giá, tâm linh"},
    "Long Trì": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Ao rồng, thanh tú, may mắn thi cử"},
    "Phượng Các": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Gác phượng, nho nhã, nhà cửa đẹp"},
    "Giải Thần": {"element": "Mộc", "type": "cat_tinh", "nature": "cat", "role": "Giải trừ hung họa, cứu khốn phò nguy"},
    "Thiên Quan": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Quý nhân che chở, phúc thiện giải tai"},
    "Thiên Phúc": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Phúc đức từ tâm, bình an hóa cát"},
    "Quốc Ấn": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Ấn tín quốc gia, chức vụ bằng sắc"},
    "Đường Phù": {"element": "Mộc", "type": "cat_tinh", "nature": "cat", "role": "Oai vệ, dinh thự, thế đứng vững"},
    "Thiên Đức": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Ân đức trời ban, hóa giải tai nạn"},
    "Nguyệt Đức": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Phúc hậu đoan trang, gặp dữ hóa lành"},
    "Tam Thai": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Thuận buồm xuôi gió, danh vị cao"},
    "Bát Tọa": {"element": "Mộc", "type": "cat_tinh", "nature": "cat", "role": "Ổn định, vị trí vững vàng êm ấm"},
    "Ân Quang": {"element": "Mộc", "type": "cat_tinh", "nature": "cat", "role": "Ơn sâu nghĩa nặng, quý nhân phù hộ"},
    "Thiên Quý": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Trời thương người mến, cứu độ tai ách"},
    "Thai Phụ": {"element": "Kim", "type": "cat_tinh", "nature": "cat", "role": "Giúp đỡ, văn bằng khen tặng"},
    "Phong Cáo": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Ban khen, thăng chức, ban thưởng"},
    "Thiên Giải": {"element": "Hỏa", "type": "cat_tinh", "nature": "cat", "role": "Hóa giải tai ách, gặp may"},
    "Địa Giải": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Hóa giải điền trạch, an hòa"},
    "Thiên Y": {"element": "Thủy", "type": "cat_tinh", "nature": "cat", "role": "Thầy thuốc, sức khỏe, giải bệnh"},
    "Thiên Trù": {"element": "Thổ", "type": "cat_tinh", "nature": "cat", "role": "Bếp trời, ẩm thực sành điệu, tài lộc ăn uống"},

    # Hung tinh & Bại tinh khác
    "Thiên Hình": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Kỷ luật, pháp luật, mổ xẻ tổn thương"},
    "Thiên Riêu": {"element": "Thủy", "type": "phu_tinh", "nature": "hung", "role": "Mê muội, phong lưu, huyền thuật dị đoan"},
    "Thiên Khốc": {"element": "Thủy", "type": "phu_tinh", "nature": "hung", "role": "Tiếng khóc, đau buồn, lo nghĩ than thở"},
    "Thiên Hư": {"element": "Thủy", "type": "phu_tinh", "nature": "hung", "role": "Hư hao, giả tạo, lo lắng viển vông"},
    "Kiếp Sát": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Sát khí, hung bạo, cản trở bất ngờ"},
    "Phá Toái": {"element": "Hỏa", "type": "phu_tinh", "nature": "hung", "role": "Đổ vỡ, ngăn trở, việc dở dang"},
    "Cô Thần": {"element": "Thổ", "type": "phu_tinh", "nature": "hung", "role": "Cô độc, khó gần, khép kín tâm sự"},
    "Quả Tú": {"element": "Thổ", "type": "phu_tinh", "nature": "hung", "role": "Lẻ loi, gìn giữ cô quạnh, trắc trở tình duyên"},
    "Lưu Hà": {"element": "Thủy", "type": "phu_tinh", "nature": "hung", "role": "Sông nước, tai nạn thủy nạn, đổ máu"},
    "Thiên Không": {"element": "Hỏa", "type": "sat_tinh", "nature": "hung", "role": "Sắc sắc không không, ngộ đạo, thăng trầm lớn"},
}

# Bảng Tứ Hóa chuẩn theo Can năm (Tử Vi Nam Phái / Toàn Thư)
TU_HOA_TABLE: dict[str, dict[str, str]] = {
    "Giáp": {"Hóa Lộc": "Liêm Trinh", "Hóa Quyền": "Phá Quân", "Hóa Khoa": "Vũ Khúc", "Hóa Kỵ": "Thái Dương"},
    "Ất":   {"Hóa Lộc": "Thiên Cơ",   "Hóa Quyền": "Thiên Lương", "Hóa Khoa": "Tử Vi",   "Hóa Kỵ": "Thái Âm"},
    "Bính": {"Hóa Lộc": "Thiên Đồng", "Hóa Quyền": "Thiên Cơ",   "Hóa Khoa": "Văn Xương", "Hóa Kỵ": "Liêm Trinh"},
    "Đinh": {"Hóa Lộc": "Thái Âm",    "Hóa Quyền": "Thiên Đồng", "Hóa Khoa": "Thiên Cơ",  "Hóa Kỵ": "Cự Môn"},
    "Mậu":  {"Hóa Lộc": "Tham Lang",  "Hóa Quyền": "Thái Âm",    "Hóa Khoa": "Hữu Bật",   "Hóa Kỵ": "Thiên Cơ"},
    "Kỷ":   {"Hóa Lộc": "Vũ Khúc",    "Hóa Quyền": "Tham Lang",  "Hóa Khoa": "Thiên Lương", "Hóa Kỵ": "Văn Khúc"},
    "Canh": {"Hóa Lộc": "Thái Dương", "Hóa Quyền": "Vũ Khúc",    "Hóa Khoa": "Thái Âm",   "Hóa Kỵ": "Thiên Đồng"},
    "Tân":  {"Hóa Lộc": "Cự Môn",     "Hóa Quyền": "Thái Dương", "Hóa Khoa": "Văn Khúc",  "Hóa Kỵ": "Văn Xương"},
    "Nhâm": {"Hóa Lộc": "Thiên Lương", "Hóa Quyền": "Tử Vi",     "Hóa Khoa": "Tả Phù",    "Hóa Kỵ": "Vũ Khúc"},
    "Quý":  {"Hóa Lộc": "Phá Quân",   "Hóa Quyền": "Cự Môn",     "Hóa Khoa": "Thái Âm",   "Hóa Kỵ": "Tham Lang"},
}

# Sao Chủ Mệnh theo Chi năm
CHU_MENH = {
    0: "Tham Lang",   # Tý
    1: "Cự Môn",       # Sửu
    2: "Lộc Tồn",      # Dần
    3: "Văn Khúc",     # Mão
    4: "Liêm Trinh",   # Thìn
    5: "Vũ Khúc",      # Tị
    6: "Phá Quân",     # Ngọ
    7: "Vũ Khúc",      # Mùi
    8: "Liêm Trinh",   # Thân
    9: "Văn Khúc",     # Dậu
    10: "Lộc Tồn",     # Tuất
    11: "Cự Môn",      # Hợi
}

# Sao Chủ Thân theo Chi năm
CHU_THAN = {
    0: "Hỏa Tinh",     # Tý
    1: "Thiên Tướng",  # Sửu
    2: "Thiên Lương",  # Dần
    3: "Thiên Đồng",   # Mão
    4: "Văn Xương",    # Thìn
    5: "Thiên Cơ",     # Tị
    6: "Hỏa Tinh",     # Ngọ
    7: "Thiên Tướng",  # Mùi
    8: "Thiên Lương",  # Thân
    9: "Thiên Đồng",   # Dậu
    10: "Văn Xương",   # Tuất
    11: "Thiên Cơ",    # Hợi
}


@dataclass
class StarInstance:
    name: str
    element: str
    star_type: str       # chinh_tinh, cat_tinh, sat_tinh, tu_hoa, phu_tinh, trang_sinh
    nature: str          # cat, hung, trung
    brightness: str = "" # M, V, Đ, H, B (cho chính tinh)
    modifier: str = ""   # vd: [Hóa Lộc], [Hóa Quyền]
    role: str = ""


@dataclass
class PalaceData:
    index: int                  # 0..11 tương ứng chi Tý..Hợi
    branch: str                 # Tý..Hợi
    stem: str                   # Can của cung
    palace_name: str            # Mệnh, Phụ Mẫu...
    is_body: bool = False       # Cung Thân đóng tại đây?
    dai_han: str = ""           # Khoảng tuổi đại hạn (vd: 22 - 31)
    tieu_han: str = ""          # Chi tiểu hạn tại cung này
    stars: list[StarInstance] = field(default_factory=list)
    tuan_khong: bool = False    # Bị Tuần án ngữ?
    triet_khong: bool = False   # Bị Triệt án ngữ?


def calculate_tuvi(
    full_name: str,
    gender: Literal["male", "female"],
    birth_date: date,
    birth_time: time | None = None,
    birth_place: str = "",
    zi_mode: Literal["next_day", "early_late"] = "next_day",
) -> dict[str, Any]:
    """Tính toán toàn bộ Lá Số Tử Vi Đẩu Số."""
    # 1. Tính thông tin Âm Lịch và Can Chi
    lunar = vc.calculate_lunar_info(birth_date, birth_time, time_zone=7.0, zi_mode=zi_mode)

    stem_year_idx = (lunar.year + 6) % 10
    branch_year_idx = (lunar.year + 8) % 12
    lunar_month = lunar.month
    lunar_day = lunar.day
    hour_idx = vc.get_hour_branch_index(birth_time, zi_mode)

    # 2. Âm Dương Nam/Nữ
    is_yang_stem = (stem_year_idx % 2 == 0)
    yin_yang_gender = ""
    if gender == "male":
        yin_yang_gender = "Dương Nam" if is_yang_stem else "Âm Nam"
        is_thuan_ly = is_yang_stem
    else:
        yin_yang_gender = "Dương Nữ" if is_yang_stem else "Âm Nữ"
        is_thuan_ly = not is_yang_stem

    thuan_ly_text = "Âm Dương thuận lý (Dương Nam / Âm Nữ: cuộc đời thuận lợi, thời thế trợ lực)" if is_thuan_ly else "Âm Dương nghịch lý (Âm Nam / Dương Nữ: nhiều thử thách tôi luyện, tự lập thành công)"

    # 3. Xác định Cung MỆNH và Cung THÂN
    # Khởi từ Dần (chi index = 2) là tháng 1, đếm thuận đến tháng sinh:
    pos_month = (2 + (lunar_month - 1)) % 12
    # Từ đó đếm nghịch đến giờ sinh là Cung MỆNH:
    pos_menh = (pos_month - hour_idx) % 12
    # Đếm thuận đến giờ sinh là Cung THÂN:
    pos_than = (pos_month + hour_idx) % 12

    # Tên cung Thân cư
    body_palace_lookup = {
        0: "Thân Mệnh đồng cung",
        1: "Thân cư Phúc Đức",
        2: "Thân cư Quan Lộc",
        3: "Thân cư Thiên Di",
        4: "Thân cư Tài Bạch",
        5: "Thân cư Phu Thê",
        6: "Thân Mệnh đồng cung",
        7: "Thân cư Phúc Đức",
        8: "Thân cư Quan Lộc",
        9: "Thân cư Thiên Di",
        10: "Thân cư Tài Bạch",
        11: "Thân cư Phu Thê",
    }
    body_placement_name = body_palace_lookup.get(hour_idx, "Thân Mệnh đồng cung")

    # 4. Xác định Can của 12 Cung (theo Ngũ Hổ Độn)
    # Khởi tại Dần (chi 2):
    start_dan_stem = ((stem_year_idx % 5) * 2 + 2) % 10
    palace_stems = {}
    for b_idx in range(12):
        dist = (b_idx - 2) % 12
        palace_stems[b_idx] = STEMS[(start_dan_stem + dist) % 10]

    # 5. Xác định CỤC (Ngũ Hành Cục)
    # Cục tính theo Nạp Âm của Can Chi Cung Mệnh
    menh_stem = palace_stems[pos_menh]
    menh_branch = BRANCHES[pos_menh]
    menh_nayin = vc.NA_YIN.get((menh_stem, menh_branch), "Thủy")

    cuc_name = ""
    cuc_num = 2
    cuc_element = "Thủy"
    if "Thủy" in menh_nayin:
        cuc_name = "Thủy Nhị Cục"
        cuc_num = 2
        cuc_element = "Thủy"
    elif "Mộc" in menh_nayin:
        cuc_name = "Mộc Tam Cục"
        cuc_num = 3
        cuc_element = "Mộc"
    elif "Kim" in menh_nayin:
        cuc_name = "Kim Tứ Cục"
        cuc_num = 4
        cuc_element = "Kim"
    elif "Thổ" in menh_nayin:
        cuc_name = "Thổ Ngũ Cục"
        cuc_num = 5
        cuc_element = "Thổ"
    elif "Hỏa" in menh_nayin:
        cuc_name = "Hỏa Lục Cục"
        cuc_num = 6
        cuc_element = "Hỏa"

    # Mệnh Cục Tương Sinh / Tương Khắc
    menh_element = ""
    for elem in ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]:
        if elem in lunar.na_yin_year:
            menh_element = elem
            break

    sinh_map = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    khac_map = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}

    menh_cuc_relation = ""
    if menh_element == cuc_element:
        menh_cuc_relation = "Mệnh Cục Tương Hòa (Bản mệnh và hoàn cảnh hòa hợp, bình ổn)"
    elif sinh_map.get(cuc_element) == menh_element:
        menh_cuc_relation = "Cục sinh Mệnh (Rất tốt: Hoàn cảnh, thời thế nâng đỡ bản mệnh)"
    elif sinh_map.get(menh_element) == cuc_element:
        menh_cuc_relation = "Mệnh sinh Cục (Hao tổn tâm lực cho công việc, tha nhân nhưng lập nghiệp vững)"
    elif khac_map.get(menh_element) == cuc_element:
        menh_cuc_relation = "Mệnh khắc Cục (Vượt khó đi lên, tự thân vận động nắm giữ vận mệnh)"
    else:
        menh_cuc_relation = "Cục khắc Mệnh (Hoàn cảnh nhiều trở lực, cần rèn luyện bản lĩnh kiên cường)"

    # 6. Khởi tạo 12 Cung chức năng
    palaces: list[PalaceData] = []
    # Từ Cung Mệnh, đi NGHỊCH 12 cung chức năng:
    palace_assignment = {}
    for i, p_name in enumerate(PALACE_NAMES):
        b_idx = (pos_menh - i) % 12
        palace_assignment[b_idx] = p_name

    for b_idx in range(12):
        palaces.append(
            PalaceData(
                index=b_idx,
                branch=BRANCHES[b_idx],
                stem=palace_stems[b_idx],
                palace_name=palace_assignment[b_idx],
                is_body=(b_idx == pos_than),
            )
        )

    # 7. Tính vị trí sao TỬ VI
    # Quy tắc chuẩn:
    c = cuc_num
    d = lunar_day
    if d % c == 0:
        x = d // c
        k = 0
        pos_tuvi = (2 + (x - 1)) % 12
    else:
        k = c - (d % c)
        x = (d + k) // c
        if k % 2 == 1:
            pos_tuvi = (2 + (x - 1) - k) % 12
        else:
            pos_tuvi = (2 + (x - 1) + k) % 12

    # 8. An 14 Chính Tinh
    # Hệ Tử Vi (đi NGHỊCH)
    tuvi_system = {
        "Tử Vi": pos_tuvi,
        "Thiên Cơ": (pos_tuvi - 1) % 12,
        "Thái Dương": (pos_tuvi - 3) % 12,
        "Vũ Khúc": (pos_tuvi - 4) % 12,
        "Thiên Đồng": (pos_tuvi - 5) % 12,
        "Liêm Trinh": (pos_tuvi - 8) % 12,
    }

    # Thiên Phủ đối xứng qua trục Dần (2) - Thân (8): (4 - pos_tuvi) % 12
    pos_thienphu = (4 - pos_tuvi) % 12
    # Hệ Thiên Phủ (đi THUẬN)
    thienphu_system = {
        "Thiên Phủ": pos_thienphu,
        "Thái Âm": (pos_thienphu + 1) % 12,
        "Tham Lang": (pos_thienphu + 2) % 12,
        "Cự Môn": (pos_thienphu + 3) % 12,
        "Thiên Tướng": (pos_thienphu + 4) % 12,
        "Thiên Lương": (pos_thienphu + 5) % 12,
        "Thất Sát": (pos_thienphu + 6) % 12,
        "Phá Quân": (pos_thienphu + 10) % 12,
    }

    all_main_stars = {**tuvi_system, **thienphu_system}

    # Tứ Hóa can năm
    year_stem_str = STEMS[stem_year_idx]
    tu_hoa_map = TU_HOA_TABLE.get(year_stem_str, {})
    # Tạo ngược map từ Tên Sao -> Tên Hóa
    star_to_hoa = {star: hoa for hoa, star in tu_hoa_map.items()}

    for star_name, b_pos in all_main_stars.items():
        brightness = MAIN_STAR_BRIGHTNESS[star_name][b_pos]
        modifier = f"[{star_to_hoa[star_name]}]" if star_name in star_to_hoa else ""
        info = STAR_INFO.get(star_name, {})
        palaces[b_pos].stars.append(
            StarInstance(
                name=star_name,
                element=info.get("element", "Thổ"),
                star_type="chinh_tinh",
                nature=info.get("nature", "cat"),
                brightness=brightness,
                modifier=modifier,
                role=info.get("role", ""),
            )
        )

    # 9. Vòng Tràng Sinh (12 sao)
    # Khởi điểm: Thủy/Thổ khởi Thân(8), Mộc khởi Hợi(11), Kim khởi Tị(5), Hỏa khởi Dần(2)
    start_trangsinh = {
        "Thủy": 8,
        "Thổ": 8,
        "Mộc": 11,
        "Kim": 5,
        "Hỏa": 2,
    }[cuc_element]

    step_trangsinh = 1 if is_thuan_ly else -1
    trangsinh_names = [
        "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng",
        "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"
    ]
    for i, ts_name in enumerate(trangsinh_names):
        b_pos = (start_trangsinh + i * step_trangsinh) % 12
        info = STAR_INFO.get(ts_name, {})
        palaces[b_pos].stars.append(
            StarInstance(
                name=ts_name,
                element=info.get("element", "Thủy"),
                star_type="trang_sinh",
                nature=info.get("nature", "cat"),
                role=info.get("role", ""),
            )
        )

    # 10. Vòng Thái Tuế (12 sao theo Chi năm)
    pos_thaitue = branch_year_idx
    thaitue_names = [
        "Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù (TT)",
        "Tử Phù", "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù"
    ]
    for i, tt_name in enumerate(thaitue_names):
        b_pos = (pos_thaitue + i) % 12
        info = STAR_INFO.get(tt_name, {})
        display_name = tt_name.replace(" (TT)", "")
        palaces[b_pos].stars.append(
            StarInstance(
                name=display_name,
                element=info.get("element", "Hỏa"),
                star_type="phu_tinh",
                nature=info.get("nature", "cat"),
                role=info.get("role", ""),
            )
        )

    # 11. Vòng Lộc Tồn / Bác Sĩ (12 sao theo Can năm)
    loc_ton_pos_table = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0]
    pos_locton = loc_ton_pos_table[stem_year_idx]

    info_lt = STAR_INFO.get("Lộc Tồn", {})
    palaces[pos_locton].stars.append(
        StarInstance(
            name="Lộc Tồn",
            element=info_lt.get("element", "Thổ"),
            star_type="cat_tinh",
            nature="cat",
            role=info_lt.get("role", ""),
        )
    )

    # Kình Dương (tiến 1), Đà La (lùi 1)
    pos_kinhduong = (pos_locton + 1) % 12
    pos_dala = (pos_locton - 1) % 12
    info_kd = STAR_INFO.get("Kình Dương", {})
    info_dl = STAR_INFO.get("Đà La", {})
    palaces[pos_kinhduong].stars.append(
        StarInstance(name="Kình Dương", element=info_kd.get("element", "Kim"), star_type="sat_tinh", nature="hung", role=info_kd.get("role", ""))
    )
    palaces[pos_dala].stars.append(
        StarInstance(name="Đà La", element=info_dl.get("element", "Kim"), star_type="sat_tinh", nature="hung", role=info_dl.get("role", ""))
    )

    # Vòng Bác Sĩ (12 sao)
    step_bacsi = 1 if is_thuan_ly else -1
    bacsi_names = [
        "Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao", "Tướng Quân", "Tấu Thư",
        "Phi Liêm", "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ (BS)"
    ]
    for i, bs_name in enumerate(bacsi_names):
        b_pos = (pos_locton + i * step_bacsi) % 12
        info = STAR_INFO.get(bs_name, {})
        display_name = bs_name.replace(" (BS)", "")
        palaces[b_pos].stars.append(
            StarInstance(
                name=display_name,
                element=info.get("element", "Thủy"),
                star_type="phu_tinh",
                nature=info.get("nature", "cat"),
                role=info.get("role", ""),
            )
        )

    # 12. Lục Cát Tinh
    # Tả Phù (Thìn khởi 1, thuận): (4 + (lunar_month - 1)) % 12
    pos_taphu = (4 + (lunar_month - 1)) % 12
    # Hữu Bật (Tuất khởi 1, nghịch): (10 - (lunar_month - 1)) % 12
    pos_huubat = (10 - (lunar_month - 1)) % 12
    # Văn Xương (Tuất khởi Tý, nghịch): (10 - hour_idx) % 12
    pos_vanxuong = (10 - hour_idx) % 12
    # Văn Khúc (Thìn khởi Tý, thuận): (4 + hour_idx) % 12
    pos_vankhuc = (4 + hour_idx) % 12

    # Thiên Khôi, Thiên Việt (theo Can năm)
    khoi_viet_table = [
        (1, 7),  # Giáp: Sửu (Khôi), Mùi (Việt)
        (0, 8),  # Ất: Tý, Thân
        (11, 9), # Bính: Hợi, Dậu
        (11, 9), # Đinh: Hợi, Dậu
        (1, 7),  # Mậu: Sửu, Mùi
        (0, 8),  # Kỷ: Tý, Thân
        (6, 2),  # Canh: Ngọ, Dần
        (6, 2),  # Tân: Ngọ, Dần
        (3, 5),  # Nhâm: Mão, Tị
        (3, 5),  # Quý: Mão, Tị
    ]
    pos_khoi, pos_viet = khoi_viet_table[stem_year_idx]

    cat_tinh_list = [
        ("Tả Phù", pos_taphu),
        ("Hữu Bật", pos_huubat),
        ("Văn Xương", pos_vanxuong),
        ("Văn Khúc", pos_vankhuc),
        ("Thiên Khôi", pos_khoi),
        ("Thiên Việt", pos_viet),
    ]
    for c_name, b_pos in cat_tinh_list:
        modifier = f"[{star_to_hoa[c_name]}]" if c_name in star_to_hoa else ""
        info = STAR_INFO.get(c_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=c_name, element=info.get("element", "Thủy"), star_type="cat_tinh", nature="cat", modifier=modifier, role=info.get("role", ""))
        )

    # 13. Lục Sát Tinh
    # Địa Không (Hợi nghịch): (11 - hour_idx) % 12
    pos_diakhong = (11 - hour_idx) % 12
    # Địa Kiếp (Hợi thuận): (11 + hour_idx) % 12
    pos_diakiep = (11 + hour_idx) % 12

    # Hỏa Tinh, Linh Tinh
    # Khởi điểm Hỏa Tinh / Linh Tinh theo Tam Hợp Chi năm:
    # Dần Ngọ Tuất: Hỏa Sửu(1), Linh Mão(3)
    # Thân Tý Thìn: Hỏa Dần(2), Linh Tuất(10)
    # Tị Dậu Sửu: Hỏa Mão(3), Linh Tuất(10)
    # Hợi Mão Mùi: Hỏa Dậu(9), Linh Tuất(10)
    hoa_linh_starts = {
        2: (1, 3), 6: (1, 3), 10: (1, 3),
        0: (2, 10), 4: (2, 10), 8: (2, 10),
        1: (3, 10), 5: (3, 10), 9: (3, 10),
        3: (9, 10), 7: (9, 10), 11: (9, 10),
    }
    start_hoa, start_linh = hoa_linh_starts[branch_year_idx]
    if is_thuan_ly:
        pos_hoatinh = (start_hoa + hour_idx) % 12
        pos_linhtinh = (start_linh - hour_idx) % 12
    else:
        pos_hoatinh = (start_hoa - hour_idx) % 12
        pos_linhtinh = (start_linh + hour_idx) % 12

    sat_tinh_list = [
        ("Địa Không", pos_diakhong),
        ("Địa Kiếp", pos_diakiep),
        ("Hỏa Tinh", pos_hoatinh),
        ("Linh Tinh", pos_linhtinh),
    ]
    for s_name, b_pos in sat_tinh_list:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Hỏa"), star_type="sat_tinh", nature="hung", role=info.get("role", ""))
        )

    # 14. Các Phụ Tinh theo Chi Năm
    # Thiên Mã (Tam hợp): Dần Ngọ Tuất -> Thân(8); Thân Tý Thìn -> Dần(2); Tị Dậu Sửu -> Hợi(11); Hợi Mão Mùi -> Tị(5)
    ma_table = {2: 8, 6: 8, 10: 8, 0: 2, 4: 2, 8: 2, 1: 11, 5: 11, 9: 11, 3: 5, 7: 5, 11: 5}
    pos_thienma = ma_table[branch_year_idx]

    # Hoa Cái (Tam hợp): Dần Ngọ Tuất -> Tuất(10); Thân Tý Thìn -> Thìn(4); Tị Dậu Sửu -> Sửu(1); Hợi Mão Mùi -> Mùi(7)
    cai_table = {2: 10, 6: 10, 10: 10, 0: 4, 4: 4, 8: 4, 1: 1, 5: 1, 9: 1, 3: 7, 7: 7, 11: 7}
    pos_hoacai = cai_table[branch_year_idx]

    # Đào Hoa (Tam hợp): Dần Ngọ Tuất -> Mão(3); Thân Tý Thìn -> Dậu(9); Tị Dậu Sửu -> Ngọ(6); Hợi Mão Mùi -> Tý(0)
    dao_table = {2: 3, 6: 3, 10: 3, 0: 9, 4: 9, 8: 9, 1: 6, 5: 6, 9: 6, 3: 0, 7: 0, 11: 0}
    pos_daohoa = dao_table[branch_year_idx]

    # Kiếp Sát (Tam hợp): Dần Ngọ Tuất -> Hợi(11); Thân Tý Thìn -> Tị(5); Tị Dậu Sửu -> Dần(2); Hợi Mão Mùi -> Thân(8)
    ks_table = {2: 11, 6: 11, 10: 11, 0: 5, 4: 5, 8: 5, 1: 2, 5: 2, 9: 2, 3: 8, 7: 8, 11: 8}
    pos_kiepsat = ks_table[branch_year_idx]

    # Cô Thần, Quả Tú
    cothan_table = {
        11: (2, 10), 0: (2, 10), 1: (2, 10),
        2: (5, 1), 3: (5, 1), 4: (5, 1),
        5: (8, 4), 6: (8, 4), 7: (8, 4),
        8: (11, 7), 9: (11, 7), 10: (11, 7),
    }
    pos_cothan, pos_quatu = cothan_table[branch_year_idx]

    # Hồng Loan (Mão khởi Tý, nghịch): (3 - branch_year_idx) % 12
    pos_hongloan = (3 - branch_year_idx) % 12
    # Thiên Hỷ (đối diện Hồng Loan): (pos_hongloan + 6) % 12
    pos_thienhy = (pos_hongloan + 6) % 12

    # Long Trì (Thìn khởi Tý, thuận): (4 + branch_year_idx) % 12
    pos_longtri = (4 + branch_year_idx) % 12
    # Phượng Các & Giải Thần (Tuất khởi Tý, nghịch): (10 - branch_year_idx) % 12
    pos_phuongcac = (10 - branch_year_idx) % 12

    # Thiên Khốc (Ngọ nghịch): (6 - branch_year_idx) % 12
    pos_thienkhoc = (6 - branch_year_idx) % 12
    # Thiên Hư (Ngọ thuận): (6 + branch_year_idx) % 12
    pos_thienhu = (6 + branch_year_idx) % 12

    # Thiên Đức (Dậu thuận): (9 + branch_year_idx) % 12
    pos_thienduc = (9 + branch_year_idx) % 12
    # Nguyệt Đức (Tị thuận): (5 + branch_year_idx) % 12
    pos_nguyetduc = (5 + branch_year_idx) % 12

    # Phá Toái
    pt_table = {0: 5, 6: 5, 3: 5, 9: 5, 2: 9, 8: 9, 5: 9, 11: 9, 4: 1, 10: 1, 1: 1, 7: 1}
    pos_phatoai = pt_table[branch_year_idx]

    chi_year_stars = [
        ("Thiên Mã", pos_thienma),
        ("Hoa Cái", pos_hoacai),
        ("Đào Hoa", pos_daohoa),
        ("Hồng Loan", pos_hongloan),
        ("Thiên Hỷ", pos_thienhy),
        ("Long Trì", pos_longtri),
        ("Phượng Các", pos_phuongcac),
        ("Giải Thần", pos_phuongcac),
        ("Thiên Đức", pos_thienduc),
        ("Nguyệt Đức", pos_nguyetduc),
        ("Thiên Khốc", pos_thienkhoc),
        ("Thiên Hư", pos_thienhu),
        ("Kiếp Sát", pos_kiepsat),
        ("Cô Thần", pos_cothan),
        ("Quả Tú", pos_quatu),
        ("Phá Toái", pos_phatoai),
    ]
    for s_name, b_pos in chi_year_stars:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Thủy"), star_type=info.get("type", "phu_tinh"), nature=info.get("nature", "cat"), role=info.get("role", ""))
        )

    # 15. Các Phụ Tinh theo Can Năm
    # Quốc Ấn: Lộc Tồn tiến 8 cung
    pos_quocan = (pos_locton + 8) % 12
    # Đường Phù: Lộc Tồn tiến 7 cung (lùi 5)
    pos_duongphu = (pos_locton + 7) % 12

    # Thiên Quan, Thiên Phúc
    t_quan_table = [7, 4, 5, 2, 3, 9, 11, 9, 10, 6]
    t_phuc_table = [9, 8, 0, 11, 3, 2, 6, 5, 6, 5]
    pos_thienquan = t_quan_table[stem_year_idx]
    pos_thienphuc = t_phuc_table[stem_year_idx]

    # Lưu Hà
    luu_ha_table = [9, 10, 7, 4, 5, 6, 8, 3, 11, 2]
    pos_luuha = luu_ha_table[stem_year_idx]

    # Thiên Trù
    thien_tru_table = [5, 6, 0, 5, 6, 8, 2, 6, 9, 11]
    pos_thientru = thien_tru_table[stem_year_idx]

    can_year_stars = [
        ("Quốc Ấn", pos_quocan),
        ("Đường Phù", pos_duongphu),
        ("Thiên Quan", pos_thienquan),
        ("Thiên Phúc", pos_thienphuc),
        ("Lưu Hà", pos_luuha),
        ("Thiên Trù", pos_thientru),
    ]
    for s_name, b_pos in can_year_stars:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Thổ"), star_type="cat_tinh", nature=info.get("nature", "cat"), role=info.get("role", ""))
        )

    # 16. Các Phụ Tinh theo Tháng Sinh
    # Thiên Hình (Dậu khởi tháng 1, thuận): (9 + (lunar_month - 1)) % 12
    pos_thienhinh = (9 + (lunar_month - 1)) % 12
    # Thiên Riêu (Sửu khởi tháng 1, thuận): (1 + (lunar_month - 1)) % 12
    pos_thienrieu = (1 + (lunar_month - 1)) % 12
    # Thiên Y (đồng cung Thiên Riêu)
    pos_thieny = (pos_thienrieu + 2) % 12
    # Thiên Giải (Thân khởi tháng 1, thuận): (8 + (lunar_month - 1)) % 12
    pos_thiengiai = (8 + (lunar_month - 1)) % 12
    # Địa Giải (Mùi khởi tháng 1, thuận): (7 + (lunar_month - 1)) % 12
    pos_diagiai = (7 + (lunar_month - 1)) % 12

    month_stars = [
        ("Thiên Hình", pos_thienhinh),
        ("Thiên Riêu", pos_thienrieu),
        ("Thiên Y", pos_thieny),
        ("Thiên Giải", pos_thiengiai),
        ("Địa Giải", pos_diagiai),
    ]
    for s_name, b_pos in month_stars:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Hỏa"), star_type=info.get("type", "phu_tinh"), nature=info.get("nature", "cat"), role=info.get("role", ""))
        )

    # 17. Các Phụ Tinh theo Ngày Sinh
    # Tam Thai: Từ Tả Phù khởi 1, thuận đến ngày sinh
    pos_tamthai = (pos_taphu + (lunar_day - 1)) % 12
    # Bát Tọa: Từ Hữu Bật khởi 1, nghịch đến ngày sinh
    pos_battoa = (pos_huubat - (lunar_day - 1)) % 12
    # Ân Quang: Từ Văn Xương khởi 1, thuận đến ngày sinh, lùi 1 cung
    pos_anquang = (pos_vanxuong + (lunar_day - 1) - 1) % 12
    # Thiên Quý: Từ Văn Khúc khởi 1, nghịch đến ngày sinh, lùi 1 cung (tức +1)
    pos_thienquy = (pos_vankhuc - (lunar_day - 1) + 1) % 12

    day_stars = [
        ("Tam Thai", pos_tamthai),
        ("Bát Tọa", pos_battoa),
        ("Ân Quang", pos_anquang),
        ("Thiên Quý", pos_thienquy),
    ]
    for s_name, b_pos in day_stars:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Thủy"), star_type="cat_tinh", nature="cat", role=info.get("role", ""))
        )

    # 18. Các Phụ Tinh theo Giờ Sinh
    # Thai Phụ: Văn Khúc tiến 2 cung
    pos_thaiphu = (pos_vankhuc + 2) % 12
    # Phong Cáo: Văn Khúc lùi 2 cung
    pos_phongcao = (pos_vankhuc - 2) % 12

    hour_stars = [
        ("Thai Phụ", pos_thaiphu),
        ("Phong Cáo", pos_phongcao),
    ]
    for s_name, b_pos in hour_stars:
        info = STAR_INFO.get(s_name, {})
        palaces[b_pos].stars.append(
            StarInstance(name=s_name, element=info.get("element", "Kim"), star_type="cat_tinh", nature="cat", role=info.get("role", ""))
        )

    # 19. Tuần Không & Triệt Không
    # Tuần Trung Không Vong:
    tuan_offset = (branch_year_idx - stem_year_idx) % 12
    tuan_pos1 = (10 + tuan_offset) % 12
    tuan_pos2 = (11 + tuan_offset) % 12
    palaces[tuan_pos1].tuan_khong = True
    palaces[tuan_pos2].tuan_khong = True

    # Triệt Lộ Không Vong:
    triet_map = {0: (8, 9), 5: (8, 9), 1: (6, 7), 6: (6, 7), 2: (4, 5), 7: (4, 5), 3: (2, 3), 8: (2, 3), 4: (0, 1), 9: (0, 1)}
    triet_pos1, triet_pos2 = triet_map[stem_year_idx]
    palaces[triet_pos1].triet_khong = True
    palaces[triet_pos2].triet_khong = True

    # 20. Đại Hạn (10 năm mỗi cung)
    # Khởi từ Cung Mệnh bằng Cục số
    step_daihan = 1 if is_thuan_ly else -1
    for i in range(12):
        b_pos = (pos_menh + i * step_daihan) % 12
        age_start = cuc_num + i * 10
        age_end = age_start + 9
        palaces[b_pos].dai_han = f"{age_start} - {age_end}"

    # 21. Tiểu Hạn (1 năm mỗi cung)
    # Khởi theo Tam Hợp Chi năm:
    # Dần Ngọ Tuất khởi Thìn(4); Thân Tý Thìn khởi Tuất(10); Tị Dậu Sửu khởi Mùi(7); Hợi Mão Mùi khởi Sửu(1)
    tieu_han_starts = {
        2: 4, 6: 4, 10: 4,
        0: 10, 4: 10, 8: 10,
        1: 7, 5: 7, 9: 7,
        3: 1, 7: 1, 11: 1,
    }
    start_tieuhan = tieu_han_starts[branch_year_idx]
    step_tieuhan = 1 if gender == "male" else -1

    # Tuổi mụ năm hiện tại
    current_year = date.today().year
    lunar_age = (current_year - lunar.year) + 1

    for i in range(12):
        b_pos = (start_tieuhan + i * step_tieuhan) % 12
        palaces[b_pos].tieu_han = BRANCHES[b_pos]

    # Vị trí cung chứa Tiểu Hạn năm hiện tại
    current_tieu_han_pos = (start_tieuhan + (lunar_age - 1) * step_tieuhan) % 12

    # 22. Phân loại và định dạng sao trong từng cung
    formatted_palaces = []
    for p in palaces:
        chinh_tinh = [s for s in p.stars if s.star_type == "chinh_tinh"]
        cat_tinh = [s for s in p.stars if s.nature == "cat" and s.star_type != "chinh_tinh"]
        sat_hung_tinh = [s for s in p.stars if s.nature in ("hung", "trung") and s.star_type != "chinh_tinh"]
        trang_sinh_star = next((s for s in p.stars if s.star_type == "trang_sinh"), None)

        formatted_palaces.append({
            "index": p.index,
            "branch": p.branch,
            "stem": p.stem,
            "name": p.palace_name,
            "can_chi_name": f"{p.stem} {p.branch}",
            "is_menh": (p.palace_name == "Mệnh"),
            "is_body": p.is_body,
            "is_current_tieuhan": (p.index == current_tieu_han_pos),
            "dai_han": p.dai_han,
            "tieu_han": p.tieu_han,
            "tuan_khong": p.tuan_khong,
            "triet_khong": p.triet_khong,
            "trang_sinh": trang_sinh_star.name if trang_sinh_star else "",
            "chinh_tinh": [
                {
                    "name": s.name,
                    "element": s.element,
                    "brightness": s.brightness,
                    "modifier": s.modifier,
                    "full_label": f"{s.name} ({s.brightness})" if s.brightness else s.name,
                    "role": s.role,
                }
                for s in chinh_tinh
            ],
            "cat_tinh": [
                {
                    "name": s.name,
                    "element": s.element,
                    "modifier": s.modifier,
                    "role": s.role,
                }
                for s in cat_tinh
            ],
            "sat_hung_tinh": [
                {
                    "name": s.name,
                    "element": s.element,
                    "modifier": s.modifier,
                    "role": s.role,
                }
                for s in sat_hung_tinh
            ],
        })

    # Cung Mệnh tóm tắt
    menh_palace = next(p for p in formatted_palaces if p["is_menh"])
    than_palace = next(p for p in formatted_palaces if p["is_body"])

    return {
        "status": "ok",
        "thien_ban": {
            "full_name": full_name,
            "gender": gender,
            "gender_label": "Nam" if gender == "male" else "Nữ",
            "birth_date_solar": birth_date.isoformat(),
            "birth_time": birth_time.strftime("%H:%M") if birth_time else "Chưa nhập",
            "birth_place": birth_place or "Việt Nam",
            "birth_date_lunar": {
                "day": lunar.day,
                "month": lunar.month,
                "year": lunar.year,
                "is_leap": lunar.is_leap,
                "text": f"Ngày {lunar.day} tháng {lunar.month}{' (nhuận)' if lunar.is_leap else ''} năm {lunar.stem_year} {lunar.branch_year}",
            },
            "can_chi": {
                "year": f"{lunar.stem_year} {lunar.branch_year}",
                "month": f"{lunar.stem_month} {lunar.branch_month}",
                "day": f"{lunar.stem_day} {lunar.branch_day}",
                "hour": f"{lunar.stem_hour} {lunar.branch_hour}",
            },
            "yin_yang_gender": yin_yang_gender,
            "thuan_ly": is_thuan_ly,
            "thuan_ly_text": thuan_ly_text,
            "ban_menh": lunar.na_yin_year,
            "menh_element": menh_element,
            "cuc": cuc_name,
            "cuc_num": cuc_num,
            "cuc_element": cuc_element,
            "menh_cuc_relation": menh_cuc_relation,
            "chu_menh": CHU_MENH[branch_year_idx],
            "chu_than": CHU_THAN[branch_year_idx],
            "body_placement": body_placement_name,
            "tu_hoa": tu_hoa_map,
            "tuan_khong_cung": [BRANCHES[tuan_pos1], BRANCHES[tuan_pos2]],
            "triet_khong_cung": [BRANCHES[triet_pos1], BRANCHES[triet_pos2]],
            "lunar_age": lunar_age,
        },
        "palaces": formatted_palaces,
        "menh_summary": {
            "branch": menh_palace["branch"],
            "can_chi": menh_palace["can_chi_name"],
            "chinh_tinh": [s["full_label"] for s in menh_palace["chinh_tinh"]] or ["Vô Chính Diệu"],
            "cat_tinh_count": len(menh_palace["cat_tinh"]),
            "sat_tinh_count": len(menh_palace["sat_hung_tinh"]),
            "trang_sinh": menh_palace["trang_sinh"],
        },
        "than_summary": {
            "branch": than_palace["branch"],
            "can_chi": than_palace["can_chi_name"],
            "palace_name": than_palace["name"],
            "chinh_tinh": [s["full_label"] for s in than_palace["chinh_tinh"]] or ["Vô Chính Diệu"],
        },
    }
