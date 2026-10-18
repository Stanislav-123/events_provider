from datetime import date

from fastapi import Request
from starlette.datastructures import URL


def build_page_link(
    request: Request,
    *,
    page: int,
    page_size: int,
    date_from: date | None,
    total: int,
) -> str | None:
    if page < 1:
        return None
    max_page = max(1, (total + page_size - 1) // page_size) if total else 1
    if page > max_page:
        return None

    params: dict[str, str] = {
        "page": str(page),
        "page_size": str(page_size),
    }
    if date_from is not None:
        params["date_from"] = date_from.isoformat()

    url = URL(str(request.url_for("list_events"))).include_query_params(**params)
    return str(url)
