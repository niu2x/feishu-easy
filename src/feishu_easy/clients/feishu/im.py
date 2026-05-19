from __future__ import annotations

from typing import Any

from lark_oapi.api.im.v1 import GetChatRequest, ListMessageRequest

from .base import _BaseAPIGroup

class FeishuImAPI(_BaseAPIGroup):
    def get_chat(
        self,
        chat_id: str,
        user_id_type: str = "open_id",
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetChatRequest.builder()
            .chat_id(chat_id)
            .user_id_type(user_id_type)
            .build()
        )
        response = self._call_with_retry(
            "client.im.v1.chat.get",
            lambda: self._parent.client.im.v1.chat.get(request, option),
        )
        return self._marshal_data(response.data)

    def list_message(
        self,
        container_id_type: str,
        container_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        sort_type: str | None = None,
        page_size: int = 50,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        builder = (
            ListMessageRequest.builder()
            .container_id_type(container_id_type)
            .container_id(container_id)
            .page_size(page_size)
        )
        if start_time is not None:
            builder = builder.start_time(start_time)
        if end_time is not None:
            builder = builder.end_time(end_time)
        if sort_type is not None:
            builder = builder.sort_type(sort_type)
        if page_token is not None:
            builder = builder.page_token(page_token)

        request = builder.build()
        response = self._call_with_retry(
            "client.im.v1.message.list",
            lambda: self._parent.client.im.v1.message.list(request, option),
        )
        return self._marshal_data(response.data)

    def list_all_messages(
        self,
        container_id_type: str,
        container_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        sort_type: str | None = None,
        page_size: int = 50,
        limit: int | None = None,
    ) -> dict[str, Any]:
        result = self.list_message(
            container_id_type=container_id_type,
            container_id=container_id,
            start_time=start_time,
            end_time=end_time,
            sort_type=sort_type,
            page_size=page_size,
        )

        items = result.get("items", [])
        if limit is not None and len(items) >= limit:
            result["items"] = items[:limit]
            result["has_more"] = True
            return result

        while result.get("has_more"):
            next_result = self.list_message(
                container_id_type=container_id_type,
                container_id=container_id,
                start_time=start_time,
                end_time=end_time,
                sort_type=sort_type,
                page_size=page_size,
                page_token=result["page_token"],
            )
            items = items + next_result.get("items", [])
            if limit is not None and len(items) >= limit:
                result["items"] = items[:limit]
                result["has_more"] = True
                return result
            next_result["items"] = items
            result = next_result

        return result
