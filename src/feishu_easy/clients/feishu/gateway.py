from __future__ import annotations

import json
from typing import Any, Callable

import lark_oapi as lark

from .auth import load_tenant_access_token_cache, request_tenant_access_token_once
from .bitable import FeishuBitableAPI
from .board import FeishuBoardAPI
from .constants import FEISHU_RATE_LIMIT_ERROR_CODES
from .doc import FeishuDocAPI
from .docx import FeishuDocxAPI
from .drive import FeishuDriveAPI
from .errors import FeishuAPIError, FeishuRateLimitError
from .retry import call_with_retry
from .sheets import FeishuSheetsAPI
from .wiki import FeishuWikiAPI

class FeishuAPI:
    _tenant_token_cache: dict[str | None, dict[str, Any]] = {}
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
            raise FeishuRateLimitError(
                error_message,
                action=action,
                code=response.code,
                log_id=response.get_log_id(),
            )

        raise FeishuAPIError(
            error_message,
            action=action,
            code=response.code,
            log_id=response.get_log_id(),
        )

    @staticmethod
    def _marshal_data(data: Any) -> dict[str, Any]:
        return json.loads(lark.JSON.marshal(data))

    def _call_with_retry(self, action: str, call: Callable[[], Any]) -> Any:
        return call_with_retry(
            action,
            call,
            validate_response=self._raise_for_failed_response,
        )

    def _load_tenant_access_token_cache(self) -> dict[str, Any] | None:
        return load_tenant_access_token_cache(self._tenant_token_cache, self.app_id)

    def _request_tenant_access_token_once(self) -> dict[str, Any]:
        return request_tenant_access_token_once(
            app_id=self.app_id,
            app_secret=self.app_secret,
            cache=self._tenant_token_cache,
        )

    def get_tenant_access_token(self) -> dict[str, Any]:
        if not self.app_secret:
            raise ValueError(
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

__all__ = ["FeishuAPI", "FeishuRateLimitError", "FeishuAPIError"]
