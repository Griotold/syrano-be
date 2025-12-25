# app/schemas/profile.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


# ========== Request DTOs ==========

class ProfileCreateRequest(BaseModel):
    """프로필 생성 요청"""
    user_id: str = Field(..., description="프로필을 생성할 사용자 ID")
    name: str = Field(..., min_length=1, max_length=100, description="프로필 이름")
    age: int | None = Field(None, ge=1, le=150, description="나이")
    gender: str | None = Field(None, max_length=10, description="성별 (예: 남성, 여성, etc)")
    memo: str | None = Field(None, description="메모")


class ProfileUpdateRequest(BaseModel):
    """프로필 수정 요청"""
    name: str | None = Field(None, min_length=1, max_length=100, description="프로필 이름")
    age: int | None = Field(None, ge=1, le=150, description="나이")
    gender: str | None = Field(None, max_length=10, description="성별")
    memo: str | None = Field(None, description="메모")


# ========== Response DTOs ==========

class ProfileResponse(BaseModel):
    """프로필 응답"""
    id: str
    user_id: str
    name: str
    age: int | None
    gender: str | None
    memo: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델을 Pydantic으로 변환 가능


class ProfileListResponse(BaseModel):
    """프로필 목록 응답"""
    profiles: list[ProfileResponse]