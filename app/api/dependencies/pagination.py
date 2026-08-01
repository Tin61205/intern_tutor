# app/api/dependencies/pagination.py
from fastapi import Query


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, description="Bỏ qua N bản ghi đầu tiên", ge=0),
        limit: int = Query(
            10, description="Giới hạn số lượng bản ghi trả về", ge=1, le=100
        ),
    ):
        self.skip = skip
        self.limit = limit
