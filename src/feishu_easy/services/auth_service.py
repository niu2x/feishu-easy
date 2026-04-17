from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI


def get_tenant_access_token() -> dict[str, Any]:
    api = FeishuAPI()
    return api.get_tenant_access_token()
