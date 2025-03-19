# Facebook RAG Chatbot

Chatbot thông minh sử dụng RAG (Retrieval-Augmented Generation) để phân tích và trả lời các câu hỏi về Facebook. Dự án này tích hợp các công nghệ AI tiên tiến để cung cấp thông tin chính xác và hữu ích về Facebook.

## Tính năng chính

- 🔍 Tìm kiếm thông tin thông minh về Facebook
- 📊 Phân tích bài đăng Facebook
- 🤖 Tương tác thông qua giao diện chat
- 📱 Giao diện người dùng thân thiện
- 🔄 Tự động cập nhật cơ sở tri thức
- 🛡️ Bảo mật và giới hạn tốc độ truy cập

## Công nghệ sử dụng

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: 
  - DeepSeek R1 Zero (thông qua OpenRouter API)
  - RAG (Retrieval-Augmented Generation)
- **Database**: SQLite
- **Authentication**: JWT

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/chatbotRAG-FB.git
cd chatbotRAG-FB
```

2. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Tạo file `.env` và cấu hình các biến môi trường:
```env
OPENROUTER_API_KEY=your_api_key_here
FB_ACCESS_TOKEN=your_facebook_access_token
```

5. Khởi động ứng dụng:
```bash
uvicorn app.main:app --reload
```

## Cấu trúc dự án

```
chatbotRAG-FB/
├── app/
│   ├── main.py              # Entry point của ứng dụng
│   ├── services/            # Các service xử lý logic
│   │   ├── deepseek_service.py
│   │   ├── llm_service.py
│   │   ├── post_analysis_service.py
│   │   └── search_service.py
│   ├── static/             # Tài nguyên tĩnh
│   │   ├── css/
│   │   └── js/
│   └── templates/          # Templates HTML
├── tests/                  # Unit tests
├── requirements.txt        # Dependencies
└── README.md
```

## API Endpoints

- `GET /`: Trang chủ
- `GET /chat`: Giao diện chat
- `GET /analyze`: Giao diện phân tích bài đăng
- `POST /search`: API tìm kiếm thông tin
- `POST /analyze`: API phân tích bài đăng

## Tính năng chi tiết

### 1. Tìm kiếm thông tin
- Tìm kiếm thông minh trong cơ sở tri thức
- Phân tích ngữ nghĩa câu hỏi
- Trả về kết quả có độ liên quan cao

### 2. Phân tích bài đăng
- Phân tích nội dung bài đăng
- Đánh giá cảm xúc
- Xác định chủ đề chính
- Trích xuất thông tin quan trọng

### 3. Cơ sở tri thức
- Tự động cập nhật từ Facebook Newsroom
- Tích hợp tài liệu hướng dẫn Facebook
- Lưu trữ và quản lý thông tin hiệu quả

## Bảo mật

- Rate limiting để tránh quá tải
- Xác thực JWT cho API
- CORS middleware
- Xử lý lỗi và logging

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## License

Dự án được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## Liên hệ

- Website: [your-website]
- Email: [your-email]
- LinkedIn: [your-linkedin]
- GitHub: [your-github] 