from __future__ import annotations

from ..feishu_api import FeishuAPI

def get_document(document_id: str) -> dict:
    api = FeishuAPI()
    return api.docx.get_document(document_id)

def raw_content(document_id: str, lang: int = 0) -> dict:
    api = FeishuAPI()
    return api.docx.raw_content(document_id=document_id, lang=lang)

def create_document(title: str, folder_token: str) -> dict:
    api = FeishuAPI()
    return api.docx.create_document(title=title, folder_token=folder_token)

def list_document_block(
    document_id: str,
    document_revision_id: int = -1,
) -> dict:
    api = FeishuAPI()
    return api.docx.list_document_block(
        document_id=document_id,
        document_revision_id=document_revision_id,
    )

def get_document_block_children(document_id: str, block_id: str) -> dict:
    api = FeishuAPI()
    return api.docx.get_document_block_children(document_id, block_id)

def get_document_block(
    document_id: str,
    block_id: str,
    document_revision_id: int = -1,
) -> dict:
    api = FeishuAPI()
    return api.docx.get_document_block(
        document_id=document_id,
        block_id=block_id,
        document_revision_id=document_revision_id,
    )

def batch_delete_document_block_children(
    document_id: str,
    block_id: str,
    start_index: int,
    end_index: int,
) -> dict:
    api = FeishuAPI()
    return api.docx.batch_delete_document_block_children(
        document_id, block_id, start_index, end_index
    )
