from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI

def batch_get_user(
    user_ids: list[str],
    user_id_type: str = "open_id",
) -> dict[str, Any]:
    return _batch_get_user(user_ids, user_id_type=user_id_type, api=FeishuAPI())

def _batch_get_user(
    user_ids: list[str],
    user_id_type: str = "open_id",
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    return api.contact.batch_get_user(user_ids=user_ids, user_id_type=user_id_type)

def basic_batch_get_user(
    user_ids: list[str],
    user_id_type: str = "open_id",
) -> dict[str, Any]:
    return _basic_batch_get_user(user_ids, user_id_type=user_id_type, api=FeishuAPI())

def _basic_batch_get_user(
    user_ids: list[str],
    user_id_type: str = "open_id",
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    return api.contact.basic_batch_get_user(user_ids=user_ids, user_id_type=user_id_type)

def get_user(
    user_id: str,
    user_id_type: str = "open_id",
    department_id_type: str = "open_department_id",
) -> dict[str, Any]:
    return _get_user(
        user_id, user_id_type=user_id_type, department_id_type=department_id_type, api=FeishuAPI()
    )

def _get_user(
    user_id: str,
    user_id_type: str = "open_id",
    department_id_type: str = "open_department_id",
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    return api.contact.get_user(
        user_id=user_id, user_id_type=user_id_type, department_id_type=department_id_type
    )
