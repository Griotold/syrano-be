# app/routers/profiles.py
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileResponse,
    ProfileListResponse,
)
from app.services.profiles import (
    create_profile,
    get_profile_by_id,
    get_profiles_by_user_id,
    update_profile,
    delete_profile,
)

logger = logging.getLogger("syrano")

router = APIRouter()


@router.post("", response_model=ProfileResponse, status_code=201)
async def create_profile_endpoint(
    body: ProfileCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    프로필 생성
    """
    try:
        profile = await create_profile(
            session=session,
            user_id=body.user_id,
            name=body.name,
            age=body.age,
            gender=body.gender,
            memo=body.memo,
        )
        return profile
    except Exception as e:
        logger.exception("Failed to create profile")
        raise HTTPException(
            status_code=500,
            detail="프로필 생성 중 오류가 발생했어요.",
        ) from e


@router.get("", response_model=ProfileListResponse)
async def get_profiles_endpoint(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    사용자의 프로필 목록 조회
    
    - Query parameter: user_id
    """
    try:
        profiles = await get_profiles_by_user_id(session, user_id)
        return ProfileListResponse(profiles=profiles)
    except Exception as e:
        logger.exception("Failed to get profiles")
        raise HTTPException(
            status_code=500,
            detail="프로필 목록 조회 중 오류가 발생했어요.",
        ) from e


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile_endpoint(
    profile_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    특정 프로필 조회
    """
    profile = await get_profile_by_id(session, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="프로필을 찾을 수 없어요.",
        )
    
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile_endpoint(
    profile_id: str,
    body: ProfileUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    프로필 수정
    
    - 제공된 필드만 업데이트됨
    - 제공되지 않은 필드는 기존 값 유지
    """
    profile = await get_profile_by_id(session, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="프로필을 찾을 수 없어요.",
        )
    
    try:
        updated_profile = await update_profile(
            session=session,
            profile=profile,
            name=body.name,
            age=body.age,
            gender=body.gender,
            memo=body.memo,
        )
        return updated_profile
    except Exception as e:
        logger.exception("Failed to update profile")
        raise HTTPException(
            status_code=500,
            detail="프로필 수정 중 오류가 발생했어요.",
        ) from e


@router.delete("/{profile_id}", status_code=204)
async def delete_profile_endpoint(
    profile_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    프로필 삭제
    
    - 204 No Content 반환
    """
    profile = await get_profile_by_id(session, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="프로필을 찾을 수 없어요.",
        )
    
    try:
        await delete_profile(session, profile)
        return None  # 204는 body 없음
    except Exception as e:
        logger.exception("Failed to delete profile")
        raise HTTPException(
            status_code=500,
            detail="프로필 삭제 중 오류가 발생했어요.",
        ) from e