def format_range(total: int, page: int, page_size: int) -> str:
    """Return a human-readable range string for pagination.

    Examples:
    - total=0 -> "No results"
    - total=5, page=1, page_size=10 -> "Showing 1–5 of 5"
    - total=137, page=1, page_size=20 -> "Showing 1–20 of 137"
    """
    if total <= 0:
        return "No results"
    page = max(1, page)
    page_size = max(1, page_size)
    start = (page - 1) * page_size + 1
    end = min(page * page_size, total)
    return f"Showing {start}–{end} of {total}"


def max_page(total: int, page_size: int) -> int:
    page_size = max(1, page_size)
    if total <= 0:
        return 1
    return (total + page_size - 1) // page_size
