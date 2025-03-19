from typing import Dict, List
import aiohttp
from loguru import logger
import os
import json

class DeepSeekService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1-zero:free"
        
    async def get_completion(self, prompt: str, max_tokens: int = 1000) -> Dict:
        """
        Gọi API OpenRouter để lấy kết quả
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/chatbotRAG-FB",  # Thay thế bằng URL thực tế của bạn
                "X-Title": "Facebook RAG Chatbot"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Bạn là một trợ lý AI chuyên gia về Facebook, có khả năng phân tích và tìm kiếm thông tin chính xác."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.95
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "answer": result["choices"][0]["message"]["content"],
                            "sources": []  # OpenRouter không cung cấp sources
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {error_text}")
                        raise Exception(f"OpenRouter API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error in OpenRouter API call: {str(e)}")
            raise
            
    async def analyze_text(self, text: str, analysis_type: str = "general") -> Dict:
        """
        Phân tích văn bản với DeepSeek
        """
        try:
            if analysis_type == "general":
                prompt = f"""
                Phân tích văn bản sau đây một cách chi tiết:
                
                {text}
                
                Hãy cung cấp:
                1. Tóm tắt nội dung chính
                2. Các chủ đề được đề cập
                3. Cảm xúc và giọng điệu
                4. Các điểm quan trọng
                
                Định dạng trả về:
                {{
                    "summary": "tóm tắt",
                    "topics": ["chủ đề 1", "chủ đề 2", ...],
                    "sentiment": "cảm xúc",
                    "key_points": ["điểm 1", "điểm 2", ...]
                }}
                """
            elif analysis_type == "sentiment":
                prompt = f"""
                Phân tích cảm xúc của văn bản sau:
                
                {text}
                
                Hãy cung cấp:
                1. Cảm xúc chính (tích cực/tiêu cực/trung tính)
                2. Mức độ cảm xúc (0-1)
                3. Các từ khóa cảm xúc
                
                Định dạng trả về:
                {{
                    "sentiment": "cảm xúc",
                    "intensity": 0.5,
                    "keywords": ["từ 1", "từ 2", ...]
                }}
                """
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
                
            result = await self.get_completion(prompt)
            return json.loads(result["answer"])
            
        except Exception as e:
            logger.error(f"Error in analyze_text: {str(e)}")
            raise
            
    async def search_knowledge(self, query: str, knowledge_base: List[Dict]) -> List[Dict]:
        """
        Tìm kiếm thông tin trong cơ sở tri thức với DeepSeek
        """
        try:
            # Chuyển đổi knowledge_base thành chuỗi JSON
            kb_text = "\n".join([
                f"Tiêu đề: {item.get('title', '')}\nNội dung: {item.get('content', '')}\n"
                for item in knowledge_base
            ])
            
            prompt = f"""
            Tìm kiếm thông tin liên quan đến câu hỏi sau trong cơ sở tri thức:
            
            Câu hỏi: {query}
            
            Cơ sở tri thức:
            {kb_text}
            
            Hãy trả về các đoạn văn bản liên quan nhất, định dạng JSON như sau:
            [
                {{
                    "text": "đoạn văn bản liên quan",
                    "relevance": 0.8,
                    "source": "nguồn thông tin",
                    "explanation": "giải thích tại sao đoạn văn bản này liên quan"
                }}
            ]
            
            Chỉ trả về JSON, không kèm text khác.
            """
            
            result = await self.get_completion(prompt)
            try:
                # Thử parse JSON từ kết quả
                search_results = json.loads(result["answer"])
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from API response: {str(e)}")
                # Nếu không parse được, tạo kết quả mặc định
                search_results = [{
                    "text": "Không tìm thấy thông tin liên quan",
                    "relevance": 0.0,
                    "source": "N/A",
                    "explanation": "Không thể phân tích kết quả từ API"
                }]
            
            # Đảm bảo search_results là list
            if not isinstance(search_results, list):
                search_results = [search_results]
            
            # Sắp xếp theo độ liên quan
            search_results.sort(key=lambda x: float(x.get("relevance", 0)), reverse=True)
            return search_results[:5]  # Trả về 5 kết quả liên quan nhất
            
        except Exception as e:
            logger.error(f"Error in search_knowledge: {str(e)}")
            return [{
                "text": "Có lỗi xảy ra khi tìm kiếm",
                "relevance": 0.0,
                "source": "N/A",
                "explanation": str(e)
            }] 