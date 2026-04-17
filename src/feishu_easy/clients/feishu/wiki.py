from __future__ import annotations

from typing import Any

from lark_oapi.api.wiki.v2 import (
    CreateSpaceNodeRequest,
    GetNodeSpaceRequest,
    GetSpaceRequest,
    ListSpaceMemberRequest,
    ListSpaceNodeRequest,
    ListSpaceRequest,
    MoveSpaceNodeRequest,
    MoveSpaceNodeRequestBody,
    Node,
    UpdateTitleSpaceNodeRequest,
    UpdateTitleSpaceNodeRequestBody,
)

from .base import _BaseAPIGroup
from .constants import (
    WIKI_LIST_SPACE_MEMBER_PAGE_SIZE,
    WIKI_LIST_SPACE_NODE_PAGE_SIZE,
    WIKI_LIST_SPACE_PAGE_SIZE,
)


class FeishuWikiAPI(_BaseAPIGroup):
    def move_space_node(
        self,
        node_token: str,
        space_id: int,
        target_parent_token: str,
        target_space_id: int | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_body_builder = MoveSpaceNodeRequestBody.builder().target_parent_token(
            target_parent_token
        )
        if target_space_id is not None:
            request_body_builder = request_body_builder.target_space_id(
                str(target_space_id)
            )

        request = (
            MoveSpaceNodeRequest.builder()
            .space_id(str(space_id))
            .node_token(node_token)
            .request_body(request_body_builder.build())
            .build()
        )

        response = self._call_with_retry(
            "client.wiki.v2.space_node.move",
            lambda: self._parent.client.wiki.v2.space_node.move(request, option),
        )
        return self._marshal_data(response.data)

    def create_space_node(
        self,
        space_id: int,
        obj_type: str,
        parent_node_token: str,
        node_type: str,
        origin_node_token: str,
        title: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            CreateSpaceNodeRequest.builder()
            .space_id(str(space_id))
            .request_body(
                Node.builder()
                .obj_type(obj_type)
                .parent_node_token(parent_node_token)
                .node_type(node_type)
                .origin_node_token(origin_node_token)
                .title(title)
                .build()
            )
            .build()
        )

        response = self._call_with_retry(
            "client.wiki.v2.space_node.create",
            lambda: self._parent.client.wiki.v2.space_node.create(request, option),
        )
        return self._marshal_data(response.data)

    def list_space_member(
        self,
        space_id: int,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            ListSpaceMemberRequest.builder()
            .space_id(str(space_id))
            .page_size(WIKI_LIST_SPACE_MEMBER_PAGE_SIZE)
            .build()
        )

        response = self._call_with_retry(
            "client.wiki.v2.space_member.list",
            lambda: self._parent.client.wiki.v2.space_member.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            request = (
                ListSpaceMemberRequest.builder()
                .space_id(str(space_id))
                .page_size(WIKI_LIST_SPACE_MEMBER_PAGE_SIZE)
                .page_token(result["page_token"])
                .build()
            )

            response = self._call_with_retry(
                "client.wiki.v2.space_member.list",
                lambda: self._parent.client.wiki.v2.space_member.list(request, option),
            )

            new_result = self._marshal_data(response.data)
            new_result["items"] = result["items"] + new_result["items"]
            result = new_result

        return result

    def list_space_node(
        self,
        space_id: int,
        parent_node_token: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_builder = (
            ListSpaceNodeRequest.builder()
            .space_id(str(space_id))
            .page_size(WIKI_LIST_SPACE_NODE_PAGE_SIZE)
        )
        if parent_node_token:
            request_builder = request_builder.parent_node_token(parent_node_token)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.wiki.v2.space_node.list",
            lambda: self._parent.client.wiki.v2.space_node.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            request_builder = (
                ListSpaceNodeRequest.builder()
                .space_id(str(space_id))
                .page_size(WIKI_LIST_SPACE_NODE_PAGE_SIZE)
                .page_token(result["page_token"])
            )
            if parent_node_token:
                request_builder = request_builder.parent_node_token(parent_node_token)
            request = request_builder.build()

            response = self._call_with_retry(
                "client.wiki.v2.space_node.list",
                lambda: self._parent.client.wiki.v2.space_node.list(request, option),
            )

            new_result = self._marshal_data(response.data)
            new_result["items"] = result["items"] + new_result["items"]
            result = new_result

        return result

    def get_space(self, space_id: int, lang: str = "zh") -> dict[str, Any]:
        option = self._request_option()
        request = GetSpaceRequest.builder().space_id(str(space_id)).lang(lang).build()

        response = self._call_with_retry(
            "client.wiki.v2.space.get",
            lambda: self._parent.client.wiki.v2.space.get(request, option),
        )
        return self._marshal_data(response.data)

    def get_node(self, node_token: str) -> dict[str, Any]:
        option = self._request_option()
        request: GetNodeSpaceRequest = (
            GetNodeSpaceRequest.builder().obj_type("wiki").token(node_token).build()
        )

        response = self._call_with_retry(
            "client.wiki.v2.space.get_node",
            lambda: self._parent.client.wiki.v2.space.get_node(request, option),
        )
        return self._marshal_data(response.data)["node"]

    def update_node_title(self, node_token: str, title: str) -> None:
        option = self._request_option()
        request = (
            UpdateTitleSpaceNodeRequest.builder()
            .node_token(node_token)
            .request_body(
                UpdateTitleSpaceNodeRequestBody.builder().title(title).build()
            )
            .build()
        )

        self._call_with_retry(
            "client.wiki.v2.space_node.update_title",
            lambda: self._parent.client.wiki.v2.space_node.update_title(
                request, option
            ),
        )

    def list_space(self) -> dict[str, Any]:
        option = self._request_option()
        request = (
            ListSpaceRequest.builder().page_size(WIKI_LIST_SPACE_PAGE_SIZE).build()
        )

        response = self._call_with_retry(
            "client.wiki.v2.space.list",
            lambda: self._parent.client.wiki.v2.space.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            request = (
                ListSpaceRequest.builder()
                .page_size(WIKI_LIST_SPACE_PAGE_SIZE)
                .page_token(result["page_token"])
                .build()
            )

            response = self._call_with_retry(
                "client.wiki.v2.space.list",
                lambda: self._parent.client.wiki.v2.space.list(request, option),
            )

            new_result = self._marshal_data(response.data)
            new_result["items"] = result["items"] + new_result["items"]
            result = new_result

        return result
