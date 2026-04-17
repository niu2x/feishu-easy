from __future__ import annotations

import json
import time
from typing import Any, Callable

import lark_oapi as lark
import requests
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .clients.feishu import (
    FEISHU_RATE_LIMIT_ERROR_CODES,
    TOKEN_REFRESH_EARLY_SECONDS,
    FeishuBitableAPI,
    FeishuBoardAPI,
    FeishuDocAPI,
    FeishuDocxAPI,
    FeishuDriveAPI,
    FeishuRateLimitError,
    FeishuSheetsAPI,
    FeishuWikiAPI,
)


class FeishuAPI:
    _tenant_token_cache: dict[str, dict[str, Any]] = {}
    _default_app_id: str | None = None
    _default_app_secret: str | None = None
    _default_user_access_token: str | None = None

    @classmethod
    def configure_defaults(
        cls,
        *,
        app_id: str | None = None,
        app_secret: str | None = None,
        user_access_token: str | None = None,
    ) -> None:
        if app_id is not None:
            cls._default_app_id = app_id
        if app_secret is not None:
            cls._default_app_secret = app_secret
        if user_access_token is not None:
            cls._default_user_access_token = user_access_token

    def __init__(
        self,
        *,
        app_id: str | None = None,
        app_secret: str | None = None,
    ) -> None:
        self.app_id = app_id or self._default_app_id
        self.app_secret = app_secret or self._default_app_secret
        self._user_access_token: str | None = None

        if self._default_user_access_token:
            self._user_access_token = self._default_user_access_token
            self.client = (
                lark.Client.builder()
                .app_id(self.app_id or "")
                .enable_set_token(True)
                .log_level(lark.LogLevel.ERROR)
                .build()
            )
            self._init_api_parts()
            return

        if not self.app_id:
            raise ValueError("FeishuAPI requires app_id")

        if not self.app_secret:
            raise ValueError("FeishuAPI requires app_secret")

        self.client = (
            lark.Client.builder()
            .app_id(self.app_id)
            .app_secret(self.app_secret)
            .log_level(lark.LogLevel.ERROR)
            .build()
        )
        self._init_api_parts()

    def _init_api_parts(self) -> None:
        self.board = FeishuBoardAPI(self)
        self.bitable = FeishuBitableAPI(self)
        self.doc = FeishuDocAPI(self)
        self.docx = FeishuDocxAPI(self)
        self.wiki = FeishuWikiAPI(self)
        self.drive = FeishuDriveAPI(self)
        self.sheets = FeishuSheetsAPI(self)

    @staticmethod
    def _response_error_message(action: str, response: Any) -> str:
        return (
            f"{action} failed, code: {response.code}, "
            f"msg: {response.msg}, log_id: {response.get_log_id()}"
        )

    def _raise_for_failed_response(self, action: str, response: Any) -> None:
        if response.success():
            return

        error_message = self._response_error_message(action, response)
        lark.logger.error(error_message)

        if response.code in FEISHU_RATE_LIMIT_ERROR_CODES:
            raise FeishuRateLimitError(error_message)

        raise RuntimeError(error_message)

    @staticmethod
    def _marshal_data(data: Any) -> dict[str, Any]:
        return json.loads(lark.JSON.marshal(data))

    @staticmethod
    def _before_sleep_log(retry_state: RetryCallState) -> None:
        if retry_state.outcome is None:
            return
        exception = retry_state.outcome.exception()
        if exception is None:
            return
        lark.logger.warning(
            "Retrying Feishu request after error: %s (attempt %s)",
            exception,
            retry_state.attempt_number,
        )

    def _call_with_retry(self, action: str, call: Callable[[], Any]) -> Any:
        @retry(
            stop=stop_after_attempt(16),
            wait=wait_exponential(multiplier=1, min=1, max=120),
            retry=retry_if_exception_type(
                (FeishuRateLimitError, ConnectionError, TimeoutError)
            ),
            before_sleep=self._before_sleep_log,
            reraise=True,
        )
        def _wrapped_call() -> Any:
            response = call()
            self._raise_for_failed_response(action, response)
            return response

        return _wrapped_call()

    def _load_tenant_access_token_cache(self) -> dict[str, Any] | None:
        app_id = self.app_id
        cached = self._tenant_token_cache.get(app_id)
        if cached is None:
            return None

        tenant_access_token = cached.get("tenant_access_token")
        fetched_at = cached.get("fetched_at")
        expire = cached.get("expire")
        if (
            not isinstance(tenant_access_token, str)
            or not isinstance(fetched_at, int)
            or not isinstance(expire, int)
        ):
            return None

        refresh_at = fetched_at + expire - TOKEN_REFRESH_EARLY_SECONDS
        now = int(time.time())
        if now >= refresh_at:
            return None

        return {
            "code": 0,
            "msg": "ok",
            "tenant_access_token": tenant_access_token,
            "expire": fetched_at + expire - now,
        }

    def _save_tenant_access_token_cache(self, payload: dict[str, Any]) -> None:
        tenant_access_token = payload.get("tenant_access_token")
        expire = payload.get("expire")
        if not isinstance(tenant_access_token, str) or not isinstance(expire, int):
            return

        self._tenant_token_cache[self.app_id] = {
            "tenant_access_token": tenant_access_token,
            "expire": expire,
            "fetched_at": int(time.time()),
        }

    @staticmethod
    def _tenant_access_token_error_message(payload: dict[str, Any]) -> str:
        request_id = payload.get("request_id") or payload.get("RequestId")
        request_id_suffix = f", request_id: {request_id}" if request_id else ""
        return (
            "get_tenant_access_token failed, "
            f"code: {payload.get('code')}, "
            f"msg: {payload.get('msg')}"
            f"{request_id_suffix}"
        )

    def _request_tenant_access_token_once(self) -> dict[str, Any]:
        try:
            response = requests.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"get_tenant_access_token failed: {exc}") from exc

        if payload.get("code") == 0:
            self._save_tenant_access_token_cache(payload)
            return payload

        error_message = self._tenant_access_token_error_message(payload)
        if payload.get("code") in FEISHU_RATE_LIMIT_ERROR_CODES:
            raise FeishuRateLimitError(error_message)
        raise RuntimeError(error_message)

    def get_tenant_access_token(self) -> dict[str, Any]:
        if not self.app_secret:
            raise RuntimeError(
                "get_tenant_access_token failed: app_secret is required. "
                "This instance was created with --run-as-user."
            )
        cached = self._load_tenant_access_token_cache()
        if cached is not None:
            return cached
        return self._request_tenant_access_token_once()

    def get_access_token(self) -> str | None:
        if self._user_access_token:
            return self._user_access_token
        return self.get_tenant_access_token().get("tenant_access_token")


__all__ = ["FeishuAPI", "FeishuRateLimitError"]
