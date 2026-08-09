from demo.ui_helpers import format_range, max_page


def test_format_range_empty():
    assert format_range(0, 1, 20) == "No results"


def test_format_range_exact_page():
    assert format_range(20, 1, 20) == "Showing 1–20 of 20"


def test_format_range_partial_last_page():
    assert format_range(21, 2, 20) == "Showing 21–21 of 21"


def test_max_page():
    assert max_page(0, 20) == 1
    assert max_page(1, 20) == 1
    assert max_page(20, 20) == 1
    assert max_page(21, 20) == 2
