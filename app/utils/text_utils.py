import re
from typing import List

def clean_text(text: str) -> str:
    """
    Làm sạch văn bản
    """
    # Loại bỏ ký tự đặc biệt
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    # Chuyển về chữ thường
    text = text.lower()
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Chia văn bản thành các đoạn nhỏ
    """
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
        
    return chunks

def extract_hashtags(text: str) -> List[str]:
    """
    Trích xuất hashtags từ văn bản
    """
    hashtags = re.findall(r'#\w+', text)
    return hashtags

def extract_mentions(text: str) -> List[str]:
    """
    Trích xuất mentions từ văn bản
    """
    mentions = re.findall(r'@\w+', text)
    return mentions

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Tính độ tương đồng giữa hai văn bản
    """
    # TODO: Implement similarity calculation
    # Có thể sử dụng các phương pháp như cosine similarity
    return 0.0 