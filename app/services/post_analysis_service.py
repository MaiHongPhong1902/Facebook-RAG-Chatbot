from typing import Dict, List, Optional
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
import os
from app.services.llm_service import LLMService
from app.services.deepseek_service import DeepSeekService

class PostAnalysisService:
    def __init__(self):
        self.llm_service = LLMService()
        self.deepseek_service = DeepSeekService()
        self.fb_access_token = os.getenv("FB_ACCESS_TOKEN")
        
    async def fetch_post_content(self, post_url: str) -> Optional[str]:
        """
        Lấy nội dung bài đăng từ URL Facebook
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Sử dụng Graph API để lấy nội dung bài đăng
                post_id = self._extract_post_id(post_url)
                if not post_id:
                    return None
                    
                api_url = f"https://graph.facebook.com/v18.0/{post_id}"
                params = {
                    "fields": "message,description,created_time",
                    "access_token": self.fb_access_token
                }
                
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message", "")
                    else:
                        logger.error(f"Error fetching post: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in fetch_post_content: {str(e)}")
            return None
            
    def _extract_post_id(self, url: str) -> Optional[str]:
        """
        Trích xuất post ID từ URL Facebook
        """
        try:
            # Xử lý các định dạng URL khác nhau
            if "/posts/" in url:
                return url.split("/posts/")[1].split("?")[0]
            elif "/permalink/" in url:
                return url.split("/permalink/")[1].split("?")[0]
            return None
        except Exception as e:
            logger.error(f"Error extracting post ID: {str(e)}")
            return None
            
    async def analyze_post(self, post_url: str, post_content: Optional[str] = None) -> Dict:
        """
        Phân tích bài đăng Facebook sử dụng DeepSeek
        """
        try:
            # Lấy nội dung bài đăng nếu không được cung cấp
            if not post_content:
                post_content = await self.fetch_post_content(post_url)
                if not post_content:
                    raise ValueError("Không thể lấy nội dung bài đăng")
                    
            # Phân tích tổng quan với DeepSeek
            general_analysis = await self.deepseek_service.analyze_text(post_content, "general")
            
            # Phân tích cảm xúc với DeepSeek
            sentiment_analysis = await self.deepseek_service.analyze_text(post_content, "sentiment")
            
            # Kết hợp kết quả
            return {
                "analysis": general_analysis["summary"],
                "sentiment": sentiment_analysis["sentiment"],
                "sentiment_intensity": sentiment_analysis["intensity"],
                "key_topics": general_analysis["topics"],
                "key_points": general_analysis["key_points"],
                "sentiment_keywords": sentiment_analysis["keywords"]
            }
                
        except Exception as e:
            logger.error(f"Error in analyze_post: {str(e)}")
            raise 