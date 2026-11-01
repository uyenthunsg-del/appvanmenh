import tuvi
from datetime import date, time

res = tuvi.calculate_tuvi("Nguyễn Văn A", "male", date(1990, 5, 15), time(8, 30), "Hà Nội")
print("Bản Mệnh:", res["thien_ban"]["ban_menh"])
print("Cục:", res["thien_ban"]["cuc"])
print("Mệnh Cục:", res["thien_ban"]["menh_cuc_relation"])
print("Cung Mệnh:", res["menh_summary"])
print("Cung Thân:", res["than_summary"])
print("Palaces count:", len(res["palaces"]))
for p in res["palaces"][:4]:
    print(p["name"], p["can_chi_name"], [s["name"] for s in p["chinh_tinh"]])
