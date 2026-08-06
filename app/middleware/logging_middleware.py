# app/middleware/logging_middleware.py
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware chặn mọi request đi vào và mọi response đi ra khỏi hệ thống.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Sinh ra một ID duy nhất cho mỗi Request (Dành cho Bước 9)
        request_id = str(uuid.uuid4())

        # 2. Ghi nhận thời gian bắt đầu
        start_time = time.time()

        # 3. Lấy thông tin Client
        client_ip = request.client.host if request.client else "Unknown IP"
        method = request.method
        url = request.url.path

        try:
            # 4. Giao Request cho các Router/API xử lý
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            # 5. Xử lý sau khi API đã chạy xong (Bất kể lỗi hay thành công)
            process_time = time.time() - start_time

            # Ghi Log
            logger.info(
                f"[{request_id}] {client_ip} | {method} {url} | Status: {status_code} | Time: {process_time:.4f}s"
            )

        # 6. Nhét Request ID vào Header để trả về cho Client
        response.headers["X-Request-ID"] = request_id

        return response
