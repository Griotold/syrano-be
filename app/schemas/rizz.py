"""
Rizz API 요청/응답 스키마
"""
from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel


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


class GenerateResponse(BaseModel):
    """답변 생성 응답"""
    suggestions: List[str]