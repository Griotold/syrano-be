from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, Subscription


async def get_or_create_anonymous_user(
    session: AsyncSession,
    user_id: str | None = None,
) -> User:
    """
    - user_id가 이미 있으면 그 유저를 찾아서 반환.
    - user_id가 없거나, DB에 없으면 새 유저 + 기본 구독을 생성.
    """

    # 1) user_id가 넘어온 경우: 이미 존재하는 유저인지 먼저 확인
    if user_id is not None:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

    # 2) 새 유저 생성
    user = User()
    session.add(user)
    await session.flush()  # user.id를 바로 쓰기 위해 flush

    # 3) 기본 구독 생성 (무료/비프리미엄)
    subscription = Subscription(
        user_id=user.id,
        is_premium=False,
        plan_type=None,
        expires_at=None,
    )
    session.add(subscription)

    await session.commit()
    await session.refresh(user)

    return user