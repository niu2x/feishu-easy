from __future__ import annotations

from typing import Any

from lark_oapi.api.board.v1 import (
    DownloadAsImageWhiteboardRequest,
    ListWhiteboardNodeRequest,
)

from .base import _BaseAPIGroup

class FeishuBoardAPI(_BaseAPIGroup):
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
            raise RuntimeError(
                "client.board.v1.whiteboard.download_as_image failed: file stream missing"
            )

        return bytes(response.file.read())
