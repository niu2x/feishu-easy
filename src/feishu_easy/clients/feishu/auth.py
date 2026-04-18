from __future__ import annotations

import time
from typing import Any

import requests

from .constants import FEISHU_RATE_LIMIT_ERROR_CODES, TOKEN_REFRESH_EARLY_SECONDS
from .errors import FeishuAuthError, FeishuHTTPError, FeishuRateLimitError

def load_tenant_access_token_cache(
    cache: dict[str | None, dict[str, Any]], app_id: str | None
) -> dict[str, Any] | None:
    cached = cache.get(app_id)
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

def save_tenant_access_token_cache(
    cache: dict[str | None, dict[str, Any]],
    app_id: str | None,
    payload: dict[str, Any],
) -> None:
    tenant_access_token = payload.get("tenant_access_token")
    expire = payload.get("expire")
    if not isinstance(tenant_access_token, str) or not isinstance(expire, int):
        return

    cache[app_id] = {
        "tenant_access_token": tenant_access_token,
        "expire": expire,
        "fetched_at": int(time.time()),
    }

def tenant_access_token_error_message(payload: dict[str, Any]) -> str:
    request_id = payload.get("request_id") or payload.get("RequestId")
    request_id_suffix = f", request_id: {request_id}" if request_id else ""
    return (
        "get_tenant_access_token failed, "
        f"code: {payload.get('code')}, "
        f"msg: {payload.get('msg')}"
        f"{request_id_suffix}"
    )

def request_tenant_access_token_once(
    *,
    app_id: str | None,
    app_secret: str | None,
    cache: dict[str | None, dict[str, Any]],
) -> dict[str, Any]:
    if not app_id:
        raise FeishuAuthError(
            "get_tenant_access_token failed: app_id is required",
            action="auth.v3.tenant_access_token.internal",
        )
    if not app_secret:
        raise FeishuAuthError(
            "get_tenant_access_token failed: app_secret is required",
            action="auth.v3.tenant_access_token.internal",
        )

    try:
        response = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={
                "app_id": app_id,
                "app_secret": app_secret,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise FeishuHTTPError(
            f"get_tenant_access_token failed: {exc}",
            action="auth.v3.tenant_access_token.internal",
        ) from exc
    except ValueError as exc:
        raise FeishuHTTPError(
            "get_tenant_access_token failed: invalid json response",
            action="auth.v3.tenant_access_token.internal",
        ) from exc

    if not isinstance(payload, dict):
        raise FeishuHTTPError(
            "get_tenant_access_token failed: invalid json payload",
            action="auth.v3.tenant_access_token.internal",
        )

    if payload.get("code") == 0:
        save_tenant_access_token_cache(cache, app_id, payload)
        return payload

    error_message = tenant_access_token_error_message(payload)
    code = payload.get("code")
    if isinstance(code, int) and code in FEISHU_RATE_LIMIT_ERROR_CODES:
        raise FeishuRateLimitError(
            error_message,
            action="auth.v3.tenant_access_token.internal",
            code=code,
            log_id=str(payload.get("request_id") or payload.get("RequestId") or ""),
        )
    raise FeishuAuthError(
        error_message,
        action="auth.v3.tenant_access_token.internal",
        code=code if isinstance(code, int) else None,
        log_id=str(payload.get("request_id") or payload.get("RequestId") or ""),
    )

__all__ = [
    "load_tenant_access_token_cache",
    "save_tenant_access_token_cache",
    "tenant_access_token_error_message",
    "request_tenant_access_token_once",
]
