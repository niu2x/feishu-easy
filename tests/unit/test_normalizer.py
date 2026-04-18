from __future__ import annotations

from feishu_easy.convert.from_feishu.normalizer import normalize_title

def test_normalize_title_returns_trimmed_text() -> None:
    assert normalize_title("  Hello  ") == "Hello"

def test_normalize_title_returns_none_for_non_string_or_empty() -> None:
    assert normalize_title(123) is None
    assert normalize_title("   ") is None
