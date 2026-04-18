from __future__ import annotations

from typing import Any

from lark_oapi.api.board.v1 import (
    CreatePlantumlWhiteboardNodeRequest,
    CreatePlantumlWhiteboardNodeRequestBody,
    DownloadAsImageWhiteboardRequest,
    ListWhiteboardNodeRequest,
)

from .base import _BaseAPIGroup
from .errors import FeishuResponseError


class FeishuBoardAPI(_BaseAPIGroup):
    def create_plantuml_whiteboard_node(
        self,
        whiteboard_id: str,
        plant_uml_code: str,
        *,
        style_type: int | None = None,
        syntax_type: int | None = None,
        diagram_type: int | None = None,
        overwrite: bool | None = None,
        parse_mode: int | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_body_builder = CreatePlantumlWhiteboardNodeRequestBody.builder().plant_uml_code(
            plant_uml_code
        )

        if style_type is not None:
            request_body_builder = request_body_builder.style_type(style_type)
        if syntax_type is not None:
            request_body_builder = request_body_builder.syntax_type(syntax_type)
        if diagram_type is not None:
            request_body_builder = request_body_builder.diagram_type(diagram_type)
        if overwrite is not None:
            request_body_builder = request_body_builder.overwrite(overwrite)
        if parse_mode is not None:
            request_body_builder = request_body_builder.parse_mode(parse_mode)

        request = (
            CreatePlantumlWhiteboardNodeRequest.builder()
            .whiteboard_id(whiteboard_id)
            .request_body(request_body_builder.build())
            .build()
        )

        response = self._call_with_retry(
            "client.board.v1.whiteboard_node.create_plantuml",
            lambda: self._parent.client.board.v1.whiteboard_node.create_plantuml(
                request,
                option,
            ),
        )
        return self._marshal_data(response.data)

    def list_whiteboard_node(
        self,
        whiteboard_id: str,
        user_id_type: str = "open_id",
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            ListWhiteboardNodeRequest.builder()
            .whiteboard_id(whiteboard_id)
            .user_id_type(user_id_type)
            .build()
        )

        response = self._call_with_retry(
            "client.board.v1.whiteboard_node.list",
            lambda: self._parent.client.board.v1.whiteboard_node.list(request, option),
        )
        return self._marshal_data(response.data)

    def download_as_image_whiteboard(self, whiteboard_id: str) -> bytes:
        option = self._request_option()
        request = (
            DownloadAsImageWhiteboardRequest.builder()
            .whiteboard_id(whiteboard_id)
            .build()
        )

        response = self._call_with_retry(
            "client.board.v1.whiteboard.download_as_image",
            lambda: self._parent.client.board.v1.whiteboard.download_as_image(
                request,
                option,
            ),
        )

        if response.file is None:
            raise FeishuResponseError(
                "client.board.v1.whiteboard.download_as_image failed: file stream missing",
                action="client.board.v1.whiteboard.download_as_image",
            )

        return bytes(response.file.read())
