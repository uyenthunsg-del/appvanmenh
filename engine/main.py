"""FastAPI engine: toàn bộ phần tính toán, trả về JSON. PHP chỉ gọi, không tự tính.

Chạy (trong thư mục engine):
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
Engine không có xác thực nên chỉ được lắng nghe trên 127.0.0.1.
"""
from __future__ import annotations

from datetime import date, time
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import bazi
import natal
import natal_svg
import numerology
import tuvi

app = FastAPI(title="Tuvi engine", version="0.4.0")


class NumerologyRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    birth_date: date
    y_mode: Literal["auto", "vowel", "consonant"] = "auto"
    # Năm dùng cho chu kỳ năm cá nhân; bỏ trống = năm hiện tại.
    year: int | None = Field(default=None, ge=1900, le=2200)


class BaziRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    gender: Literal["male", "female"]
    birth_date: date
    birth_time: time | None = None
    birth_place: str = Field(default="", max_length=150)
    zi_mode: Literal["next_day", "early_late"] = "next_day"
    tu_mode: Literal["fire", "water"] = "fire"


class NatalRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    gender: Literal["male", "female"]
    birth_date: date
    birth_time: time | None = None
    birth_place: str = Field(default="", max_length=150)
    house_system: Literal["placidus", "whole_sign", "equal"] = "placidus"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": app.version}


@app.post("/numerology")
def numerology_endpoint(req: NumerologyRequest) -> dict:
    try:
        return numerology.calculate(req.full_name, req.birth_date, req.y_mode, req.year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/bazi")
def bazi_endpoint(req: BaziRequest) -> dict:
    try:
        return bazi.calculate_bazi(
            full_name=req.full_name,
            gender=req.gender,
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            birth_place=req.birth_place,
            zi_mode=req.zi_mode,
            tu_mode=req.tu_mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/natal")
def natal_endpoint(req: NatalRequest) -> dict:
    try:
        chart_data = natal.calculate_natal_chart(
            full_name=req.full_name,
            gender=req.gender,
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            birth_place=req.birth_place,
            house_system=req.house_system,
        )
        chart_data["svg"] = natal_svg.generate_natal_chart_svg(chart_data)
        return chart_data
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class TuviRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    gender: Literal["male", "female"]
    birth_date: date
    birth_time: time | None = None
    birth_place: str = Field(default="", max_length=150)
    zi_mode: Literal["next_day", "early_late"] = "next_day"


@app.post("/tuvi")
def tuvi_endpoint(req: TuviRequest) -> dict:
    try:
        return tuvi.calculate_tuvi(
            full_name=req.full_name,
            gender=req.gender,
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            birth_place=req.birth_place,
            zi_mode=req.zi_mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
