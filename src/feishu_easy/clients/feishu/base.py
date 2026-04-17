from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import lark_oapi as lark

if TYPE_CHECKING:
    from ...feishu_api import FeishuAPI

class _FeishuAPIResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.code = payload.get("code")
        self.msg = payload.get("msg")
        self.data = payload.get("data")
        self._log_id = (
            payload.get("request_id")
            or payload.get("RequestId")
            or payload.get("log_id")
            or ""
        )

    def success(self) -> bool:
        return self.code == 0

    def get_log_id(self) -> str:
        return str(self._log_id)

class _BaseAPIGroup:
    def __init__(self, parent: FeishuAPI) -> None:
        self._parent = parent

    def _call_with_retry(self, action: str, call: Callable[[], Any]):
        return self._parent._call_with_retry(action, call)

    def _marshal_data(self, data: Any) -> dict[str, Any]:
        return self._parent._marshal_data(data)

    def _request_option(self) -> lark.RequestOption | None:
        if self._parent._user_access_token:
            return (
                lark.RequestOption.builder()
                .user_access_token(self._parent._user_access_token)
                .build()
            )

        return None
