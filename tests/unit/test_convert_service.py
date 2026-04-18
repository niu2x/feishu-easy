from __future__ import annotations

import pytest

from feishu_easy.services.convert_service import (
    convert_from_feishu,
    normalize_payload,
    resolve_sheet_asset_tokens,
)
from feishu_easy.services.errors import ServiceValidationError


def test_resolve_sheet_asset_tokens_success() -> None:
    spreadsheet_token, sheet_token = resolve_sheet_asset_tokens("shtcn123_sheet001")
    assert spreadsheet_token == "shtcn123"
    assert sheet_token == "sheet001"


def test_resolve_sheet_asset_tokens_invalid() -> None:
    with pytest.raises(ServiceValidationError):
        resolve_sheet_asset_tokens("invalid-token")


def test_convert_from_feishu_invalid_json() -> None:
    with pytest.raises(ServiceValidationError):
        convert_from_feishu(
            "{not-json}",
            source_type="doc",
            target_type="unified",
            mode="online",
        )


def test_convert_from_feishu_non_object_json() -> None:
    with pytest.raises(ServiceValidationError):
        convert_from_feishu(
            "[]",
            source_type="doc",
            target_type="unified",
            mode="online",
        )


def test_normalize_payload_bitable_invalid() -> None:
    with pytest.raises(ServiceValidationError):
        normalize_payload(
            {
                "node": {"title": "demo"},
                "obj": [{"app_token": "app", "table": {}, "data": "not-list"}],
            },
            source_type="bitable",
        )
