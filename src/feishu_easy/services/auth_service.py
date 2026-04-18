from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI


def get_tenant_access_token() -> dict[str, Any]:
    return _get_tenant_access_token(api=FeishuAPI())


def _get_tenant_access_token(*, api: FeishuAPI) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.get_tenant_access_token()
