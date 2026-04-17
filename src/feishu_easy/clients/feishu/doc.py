from __future__ import annotations

import requests

from .base import _BaseAPIGroup, _FeishuAPIResponse

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
            raise RuntimeError(f"open-apis.doc.v2.content.get failed: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "open-apis.doc.v2.content.get failed: invalid json response"
            ) from exc

        if not isinstance(payload, dict):
            raise RuntimeError(
                "open-apis.doc.v2.content.get failed: invalid json payload"
            )

        return _FeishuAPIResponse(payload)

    def get_doc_content(self, obj_token: str) -> str:
        token = self._parent.get_access_token()
        if not isinstance(token, str) or not token:
            raise RuntimeError("get_doc_content failed: access_token missing")

        wrapped_response = self._call_with_retry(
            "open-apis.doc.v2.content.get",
            lambda: self._request_doc_content_once(obj_token, token),
        )

        if not isinstance(wrapped_response.data, dict):
            raise RuntimeError("open-apis.doc.v2.content.get failed: data missing")

        content = wrapped_response.data.get("content")
        if not isinstance(content, str):
            raise RuntimeError(
                "open-apis.doc.v2.content.get failed: data.content missing"
            )

        return content
