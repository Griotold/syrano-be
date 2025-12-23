"""
Naver Clova OCR 구현체
"""
from __future__ import annotations

import logging
import uuid
import json
import base64
from pathlib import Path

import httpx

logger = logging.getLogger("syrano")


class NaverOCRService:
    """Naver Clova OCR 서비스 구현"""
    
    def __init__(self, secret_key: str, invoke_url: str):
        self.secret_key = secret_key
        self.invoke_url = invoke_url
    
    async def extract_text(self, image_path: str | Path) -> str:
        """
        Naver Clova OCR로 이미지에서 텍스트를 추출합니다.
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            추출된 텍스트 (줄바꿈으로 구분)
            
        Raises:
            Exception: OCR 처리 중 오류 발생 시
        """
        try:
            # 이미지 파일을 base64로 인코딩
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # base64 인코딩
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 파일 확장자 확인
            file_extension = Path(image_path).suffix.lower().replace('.', '')
            if file_extension == 'jpg':
                file_extension = 'jpeg'
            
            # 요청 JSON
            request_json = {
                'images': [
                    {
                        'format': file_extension,
                        'name': 'demo',
                        'data': image_base64  # ← base64 데이터 전송
                    }
                ],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': 0
            }
            
            # API 호출
            logger.info(f"Calling Naver OCR API: {self.invoke_url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.invoke_url,
                    headers={
                        'X-OCR-SECRET': self.secret_key,
                        'Content-Type': 'application/json'
                    },
                    json=request_json,  # ← JSON으로 전송
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            logger.info(f"API Response Status: {response.status_code}")
            
            # 텍스트 추출
            texts = []
            if 'images' in result and len(result['images']) > 0:
                fields = result['images'][0].get('fields', [])
                for field in fields:
                    text = field.get('inferText', '')
                    if text:
                        texts.append(text)
            
            extracted_text = '\n'.join(texts)
            
            # 상세 로그
            logger.info("=" * 80)
            logger.info("Naver Clova OCR 결과")
            logger.info("=" * 80)
            logger.info(f"추출된 텍스트 블록 수: {len(texts)}개")
            logger.info(f"추출된 문자 수: {len(extracted_text)}자")
            logger.info("-" * 80)
            logger.info("전체 추출 텍스트:")
            logger.info(extracted_text)
            logger.info("=" * 80)
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.exception(f"Naver Clova OCR failed for image: {image_path}")
            raise Exception(f"텍스트 추출 중 오류 발생: {str(e)}") from e