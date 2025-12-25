# app/services/profiles.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile


async def create_profile(
    session: AsyncSession,
    user_id: str,
    name: str,
    age: int | None = None,
    gender: str | None = None,
    memo: str | None = None,
) -> Profile:
    """
    새 프로필 생성
    """
    profile = Profile(
        user_id=user_id,
        name=name,
        age=age,
        gender=gender,
        memo=memo,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def get_profile_by_id(
    session: AsyncSession,
    profile_id: str,
) -> Profile | None:
    """
    ID로 프로필 조회
    """
    result = await session.execute(
        select(Profile).where(Profile.id == profile_id)
    )
    return result.scalar_one_or_none()


async def get_profiles_by_user_id(
    session: AsyncSession,
    user_id: str,
) -> list[Profile]:
    """
    사용자의 모든 프로필 조회
    """
    result = await session.execute(
        select(Profile)
        .where(Profile.user_id == user_id)
        .order_by(Profile.created_at.desc())
    )
    return list(result.scalars().all())


async def update_profile(
    session: AsyncSession,
    profile: Profile,
    name: str | None = None,
    age: int | None = None,
    gender: str | None = None,
    memo: str | None = None,
) -> Profile:
    """
    프로필 수정
    
    - None이 아닌 값만 업데이트
    """
    if name is not None:
        profile.name = name
    if age is not None:
        profile.age = age
    if gender is not None:
        profile.gender = gender
    if memo is not None:
        profile.memo = memo
    
    await session.commit()
    await session.refresh(profile)
    return profile


async def delete_profile(
    session: AsyncSession,
    profile: Profile,
) -> None:
    """
    프로필 삭제
    """
    await session.delete(profile)
    await session.commit()