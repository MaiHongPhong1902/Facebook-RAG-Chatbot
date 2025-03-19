from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
import torch

class RAGModel:
    def __init__(self):
        # Khởi tạo mô hình embedding
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Khởi tạo FAISS index
        self.dimension = 384  # Kích thước vector của mô hình
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Lưu trữ documents và metadata
        self.documents = []
        self.metadata = []
        
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """
        Thêm documents vào hệ thống RAG
        """
        if metadata is None:
            metadata = [{} for _ in documents]
            
        # Tạo embeddings cho documents
        embeddings = self.embedding_model.encode(documents)
        
        # Thêm vào FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Lưu documents và metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Truy xuất k documents liên quan nhất cho câu query
        """
        # Tạo embedding cho query
        query_embedding = self.embedding_model.encode([query])
        
        # Tìm k documents gần nhất
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Trả về documents và metadata tương ứng
        results = []
        for idx in indices[0]:
            results.append({
                'document': self.documents[idx],
                'metadata': self.metadata[idx]
            })
            
        return results
    
    def generate_response(self, query: str, retrieved_docs: List[Dict]) -> str:
        """
        Tạo câu trả lời dựa trên query và documents đã truy xuất
        """
        # TODO: Implement response generation logic
        # Có thể sử dụng LLM như GPT hoặc các mô hình khác
        return "Câu trả lời mẫu dựa trên documents đã truy xuất" 