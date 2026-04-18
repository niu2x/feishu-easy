from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI

def get_app(
    app_token: str,
    *,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    return _get_app(app_token, user_id_type=user_id_type, api=FeishuAPI())

def _get_app(
    app_token: str,
    *,
    user_id_type: str | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.get_app(
        app_token=app_token,
        user_id_type=user_id_type,
    )

def list_app_table(
    app_token: str,
) -> dict[str, Any]:
    return _list_app_table(app_token, api=FeishuAPI())

def _list_app_table(
    app_token: str,
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.list_app_table(app_token=app_token)

def list_app_table_field(
    app_token: str,
    table_id: str,
    *,
    view_id: str | None = None,
    text_field_as_array: bool | None = None,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    return _list_app_table_field(
        app_token,
        table_id,
        view_id=view_id,
        text_field_as_array=text_field_as_array,
        user_id_type=user_id_type,
        api=FeishuAPI(),
    )

def _list_app_table_field(
    app_token: str,
    table_id: str,
    *,
    view_id: str | None = None,
    text_field_as_array: bool | None = None,
    user_id_type: str | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.list_app_table_field(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        text_field_as_array=text_field_as_array,
        user_id_type=user_id_type,
    )

def list_app_table_view(
    app_token: str,
    table_id: str,
    *,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    return _list_app_table_view(
        app_token,
        table_id,
        user_id_type=user_id_type,
        api=FeishuAPI(),
    )

def _list_app_table_view(
    app_token: str,
    table_id: str,
    *,
    user_id_type: str | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.list_app_table_view(
        app_token=app_token,
        table_id=table_id,
        user_id_type=user_id_type,
    )

def get_app_table_view(
    app_token: str,
    table_id: str,
    view_id: str,
    *,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    return _get_app_table_view(
        app_token,
        table_id,
        view_id,
        user_id_type=user_id_type,
        api=FeishuAPI(),
    )

def _get_app_table_view(
    app_token: str,
    table_id: str,
    view_id: str,
    *,
    user_id_type: str | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.get_app_table_view(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        user_id_type=user_id_type,
    )

def search_app_table_record(
    app_token: str,
    table_id: str,
    *,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    return _search_app_table_record(
        app_token,
        table_id,
        user_id_type=user_id_type,
        api=FeishuAPI(),
    )

def _search_app_table_record(
    app_token: str,
    table_id: str,
    *,
    user_id_type: str | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.bitable.search_app_table_record(
        app_token=app_token,
        table_id=table_id,
        user_id_type=user_id_type,
    )
