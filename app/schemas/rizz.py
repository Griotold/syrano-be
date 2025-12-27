"""
Rizz API 요청/응답 스키마
"""
from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field

# ========== Request DTOs ==========

class GenerateRequest(BaseModel):
    """텍스트 기반 답변 생성 요청 (기존)"""
    mode: Literal["conversation"] = "conversation"
    conversation: str
    platform: str = "kakao"
    relationship: str = "first_meet"
    style: str = "banmal"
    tone: str = "friendly"
    num_suggestions: int = 3
    user_id: str

class ImageAnalyzeRequest(BaseModel):
    """이미지 기반 답변 생성 요청 (Profile 활용)"""
    user_id: str = Field(..., description="사용자 ID")
    profile_id: str = Field(..., description="상대방 프로필 ID")
    num_suggestions: int = Field(default=3, ge=1, le=5, description="생성할 답장 개수")

# ========== Response DTOs ==========

class UsageInfo(BaseModel):
    """사용량 정보"""
    remaining: int = Field(..., description="남은 사용 횟수 (-1: 무제한)")
    limit: int = Field(..., description="일일 제한 횟수 (-1: 무제한)")
    is_premium: bool = Field(..., description="프리미엄 여부")

class GenerateResponse(BaseModel):
    """답변 생성 응답"""
    suggestions: List[str]
    usage_info: UsageInfo