# TaskHub API 🚀

> Hệ thống quản lý công việc chuyên nghiệp (Production-Ready), được xây dựng với kiến trúc Clean Architecture.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

---

## 🌟 Tính năng nổi bật
* **Clean Architecture:** Phân tách rõ ràng Router → Service → Repository.
* **Bảo mật (Security):** Tích hợp JWT, RBAC (Role-Based Access Control), tự động băm mật khẩu với `bcrypt` và chống truy cập ngoại lai với CORS.
* **Tối ưu hóa (Performance):** Caching siêu tốc với Redis, tối ưu Database Connection Pool, nói không với N+1 Query.
* **Tiêu chuẩn Code (Code Quality):** 
  * Định dạng 100% bằng **Ruff**.
  * Kiểm tra kiểu dữ liệu nghiêm ngặt bằng **MyPy**.
* **DevOps Ready:** Cấu trúc Docker Multi-stage tối ưu dung lượng, phân chia môi trường Dev/Prod rạch ròi cùng Nginx Reverse Proxy.

## 🛠️ Công nghệ sử dụng
* **Core:** Python 3.12, FastAPI, Uvicorn
* **Database:** PostgreSQL, SQLAlchemy 2.0 (Async), Alembic
* **Cache:** Redis
* **Tooling:** `uv` (siêu tốc), Ruff, MyPy, Pytest

## 🚀 Hướng dẫn khởi chạy

### 1. Môi trường Phát triển (Development)
Sử dụng Docker Compose để tạo nhanh môi trường code local với Hot-Reload.

```bash
# Clone dự án
git clone https://github.com/your-username/taskhub-api.git
cd taskhub-api

# Khởi chạy Docker cho Dev
docker compose up -d --build

# API sẽ có mặt tại: http://localhost:8000/docs
```

### 2. Môi trường Sản xuất (Production)
Triển khai lên server với độ an toàn cao nhất (Database ẩn, Nginx bảo vệ).

```bash
# Khởi chạy Docker cho Prod
docker compose -f docker-compose.prod.yml up -d --build
```

## 📂 Kiến trúc Thư mục (Clean Architecture)
```text
app/
├── api/             # API Router (Controllers) & Dependencies
├── core/            # Config, Security, Exception, Cache...
├── db/              # Khởi tạo PostgreSQL Engine & Database Session
├── middleware/      # Interceptors (Logging, CORS,...)
├── models/          # SQLAlchemy Database Models
├── repositories/    # Lớp giao tiếp trực tiếp với Database (CRUD)
├── schemas/         # Pydantic Models (Validate Data In/Out)
└── services/        # Business Logic (Nghiệp vụ cốt lõi)
```

## 🔒 Kiểm tra chất lượng (Quality Check)
Dự án sử dụng `uv` để quản lý môi trường.
```bash
# Cài đặt môi trường ảo bằng uv
uv sync

# Chạy Linter (Ruff)
uv run ruff check .

# Chạy Type Checker (MyPy)
uv run mypy app
```
