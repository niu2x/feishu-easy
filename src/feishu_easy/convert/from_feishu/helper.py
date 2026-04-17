from __future__ import annotations

import urllib
from typing import Any


def build_feishu_resource_url(root: str, link_data: dict[str, Any] | None) -> str:
    if not link_data:
        return root

    params = {k: v for k, v in link_data.items() if v is not None}
    if not params:
        return root

    query_string = urllib.parse.urlencode(params)
    if "?" in root:
        return f"{root}&{query_string}"
    return f"{root}?{query_string}"
