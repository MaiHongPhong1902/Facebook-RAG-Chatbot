import os
from typing import List, Dict
import json
from bs4 import BeautifulSoup
import requests

class DataService:
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def save_document(self, content: str, metadata: Dict, filename: str):
        """
        Lưu document và metadata vào file
        """
        filepath = os.path.join(self.data_dir, filename)
        data = {
            "content": content,
            "metadata": metadata
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_document(self, filename: str) -> Dict:
        """
        Đọc document từ file
        """
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def crawl_facebook_help(self, url: str) -> List[Dict]:
        """
        Crawl dữ liệu từ trang trợ giúp Facebook
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # TODO: Implement specific crawling logic for Facebook Help
            # This is just a placeholder
            documents = []
            for article in soup.find_all("article"):
                title = article.find("h2").text
                content = article.find("div", class_="content").text
                documents.append({
                    "content": content,
                    "metadata": {
                        "title": title,
                        "source": url
                    }
                })
                
            return documents
            
        except Exception as e:
            print(f"Error crawling Facebook Help: {str(e)}")
            return []
            
    def process_facebook_post(self, post_url: str) -> Dict:
        """
        Xử lý và phân tích bài đăng Facebook
        """
        # TODO: Implement Facebook post processing
        # This would require Facebook API access
        return {
            "content": "Nội dung bài đăng mẫu",
            "metadata": {
                "likes": 100,
                "comments": 10,
                "shares": 5
            }
        } 