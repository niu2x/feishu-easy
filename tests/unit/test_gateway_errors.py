from __future__ import annotations

import pytest

from feishu_easy.clients.feishu.errors import FeishuAPIError, FeishuRateLimitError
from feishu_easy.clients.feishu.gateway import FeishuAPI

class _FakeResponse:
    def __init__(self, *, code: int, msg: str = "bad", log_id: str = "log_1") -> None:
        self.code = code
        self.msg = msg
        self._log_id = log_id

    def success(self) -> bool:
        return False

    def get_log_id(self) -> str:
        return self._log_id

def test_raise_for_failed_response_rate_limit() -> None:
    api = object.__new__(FeishuAPI)
    with pytest.raises(FeishuRateLimitError):
        api._raise_for_failed_response(
            "client.docx.v1.document.get",
            _FakeResponse(code=99991400),
        )

def test_raise_for_failed_response_api_error() -> None:
    api = object.__new__(FeishuAPI)
    with pytest.raises(FeishuAPIError):
        api._raise_for_failed_response(
            "client.docx.v1.document.get",
            _FakeResponse(code=400),
        )
