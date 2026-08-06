# ==========================================
# STAGE 1: Builder (Dùng uv để cài đặt dependencies)
# ==========================================
FROM python:3.12-slim AS builder

# Lấy binary uv đã được tối ưu từ registry chính thức của Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

# Tối ưu cache cho uv: Không lưu cache gói tải về để giảm dung lượng build
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

# Tạo môi trường ảo độc lập bằng uv
RUN uv venv /opt/venv

# Kích hoạt venv cho các câu lệnh RUN tiếp theo và ép uv sử dụng nó
ENV VIRTUAL_ENV="/opt/venv" \
    UV_PROJECT_ENVIRONMENT="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

# Copy file định nghĩa thư viện (uv dùng pyproject.toml + uv.lock)
COPY pyproject.toml uv.lock ./

# Cài đặt thư viện siêu tốc vào /opt/venv bằng uv (chỉ cài production, không cài project code)
RUN uv sync --frozen --no-dev --no-install-project


# ==========================================
# STAGE 2: Runtime (Gọn nhẹ cho Production)
# ==========================================
FROM python:3.12-slim

# Cấu hình tối ưu cho môi trường Python trong Container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Tạo non-root user đảm bảo an toàn bảo mật
RUN adduser --disabled-password --gecos "" taskhubuser

WORKDIR /app

# Copy môi trường ảo chứa đầy đủ thư viện từ Stage Builder sang
COPY --from=builder /opt/venv /opt/venv

# Copy toàn bộ mã nguồn ứng dụng
COPY . .

# Phân quyền cho user
RUN chown -R taskhubuser:taskhubuser /app

# Khóa container chạy dưới quyền user thường
USER taskhubuser

# Khai báo Port
EXPOSE 8000

# Khởi chạy FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]