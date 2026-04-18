from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI


def get_tenant_access_token(*, api: FeishuAPI | None = None) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.get_tenant_access_token()
