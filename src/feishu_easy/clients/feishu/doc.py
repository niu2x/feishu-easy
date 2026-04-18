from __future__ import annotations

import requests

from .base import _BaseAPIGroup, _FeishuAPIResponse
from .errors import FeishuAuthError, FeishuHTTPError, FeishuResponseError

class FeishuDocAPI(_BaseAPIGroup):
    def _request_doc_content_once(
        self, obj_token: str, token: str
    ) -> _FeishuAPIResponse:
        url = f"https://open.feishu.cn/open-apis/doc/v2/{obj_token}/content"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.Timeout as exc:
            raise TimeoutError("open-apis.doc.v2.content.get timeout") from exc
        except requests.ConnectionError as exc:
            raise ConnectionError(
                "open-apis.doc.v2.content.get connection error"
            ) from exc
        except requests.RequestException as exc:
            raise FeishuHTTPError(
                f"open-apis.doc.v2.content.get failed: {exc}",
                action="open-apis.doc.v2.content.get",
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise FeishuHTTPError(
                "open-apis.doc.v2.content.get failed: invalid json response",
                action="open-apis.doc.v2.content.get",
            ) from exc

        if not isinstance(payload, dict):
            raise FeishuHTTPError(
                "open-apis.doc.v2.content.get failed: invalid json payload",
                action="open-apis.doc.v2.content.get",
            )

        return _FeishuAPIResponse(payload)

    def get_doc_content(self, obj_token: str) -> str:
        token = self._parent.get_access_token()
        if not isinstance(token, str) or not token:
            raise FeishuAuthError(
                "get_doc_content failed: access_token missing",
                action="open-apis.doc.v2.content.get",
            )

        wrapped_response = self._call_with_retry(
            "open-apis.doc.v2.content.get",
            lambda: self._request_doc_content_once(obj_token, token),
        )

        if not isinstance(wrapped_response.data, dict):
            raise FeishuResponseError(
                "open-apis.doc.v2.content.get failed: data missing",
                action="open-apis.doc.v2.content.get",
            )

        content = wrapped_response.data.get("content")
        if not isinstance(content, str):
            raise FeishuResponseError(
                "open-apis.doc.v2.content.get failed: data.content missing",
                action="open-apis.doc.v2.content.get",
            )

        return content
