# COWN - Mạng Xã Hội

🌟 **COWN** là một mạng xã hội hiện đại được xây dựng bằng Node.js, cung cấp các tính năng giao tiếp real-time, chia sẻ vị trí, và kết nối bạn bè.

## 🚀 Tính Năng Chính

- 🏠 **Trang Home** - News feed và timeline cá nhân
- 💬 **Tin Nhắn Real-time** - Chat real-time với Socket.IO
- 🗺️ **Bản Đồ** - Chia sẻ và khám phá vị trí
- 🔍 **Tìm Kiếm** - Tìm kiếm người dùng và nội dung
- ⚙️ **Cài Đặt** - Quản lý tài khoản và quyền riêng tư
- 👥 **Bạn Bè** - Kết nối và quản lý mối quan hệ
- 📱 **Responsive Design** - Tương thích mọi thiết bị

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **Node.js** - Runtime environment
- **Express.js** - Web framework
- **Socket.IO** - Real-time communication
- **PostgreSQL** - Database chính
- **Redis** - Caching và session storage
- **JWT** - Authentication

### Frontend
- **HTML5/CSS3** - Markup và styling
- **JavaScript ES6+** - Client-side logic
- **Bootstrap** - UI framework
- **Socket.IO Client** - Real-time updates

### DevOps & Tools
- **Docker** - Containerization
- **Jest** - Testing framework
- **ESLint** - Code linting
- **Winston** - Logging

## 📁 Cấu Trúc Dự Án

```
cownV1.1.1/
├── src/
│   ├── controllers/          # Logic xử lý request
│   ├── models/              # Database models & DTOs
│   ├── services/            # Business logic
│   ├── routes/              # API & Web routes
│   ├── middleware/          # Custom middleware
│   ├── utils/               # Utilities & helpers
│   ├── config/              # Configuration files
│   ├── validators/          # Input validation
│   └── sockets/             # Real-time handlers
├── public/                  # Static assets
├── views/                   # Template files
├── tests/                   # Test suites
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── migrations/              # Database migrations
└── seeders/                 # Sample data
```

## 🔧 Cài Đặt

### Yêu Cầu Hệ Thống
- Node.js >= 16.0.0
- PostgreSQL >= 13.0
- Redis >= 6.0
- npm hoặc yarn

### Bước 1: Clone Repository
```bash
git clone <repository-url>
cd cownV1.1.1
```

### Bước 2: Cài Đặt Dependencies
```bash
npm install
```

### Bước 3: Cấu Hình Môi Trường
Sao chép file `.env.example` thành `.env` và cập nhật thông tin:
```bash
cp .env.example .env
```

Cập nhật file `.env`:
```env
# Database
DATABASE_URL=postgres://username:password@localhost:5432/cown_db

# Server
PORT=3000
NODE_ENV=development

# JWT
JWT_SECRET=your_super_secret_key
JWT_EXPIRES_IN=7d

# Redis
REDIS_URL=redis://localhost:6379
```

### Bước 4: Khởi Tạo Database
```bash
# Chạy migrations
npm run migrate

# Seed sample data (optional)
npm run seed
```

### Bước 5: Khởi Động Server
```bash
# Development mode
npm run dev

# Production mode
npm start
```

## 🧪 Testing

```bash
# Chạy tất cả tests
npm test

# Chạy tests với coverage
npm run test:coverage

# Chạy tests trong watch mode
npm run test:watch
```

## 📋 Scripts Có Sẵn

```bash
npm start          # Khởi động production server
npm run dev        # Khởi động development server với nodemon
npm test           # Chạy test suite
npm run lint       # Kiểm tra code style
npm run format     # Format code với prettier
npm run migrate    # Chạy database migrations
npm run seed       # Seed sample data
npm run build      # Build cho production
```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký tài khoản mới
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất
- `POST /api/auth/refresh` - Refresh token

### Users
- `GET /api/users/profile` - Lấy thông tin profile
- `PUT /api/users/profile` - Cập nhật profile
- `GET /api/users/search` - Tìm kiếm người dùng

### Messages
- `GET /api/messages` - Lấy danh sách tin nhắn
- `POST /api/messages` - Gửi tin nhắn mới
- `GET /api/messages/:conversationId` - Lấy lịch sử chat

### Friends
- `GET /api/friends` - Danh sách bạn bè
- `POST /api/friends/request` - Gửi lời mời kết bạn
- `PUT /api/friends/accept/:id` - Chấp nhận lời mời
- `DELETE /api/friends/:id` - Hủy kết bạn

## 🔌 Socket Events

### Connection
- `connection` - Client kết nối
- `disconnect` - Client ngắt kết nối

### Messaging
- `join_conversation` - Tham gia cuộc trò chuyện
- `send_message` - Gửi tin nhắn
- `message_received` - Nhận tin nhắn mới
- `typing` - Đang gõ tin nhắn

### Real-time Updates
- `user_online` - User online
- `user_offline` - User offline
- `friend_request` - Lời mời kết bạn mới

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t cown-app .

# Run with Docker Compose
docker-compose up -d
```

## 🔒 Bảo Mật

- JWT Authentication
- Password hashing với bcrypt
- Rate limiting
- CORS protection
- Input validation
- SQL injection prevention
- XSS protection

## 📊 Monitoring & Logging

- Winston logger với multiple transports
- Request/Response logging
- Error tracking
- Performance monitoring
- Health check endpoint: `/health`

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Tạo Pull Request

## 📝 License

Dự án này được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## 👥 Team

- **Developer**: Nghia HT
- **Email**: nghiaht281003@gmail.com

## 🆘 Hỗ Trợ

Nếu bạn gặp vấn đề hoặc có câu hỏi, vui lòng:
1. Kiểm tra [Issues](link-to-issues) hiện có
2. Tạo issue mới với label phù hợp
3. Liên hệ team qua email

## 🚀 Roadmap

- [ ] Mobile app (React Native)
- [ ] Video calling
- [ ] Stories/Status updates
- [ ] Group chat
- [ ] Advanced map features
- [ ] AI-powered recommendations
- [ ] Push notifications
- [ ] Multi-language support

---

⭐ **Nếu dự án này hữu ích, đừng quên star repo này!**
