import os
import httpx
from typing import Dict, List
from loguru import logger

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY not found in environment variables")
            raise ValueError("OPENROUTER_API_KEY is required")
            
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Sử dụng model phổ biến và ổn định hơn
        self.model = "mistralai/mistral-7b-instruct"
        self.timeout = 30.0
        self.max_retries = 3

    async def get_completion(self, question: str) -> Dict[str, List[str]]:
        """
        Gọi API để lấy câu trả lời từ model
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Facebook RAG Chatbot"
        }

        messages = [
            {"role": "system", "content": "Bạn là một chatbot chuyên gia về Facebook. Hãy trả lời câu hỏi dựa trên kiến thức của bạn."},
            {"role": "user", "content": question}
        ]

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        }

        # Log request details (không log API key)
        logger.debug(f"Request to {self.api_url}")
        logger.debug(f"Model: {self.model}")
        logger.debug(f"Messages: {messages}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=data
                    )
                    
                    # Log response status và headers
                    logger.debug(f"Response status: {response.status_code}")
                    logger.debug(f"Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 401:
                        logger.error("Unauthorized: Invalid API key")
                        raise Exception("API key không hợp lệ")
                        
                    if response.status_code == 403:
                        logger.error("Forbidden: No access to model")
                        raise Exception("Không có quyền truy cập model")
                        
                    if response.status_code == 404:
                        logger.error("Model not found")
                        raise Exception("Model không tồn tại")
                        
                    response.raise_for_status()
                    
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                    
                    # Tạo nguồn tham khảo mẫu
                    sources = [
                        "Facebook Marketing Guide 2024",
                        "Social Media Best Practices",
                        "Facebook Algorithm Updates"
                    ]
                    
                    return {
                        "answer": answer,
                        "sources": sources
                    }
                    
                except httpx.TimeoutException:
                    logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                    if attempt == self.max_retries - 1:
                        raise Exception("API request timeout after multiple attempts")
                    continue
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error on attempt {attempt + 1}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"API request failed: {str(e)}")
                    continue
                    
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Unexpected error: {str(e)}")
                    continue 