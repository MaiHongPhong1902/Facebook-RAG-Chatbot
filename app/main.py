from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
import os
import sys
from pathlib import Path
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Cấu hình logging
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    backtrace=True,
    diagnose=True
)

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.services.llm_service import LLMService
from app.services.post_analysis_service import PostAnalysisService
from app.services.search_service import SearchService

# Khởi tạo rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Facebook RAG Chatbot API",
    description="API cho chatbot RAG về Facebook",
    version="1.0.0"
)

# Xử lý rate limit exceeded
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Khởi tạo các service
llm_service = LLMService()
post_analysis_service = PostAnalysisService()
search_service = SearchService()

# Thêm Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount thư mục static với caching
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Cấu hình templates với cache
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
@limiter.limit("100/minute")
async def root(request: Request):
    """
    Trang chủ của API
    """
    logger.info(f"Access homepage from {request.client.host}")
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Facebook RAG Chatbot API",
            "endpoints": {
                "/chat-ui": "Giao diện chat với bot",
                "/docs": "API documentation",
                "/chat": "API gửi câu hỏi cho chatbot",
                "/analyze-post": "Phân tích bài đăng Facebook",
                "/search": "Tìm kiếm thông tin"
            }
        }
    )
    response.headers["Cache-Control"] = "public, max-age=31536000"
    return response

@app.get("/chat-ui", response_class=HTMLResponse)
@limiter.limit("100/minute")
async def chat_ui(request: Request):
    """
    Giao diện chat với bot
    """
    logger.info(f"Access chat UI from {request.client.host}")
    return templates.TemplateResponse("chat.html", {"request": request})

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class PostAnalysisRequest(BaseModel):
    post_url: str
    post_content: Optional[str] = None

class PostAnalysisResponse(BaseModel):
    analysis: str
    sentiment: str
    key_topics: List[str]

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest
):
    """
    Endpoint để gửi câu hỏi và nhận câu trả lời từ chatbot
    """
    try:
        logger.info(f"Chat request from {request.client.host}: {chat_request.question}")
        result = await llm_service.get_completion(chat_request.question)
        logger.info(f"Chat response: {result['answer'][:100]}...")
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze-post", response_class=HTMLResponse)
@limiter.limit("100/minute")
async def analyze_post_page(request: Request):
    """
    Trang phân tích bài đăng Facebook
    """
    logger.info(f"Access analyze post page from {request.client.host}")
    return templates.TemplateResponse("analyze.html", {"request": request})

@app.post("/analyze-post", response_model=PostAnalysisResponse)
@limiter.limit("30/minute")
async def analyze_post(
    request: Request,
    analysis_request: PostAnalysisRequest
):
    """
    Endpoint để phân tích bài đăng Facebook
    """
    try:
        logger.info(f"Analyze post request from {request.client.host}: {analysis_request.post_url}")
        result = await post_analysis_service.analyze_post(
            analysis_request.post_url,
            analysis_request.post_content
        )
        return PostAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Error in analyze post endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def search_page(request: Request):
    """
    Trang tìm kiếm
    """
    logger.info(f"Access search page from {request.client.host}")
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/api/search")
@limiter.limit("50/minute")
async def search(
    request: Request,
    q: str = Query(..., description="Từ khóa tìm kiếm")
):
    """
    API endpoint để tìm kiếm thông tin về Facebook
    """
    try:
        logger.info(f"Search request from {request.client.host}: {q}")
        results = await search_service.search(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Tạo thư mục logs nếu chưa tồn tại
    os.makedirs("logs", exist_ok=True)
    uvicorn.run(app, host="localhost", port=8000) 