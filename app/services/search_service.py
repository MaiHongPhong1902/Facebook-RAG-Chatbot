from typing import Dict, List
from loguru import logger
from app.services.llm_service import LLMService
from app.services.deepseek_service import DeepSeekService
import json
import os
from pathlib import Path
import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib

class SearchService:
    def __init__(self):
        self.llm_service = LLMService()
        self.deepseek_service = DeepSeekService()
        self.knowledge_base_path = Path("app/data/knowledge_base.json")
        self.last_update_path = Path("app/data/last_update.json")
        self.update_interval = 24 * 60 * 60  # 24 giờ
        
    def _load_knowledge_base(self) -> List[Dict]:
        """
        Tải cơ sở tri thức từ file JSON
        """
        try:
            if not self.knowledge_base_path.exists():
                logger.warning("Knowledge base file not found")
                return []
                
            with open(self.knowledge_base_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            return []
            
    def _save_knowledge_base(self, knowledge_base: List[Dict]):
        """
        Lưu cơ sở tri thức vào file JSON
        """
        try:
            self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.knowledge_base_path, "w", encoding="utf-8") as f:
                json.dump(knowledge_base, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")
            
    def _get_last_update(self) -> datetime:
        """
        Lấy thời gian cập nhật cuối cùng
        """
        try:
            if self.last_update_path.exists():
                with open(self.last_update_path, "r") as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data["last_update"])
            return datetime.min
        except Exception as e:
            logger.error(f"Error getting last update: {str(e)}")
            return datetime.min
            
    def _save_last_update(self):
        """
        Lưu thời gian cập nhật cuối cùng
        """
        try:
            self.last_update_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.last_update_path, "w") as f:
                json.dump({"last_update": datetime.now().isoformat()}, f)
        except Exception as e:
            logger.error(f"Error saving last update: {str(e)}")
            
    async def _fetch_facebook_news(self) -> List[Dict]:
        """
        Lấy tin tức mới từ Facebook Newsroom
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://newsroom.fb.com/news/"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        news_items = []
                        
                        for article in soup.select('article'):
                            title = article.select_one('h2')
                            content = article.select_one('.entry-content')
                            date = article.select_one('.date')
                            
                            if title and content:
                                news_items.append({
                                    "id": hashlib.md5(title.text.encode()).hexdigest(),
                                    "title": title.text.strip(),
                                    "content": content.text.strip(),
                                    "source": "Facebook Newsroom",
                                    "category": "news",
                                    "date": date.text.strip() if date else datetime.now().isoformat()
                                })
                                
                        return news_items
                    return []
        except Exception as e:
            logger.error(f"Error fetching Facebook news: {str(e)}")
            return []
            
    async def _fetch_facebook_docs(self) -> List[Dict]:
        """
        Lấy tài liệu mới từ Facebook Documentation
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://developers.facebook.com/docs/"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        docs_items = []
                        
                        for doc in soup.select('.documentation-item'):
                            title = doc.select_one('h3')
                            content = doc.select_one('.description')
                            
                            if title and content:
                                docs_items.append({
                                    "id": hashlib.md5(title.text.encode()).hexdigest(),
                                    "title": title.text.strip(),
                                    "content": content.text.strip(),
                                    "source": "Facebook Documentation",
                                    "category": "documentation",
                                    "date": datetime.now().isoformat()
                                })
                                
                        return docs_items
                    return []
        except Exception as e:
            logger.error(f"Error fetching Facebook docs: {str(e)}")
            return []
            
    async def _update_knowledge_base(self):
        """
        Cập nhật cơ sở tri thức với thông tin mới
        """
        try:
            # Kiểm tra thời gian cập nhật cuối
            last_update = self._get_last_update()
            if (datetime.now() - last_update).total_seconds() < self.update_interval:
                logger.info("Knowledge base is up to date")
                return
                
            # Lấy thông tin mới
            news_items = await self._fetch_facebook_news()
            docs_items = await self._fetch_facebook_docs()
            
            # Tải cơ sở tri thức hiện tại
            current_kb = self._load_knowledge_base()
            
            # Tạo set ID hiện tại
            current_ids = {item["id"] for item in current_kb}
            
            # Thêm các mục mới
            for item in news_items + docs_items:
                if item["id"] not in current_ids:
                    current_kb.append(item)
                    current_ids.add(item["id"])
                    
            # Lưu cơ sở tri thức mới
            self._save_knowledge_base(current_kb)
            self._save_last_update()
            
            logger.info(f"Updated knowledge base with {len(news_items) + len(docs_items)} new items")
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")
            
    async def _search_knowledge_base(self, query: str, knowledge_base: List[Dict]) -> List[Dict]:
        """
        Tìm kiếm trong cơ sở tri thức sử dụng DeepSeek
        """
        try:
            # Sử dụng DeepSeek để tìm kiếm
            search_results = await self.deepseek_service.search_knowledge(query, knowledge_base)
            
            # Thêm thông tin chi tiết cho mỗi kết quả
            for result in search_results:
                # Phân tích chi tiết nội dung
                analysis = await self.deepseek_service.analyze_text(result["text"])
                result.update({
                    "summary": analysis["summary"],
                    "topics": analysis["topics"],
                    "sentiment": analysis["sentiment"],
                    "key_points": analysis["key_points"]
                })
                
            return search_results
                
        except Exception as e:
            logger.error(f"Error in search_knowledge_base: {str(e)}")
            return []
            
    async def search(self, query: str) -> List[str]:
        """
        Tìm kiếm thông tin về Facebook
        """
        try:
            # Cập nhật cơ sở tri thức nếu cần
            await self._update_knowledge_base()
            
            # Tải cơ sở tri thức
            knowledge_base = self._load_knowledge_base()
            
            # Tìm kiếm trong cơ sở tri thức
            search_results = await self._search_knowledge_base(query, knowledge_base)
            
            # Chuyển đổi kết quả thành danh sách văn bản
            results = []
            for result in search_results:
                text = result["text"]
                source = result["source"]
                relevance = result["relevance"]
                explanation = result["explanation"]
                sentiment = result["sentiment"]
                key_points = result["key_points"]
                
                formatted_result = f"""
                {text}
                
                Độ liên quan: {relevance}
                Giải thích: {explanation}
                Cảm xúc: {sentiment}
                Điểm chính: {', '.join(key_points)}
                
                Nguồn: {source}
                """
                results.append(formatted_result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return ["Xin lỗi, đã có lỗi xảy ra khi tìm kiếm"] 