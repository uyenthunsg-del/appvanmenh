"""Test các endpoint FastAPI (cần httpx: pip install -r requirements-dev.txt)."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_numerology_ok_with_vietnamese_name():
    r = client.post("/numerology", json={"full_name": "Nguyễn Văn A", "birth_date": "1990-01-01"})
    assert r.status_code == 200
    data = r.json()
    assert data["input"]["normalized_name"] == "NGUYEN VAN A"
    assert data["life_path"]["value"] == 3
    assert data["expression"]["value"] == 7
    assert data["soul_urge"]["value"] == 1
    assert data["personality"]["value"] == 33
    assert data["personality"]["master"] is True
    assert data["birth_day"]["value"] == 1


def test_y_mode_changes_result():
    body = {"full_name": "Thùy", "birth_date": "1990-01-01"}
    assert client.post("/numerology", json=body).json()["soul_urge"]["value"] == 3
    body["y_mode"] = "vowel"
    assert client.post("/numerology", json=body).json()["soul_urge"]["value"] == 1


def test_new_indices_and_cycle_in_response():
    body = {"full_name": "Nguyễn Lê Uyên Thư", "birth_date": "2005-10-21", "year": 2026}
    data = client.post("/numerology", json=body).json()
    assert data["attitude"]["value"] == 4
    assert data["maturity"]["value"] == 3
    assert data["personal_year"]["current"]["value"] == 5
    assert [c["single"] for c in data["personal_year"]["cycle"]] == [9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]


@pytest.mark.parametrize(
    "body",
    [
        {"full_name": "Anh", "birth_date": "1990-02-30"},                  # ngày không tồn tại
        {"full_name": "123", "birth_date": "1990-01-01"},                  # tên không có chữ cái
        {"full_name": "", "birth_date": "1990-01-01"},                     # tên rỗng
        {"full_name": "Anh"},                                              # thiếu ngày sinh
        {"full_name": "Anh", "birth_date": "1990-01-01", "y_mode": "xx"},  # y_mode sai
        {"full_name": "Anh", "birth_date": "1990-01-01", "year": 1800},     # năm ngoài khoảng cho phép
    ],
)
def test_invalid_input_returns_422(body):
    assert client.post("/numerology", json=body).status_code == 422


def test_bazi_endpoint_success():
    body = {
        "full_name": "Nguyễn Văn A",
        "gender": "male",
        "birth_date": "1990-05-15",
        "birth_time": "10:30",
        "birth_place": "Hà Nội",
        "zi_mode": "next_day",
        "tu_mode": "fire",
    }
    r = client.post("/bazi", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["day_master"]["stem"] == "Canh"
    assert len(data["pillars"]) == 4
    assert len(data["major_cycles"]) == 8
    assert "five_elements" in data
    assert data["options"]["zi_hour_mode"] is not None


def test_bazi_endpoint_without_birth_time():
    body = {
        "full_name": "Trần Thị B",
        "gender": "female",
        "birth_date": "1995-08-20",
    }
    r = client.post("/bazi", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["time_provided"] is False
    assert len(data["pillars"]) == 4


def test_natal_endpoint_success():
    body = {
        "full_name": "Nguyễn Văn A",
        "gender": "male",
        "birth_date": "1990-05-15",
        "birth_time": "10:30",
        "birth_place": "Hà Nội",
        "house_system": "placidus",
    }
    r = client.post("/natal", json=body)
    assert r.status_code == 200
    data = r.json()
    assert "SUN" in data["planets"]
    assert "ASC" in data["angles"]
    assert len(data["houses"]) == 12
    assert "svg" in data
    assert "<svg" in data["svg"]


def test_natal_endpoint_whole_sign():
    body = {
        "full_name": "Trần C",
        "gender": "female",
        "birth_date": "2000-01-01",
        "birth_time": "12:00",
        "birth_place": "Đà Nẵng",
        "house_system": "whole_sign",
    }
    r = client.post("/natal", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["house_system"] == "whole_sign"
    assert data["houses"]["1"]["cusp_longitude"] % 30 == 0
