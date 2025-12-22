from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

from app.db import get_session
from app.services.llm import generate_suggestions_from_conversation
from app.services.subscriptions import get_subscription_by_user_id
from app.services.ocr import extract_text_from_image
from app.schemas.rizz import GenerateRequest, GenerateResponse

logger = logging.getLogger("syrano")
router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_rizz(
    req: GenerateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Rizz 메시지 생성 엔드포인트 (텍스트 입력).
    - user_id를 기반으로 DB에서 구독 상태를 조회해서 is_premium을 결정한다.
    """

    # 1) user_id로 구독 조회
    subscription = await get_subscription_by_user_id(session, req.user_id)
    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="해당 user_id의 구독 정보를 찾을 수 없어요. 다시 로그인(익명 인증)해 주세요.",
        )

    is_premium = subscription.is_premium

    logger.info(
        "Generate rizz called",
        extra={
            "platform": req.platform,
            "relationship": req.relationship,
            "style": req.style,
            "tone": req.tone,
            "num_suggestions": req.num_suggestions,
            "user_id": req.user_id,
            "is_premium": is_premium,
        },
    )

    try:
        suggestions = await generate_suggestions_from_conversation(
            conversation=req.conversation,
            platform=req.platform,
            relationship=req.relationship,
            style=req.style,
            tone=req.tone,
            num_suggestions=req.num_suggestions,
            is_premium=is_premium,
        )
    except Exception as e:
        logger.exception("Error while generating suggestions from LLM")
        raise HTTPException(
            status_code=500,
            detail="메시지 생성 중 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
        ) from e

    if not suggestions:
        logger.error("LLM returned empty suggestions")
        raise HTTPException(
            status_code=500,
            detail="메시지를 생성하지 못했어요. 다시 한 번 시도해볼래요?",
        )

    return GenerateResponse(suggestions=suggestions)


@router.post("/analyze-image", response_model=GenerateResponse)
async def analyze_image(
    image: UploadFile = File(...),
    user_id: str = Form(...),
    platform: str = Form("kakao"),
    relationship: str = Form("first_meet"),
    style: str = Form("banmal"),
    tone: str = Form("friendly"),
    num_suggestions: int = Form(3),
    session: AsyncSession = Depends(get_session),
):
    """
    이미지 기반 Rizz 메시지 생성 엔드포인트.
    
    1. 이미지를 임시 저장
    2. EasyOCR로 텍스트 추출
    3. LLM으로 답변 생성
    4. 임시 파일 삭제
    """
    
    # 1) 구독 확인
    subscription = await get_subscription_by_user_id(session, user_id)
    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="해당 user_id의 구독 정보를 찾을 수 없어요. 다시 로그인(익명 인증)해 주세요.",
        )
    
    is_premium = subscription.is_premium
    
    # 2) 임시 디렉토리 생성
    temp_dir = Path("temp_images")
    temp_dir.mkdir(exist_ok=True)
    
    # 3) 임시 파일 저장
    file_id = str(uuid.uuid4())
    file_extension = Path(image.filename or "image.jpg").suffix or ".jpg"
    file_path = temp_dir / f"{file_id}{file_extension}"
    
    try:
        # 파일 저장
        async with aiofiles.open(file_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        logger.info(f"Image saved to {file_path}, size: {len(content)} bytes")
        
        # 4) OCR 실행
        conversation = await extract_text_from_image(file_path)
        
        logger.info(f"Extracted text length: {len(conversation)} characters")
        logger.info(f"Extracted text preview: {conversation[:100]}...")
        
        # 텍스트 추출 검증
        if not conversation or len(conversation.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="이미지에서 텍스트를 추출하지 못했어요. 더 선명한 이미지를 사용해주세요.",
            )
        
        # 5) LLM 답변 생성
        suggestions = await generate_suggestions_from_conversation(
            conversation=conversation,
            platform=platform,
            relationship=relationship,
            style=style,
            tone=tone,
            num_suggestions=num_suggestions,
            is_premium=is_premium,
        )
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="메시지를 생성하지 못했어요. 다시 한 번 시도해볼래요?",
            )
        
        return GenerateResponse(suggestions=suggestions)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in analyze_image")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 분석 중 오류가 발생했어요: {str(e)}",
        ) from e
    finally:
        # 6) 임시 파일 삭제
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Temporary file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")