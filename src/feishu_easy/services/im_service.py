from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI

def get_chat(
    chat_id: str,
    user_id_type: str = "open_id",
) -> dict[str, Any]:
    return _get_chat(chat_id, user_id_type=user_id_type, api=FeishuAPI())

def _get_chat(
    chat_id: str,
    user_id_type: str = "open_id",
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    return api.im.get_chat(chat_id=chat_id, user_id_type=user_id_type)

def list_all_messages(
    container_id_type: str,
    container_id: str,
    start_time: str | None = None,
    end_time: str | None = None,
    sort_type: str | None = None,
    page_size: int = 50,
    limit: int | None = None,
) -> dict[str, Any]:
    return _list_all_messages(
        container_id_type=container_id_type,
        container_id=container_id,
        start_time=start_time,
        end_time=end_time,
        sort_type=sort_type,
        page_size=page_size,
        limit=limit,
        api=FeishuAPI(),
    )

def _list_all_messages(
    container_id_type: str,
    container_id: str,
    start_time: str | None = None,
    end_time: str | None = None,
    sort_type: str | None = None,
    page_size: int = 50,
    limit: int | None = None,
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    return api.im.list_all_messages(
        container_id_type=container_id_type,
        container_id=container_id,
        start_time=start_time,
        end_time=end_time,
        sort_type=sort_type,
        page_size=page_size,
        limit=limit,
    )
