# app/core/logging.py
import logging
import os
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging():
    """
    Khởi tạo hệ thống Logging chuyên nghiệp cho Production.
    Bao gồm cả Console Logger (in ra terminal) và File Logger (lưu vào file).
    """
    # Tạo thư mục 'logs' ở thư mục gốc của project nếu chưa tồn tại
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "app.log")

    # Đọc mức độ Log từ cấu hình (VD: DEBUG, INFO)
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # --- BƯỚC 7: STRUCTURED LOGGING (Định dạng Log có cấu trúc) ---
    # asctime: Thời gian
    # levelname: Mức độ (INFO/ERROR)
    # module, funcName, lineno: Dấu vết xem log này được gọi từ file nào, hàm nào, dòng số mấy
    # message: Nội dung log
    log_format = (
        "[%(asctime)s] | %(levelname)-8s | "
        "%(module)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # --- BƯỚC 5: CONSOLE LOGGER ---
    # Chuyên để in ra màn hình khi dev chạy ở local
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # --- BƯỚC 6: LOG ROTATION (Luân chuyển file) ---
    # Tránh tình trạng file log phình to lên hàng chục GB làm sập ổ cứng.
    # Cấu hình dưới đây: Nếu file app.log vượt quá 5MB, tự động cắt ra thành app.log.1
    # Và chỉ giữ lại tối đa 5 file cũ (backupCount=5).
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Thiết lập cho Root Logger (Đây là ông trùm bắt mọi log của dự án)
    # force=True để ghi đè các cấu hình log lởm khởm cũ của FastAPI/Uvicorn nếu có
    logging.basicConfig(
        level=log_level, handlers=[console_handler, file_handler], force=True
    )

    # Giảm bớt "log rác" từ các thư viện bên ngoài để đỡ rối mắt
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
