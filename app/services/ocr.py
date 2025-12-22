"""
OCR 서비스 - EasyOCR을 사용한 이미지 텍스트 추출
"""
from __future__ import annotations

import logging
from pathlib import Path

import easyocr
import torch

logger = logging.getLogger("syrano")

# EasyOCR Reader 글로벌 초기화 (앱 시작 시 한 번만)
# GPU 사용 가능 여부 자동 감지
_USE_GPU = torch.cuda.is_available()
_READER = None


def get_reader() -> easyocr.Reader:
    """
    EasyOCR Reader 싱글톤 인스턴스 반환.
    처음 호출 시 초기화되며, 이후 재사용.
    """
    global _READER
    if _READER is None:
        logger.info(f"Initializing EasyOCR Reader (GPU: {_USE_GPU})")
        _READER = easyocr.Reader(['ko', 'en'], gpu=_USE_GPU)
        logger.info("EasyOCR Reader initialized")
    return _READER


async def extract_text_from_image(image_path: str | Path) -> str:
    """
    이미지 파일에서 텍스트를 추출합니다.
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        추출된 텍스트 (줄바꿈으로 구분)
        
    Raises:
        Exception: OCR 처리 중 오류 발생 시
    """
    try:
        reader = get_reader()
        
        # OCR 실행
        # result: List[Tuple[bbox, text, confidence]]
        result = reader.readtext(str(image_path))
        
        # 텍스트만 추출 (confidence 낮은 것도 일단 포함)
        texts = [detection[1] for detection in result]
        
        # 줄바꿈으로 합치기
        extracted_text = '\n'.join(texts)
        
        logger.info(
            f"OCR completed: extracted {len(texts)} text blocks, "
            f"total {len(extracted_text)} characters"
        )
        
        return extracted_text.strip()
        
    except Exception as e:
        logger.exception(f"OCR failed for image: {image_path}")
        raise Exception(f"텍스트 추출 중 오류 발생: {str(e)}") from e