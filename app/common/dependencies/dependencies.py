from fastapi import Query

from app.common.dependencies.dependencies_schemas import PaginationParams


def get_pagination_params(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> PaginationParams:
    return PaginationParams(
        limit=size,
        offset=(page - 1) * size
    )