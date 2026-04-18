from __future__ import annotations

from ..feishu_api import FeishuAPI


def get_document(
    document_id: str,
) -> dict:
    return _get_document(document_id, api=FeishuAPI())


def _get_document(
    document_id: str,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.get_document(document_id)


def raw_content(
    document_id: str,
    lang: int = 0,
) -> dict:
    return _raw_content(document_id, lang=lang, api=FeishuAPI())


def _raw_content(
    document_id: str,
    lang: int = 0,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.raw_content(document_id=document_id, lang=lang)


def create_document(
    title: str,
    folder_token: str,
) -> dict:
    return _create_document(title, folder_token, api=FeishuAPI())


def _create_document(
    title: str,
    folder_token: str,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.create_document(title=title, folder_token=folder_token)


def list_document_block(
    document_id: str,
    document_revision_id: int = -1,
) -> dict:
    return _list_document_block(
        document_id,
        document_revision_id=document_revision_id,
        api=FeishuAPI(),
    )


def _list_document_block(
    document_id: str,
    document_revision_id: int = -1,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.list_document_block(
        document_id=document_id,
        document_revision_id=document_revision_id,
    )


def get_document_block_children(
    document_id: str,
    block_id: str,
) -> dict:
    return _get_document_block_children(document_id, block_id, api=FeishuAPI())


def _get_document_block_children(
    document_id: str,
    block_id: str,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.get_document_block_children(document_id, block_id)


def get_document_block(
    document_id: str,
    block_id: str,
    document_revision_id: int = -1,
) -> dict:
    return _get_document_block(
        document_id,
        block_id,
        document_revision_id=document_revision_id,
        api=FeishuAPI(),
    )


def _get_document_block(
    document_id: str,
    block_id: str,
    document_revision_id: int = -1,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.get_document_block(
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
    return _batch_delete_document_block_children(
        document_id,
        block_id,
        start_index,
        end_index,
        api=FeishuAPI(),
    )


def _batch_delete_document_block_children(
    document_id: str,
    block_id: str,
    start_index: int,
    end_index: int,
    *,
    api: FeishuAPI,
) -> dict:
    feishu_api = api
    return feishu_api.docx.batch_delete_document_block_children(
        document_id, block_id, start_index, end_index
    )
