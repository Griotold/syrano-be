"""
OCR 서비스 인터페이스 (Protocol)
"""
from typing import Protocol
from pathlib import Path


class OCRService(Protocol):
    """
    OCR 서비스 프로토콜.
    이 인터페이스를 따르는 모든 클래스는 OCRService로 사용 가능.
    """
    
    async def extract_text(self, image_path: str | Path) -> str:
        """
        이미지에서 텍스트를 추출합니다.
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            추출된 텍스트
            
        Raises:
            Exception: OCR 처리 중 오류 발생 시
        """
        ...