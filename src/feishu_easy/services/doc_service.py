from __future__ import annotations

from ..feishu_api import FeishuAPI

def get_doc_content(obj_token: str, *, api: FeishuAPI | None = None) -> str:
    feishu_api = api or FeishuAPI()
    return feishu_api.doc.get_doc_content(obj_token=obj_token)
