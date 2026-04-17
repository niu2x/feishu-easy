from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI

def get_wiki_space_node(node_token: str) -> dict:
    api = FeishuAPI()
    return api.wiki.get_node(node_token)

def get_wiki_space(space_id: int, lang: str = "zh") -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.get_space(space_id=space_id, lang=lang)

def create_wiki_space_node(
    space_id: int,
    obj_type: str,
    parent_node_token: str,
    node_type: str,
    origin_node_token: str,
    title: str,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.create_space_node(
        space_id=space_id,
        obj_type=obj_type,
        parent_node_token=parent_node_token,
        node_type=node_type,
        origin_node_token=origin_node_token,
        title=title,
    )

def update_wiki_node_title(node_token: str, title: str) -> None:
    api = FeishuAPI()
    api.wiki.update_node_title(node_token=node_token, title=title)

def move_wiki_space_node(
    node_token: str,
    space_id: int,
    target_parent_token: str,
    target_space_id: int | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.move_space_node(
        node_token=node_token,
        space_id=space_id,
        target_parent_token=target_parent_token,
        target_space_id=target_space_id,
    )

def list_wiki_space() -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.list_space()

def list_wiki_space_member(space_id: int) -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.list_space_member(space_id=space_id)

def list_wiki_space_node(
    space_id: int,
    parent_node_token: str | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.wiki.list_space_node(
        space_id=space_id,
        parent_node_token=parent_node_token,
    )
