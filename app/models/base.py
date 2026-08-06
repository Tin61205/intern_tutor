# app/models/base.py
from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Class gốc cho tất cả các Model của dự án.
    Mọi Model (User, Task,...) đều sẽ kế thừa từ class này.
    """

    id: Any
