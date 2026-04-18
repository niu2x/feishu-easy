from __future__ import annotations

from ..feishu_api import FeishuAPI

def get_doc_content(obj_token: str) -> str:
    return _get_doc_content(obj_token, api=FeishuAPI())

def _get_doc_content(obj_token: str, *, api: FeishuAPI) -> str:
    feishu_api = api
    return feishu_api.doc.get_doc_content(obj_token=obj_token)
