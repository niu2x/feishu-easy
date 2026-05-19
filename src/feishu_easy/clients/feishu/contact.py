from __future__ import annotations

import json
from typing import Any

import requests

from lark_oapi.api.contact.v3 import BatchUserRequest, GetUserRequest

from .base import _BaseAPIGroup, _FeishuAPIResponse
from .errors import FeishuAuthError, FeishuHTTPError, FeishuResponseError

class FeishuContactAPI(_BaseAPIGroup):
    def _request_basic_batch_once(
        self, user_ids: list[str], user_id_type: str, token: str
    ) -> _FeishuAPIResponse:
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/basic_batch?user_id_type={user_id_type}"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        }
        body = json.dumps({"user_ids": user_ids})

        try:
            response = requests.post(url, headers=headers, data=body, timeout=30)
        except requests.Timeout as exc:
            raise TimeoutError("open-apis.contact.v3.users.basic_batch timeout") from exc
        except requests.ConnectionError as exc:
            raise ConnectionError(
                "open-apis.contact.v3.users.basic_batch connection error"
            ) from exc
        except requests.RequestException as exc:
            raise FeishuHTTPError(
                f"open-apis.contact.v3.users.basic_batch failed: {exc}",
                action="open-apis.contact.v3.users.basic_batch",
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise FeishuHTTPError(
                "open-apis.contact.v3.users.basic_batch failed: invalid json response",
                action="open-apis.contact.v3.users.basic_batch",
            ) from exc

        if not isinstance(payload, dict):
            raise FeishuHTTPError(
                "open-apis.contact.v3.users.basic_batch failed: invalid json payload",
                action="open-apis.contact.v3.users.basic_batch",
            ) from exc

        return _FeishuAPIResponse(payload)

    def basic_batch_get_user(
        self,
        user_ids: list[str],
        user_id_type: str = "open_id",
    ) -> dict[str, Any]:
        token = self._parent.get_access_token()
        if not isinstance(token, str) or not token:
            raise FeishuAuthError(
                "basic_batch_get_user failed: access_token missing",
                action="open-apis.contact.v3.users.basic_batch",
            )

        wrapped_response = self._call_with_retry(
            "open-apis.contact.v3.users.basic_batch",
            lambda: self._request_basic_batch_once(user_ids, user_id_type, token),
        )

        if not isinstance(wrapped_response.data, dict):
            raise FeishuResponseError(
                "open-apis.contact.v3.users.basic_batch failed: data missing",
                action="open-apis.contact.v3.users.basic_batch",
            )

        return wrapped_response.data

    def batch_get_user(
        self,
        user_ids: list[str],
        user_id_type: str = "open_id",
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            BatchUserRequest.builder()
            .user_id_type(user_id_type)
            .user_ids(user_ids)
            .build()
        )

        response = self._call_with_retry(
            "client.contact.v3.user.batch",
            lambda: self._parent.client.contact.v3.user.batch(request, option),
        )
        return self._marshal_data(response.data)

    def get_user(
        self,
        user_id: str,
        user_id_type: str = "open_id",
        department_id_type: str = "open_department_id",
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetUserRequest.builder()
            .user_id(user_id)
            .user_id_type(user_id_type)
            .department_id_type(department_id_type)
            .build()
        )

        response = self._call_with_retry(
            "client.contact.v3.user.get",
            lambda: self._parent.client.contact.v3.user.get(request, option),
        )
        return self._marshal_data(response.data)
