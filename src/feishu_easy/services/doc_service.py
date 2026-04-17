from __future__ import annotations

from ..feishu_api import FeishuAPI


def get_doc_content(obj_token: str) -> str:
    api = FeishuAPI()
    return api.doc.get_doc_content(obj_token=obj_token)
