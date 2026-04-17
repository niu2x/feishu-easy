from __future__ import annotations

from typing import Any

from lark_oapi.api.bitable.v1 import (
    GetAppRequest,
    ListAppTableFieldRequest,
    ListAppTableRequest,
    GetAppTableViewRequest,
    ListAppTableViewRequest,
    SearchAppTableRecordRequest,
    SearchAppTableRecordRequestBody,
)

from .base import _BaseAPIGroup


class FeishuBitableAPI(_BaseAPIGroup):
    def get_app(
        self,
        app_token: str,
        *,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_builder = GetAppRequest.builder().app_token(app_token)
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app.get",
            lambda: self._parent.client.bitable.v1.app.get(request, option),
        )
        return self._marshal_data(response.data)

    def list_app_table(self, app_token: str) -> dict[str, Any]:
        option = self._request_option()
        effective_page_size = 500

        def _build_request(next_page_token: str | None) -> ListAppTableRequest:
            request_builder = (
                ListAppTableRequest.builder()
                .app_token(app_token)
                .page_size(effective_page_size)
            )
            if next_page_token:
                request_builder = request_builder.page_token(next_page_token)
            return request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app_table.list",
            lambda: self._parent.client.bitable.v1.app_table.list(
                _build_request(None),
                option,
            ),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not isinstance(next_page_token, str) or not next_page_token:
                break

            response = self._call_with_retry(
                "client.bitable.v1.app_table.list",
                lambda: self._parent.client.bitable.v1.app_table.list(
                    _build_request(next_page_token),
                    option,
                ),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result

    def list_app_table_field(
        self,
        app_token: str,
        table_id: str,
        *,
        view_id: str | None = None,
        text_field_as_array: bool | None = None,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        effective_page_size = 500

        def _build_request(next_page_token: str | None) -> ListAppTableFieldRequest:
            request_builder = (
                ListAppTableFieldRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .page_size(effective_page_size)
            )
            if view_id:
                request_builder = request_builder.view_id(view_id)
            if text_field_as_array is not None:
                request_builder = request_builder.text_field_as_array(
                    text_field_as_array
                )
            if next_page_token:
                request_builder = request_builder.page_token(next_page_token)
            if user_id_type:
                request_builder = request_builder.user_id_type(user_id_type)
            return request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app_table_field.list",
            lambda: self._parent.client.bitable.v1.app_table_field.list(
                _build_request(None),
                option,
            ),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not isinstance(next_page_token, str) or not next_page_token:
                break

            response = self._call_with_retry(
                "client.bitable.v1.app_table_field.list",
                lambda: self._parent.client.bitable.v1.app_table_field.list(
                    _build_request(next_page_token),
                    option,
                ),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result

    def list_app_table_view(
        self,
        app_token: str,
        table_id: str,
        *,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        effective_page_size = 500

        def _build_request(next_page_token: str | None) -> ListAppTableViewRequest:
            request_builder = (
                ListAppTableViewRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .page_size(effective_page_size)
            )
            if next_page_token:
                request_builder = request_builder.page_token(next_page_token)
            if user_id_type:
                request_builder = request_builder.user_id_type(user_id_type)
            return request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app_table_view.list",
            lambda: self._parent.client.bitable.v1.app_table_view.list(
                _build_request(None),
                option,
            ),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not isinstance(next_page_token, str) or not next_page_token:
                break

            response = self._call_with_retry(
                "client.bitable.v1.app_table_view.list",
                lambda: self._parent.client.bitable.v1.app_table_view.list(
                    _build_request(next_page_token),
                    option,
                ),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result

    def get_app_table_view(
        self,
        app_token: str,
        table_id: str,
        view_id: str,
        *,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_builder = (
            GetAppTableViewRequest.builder()
            .app_token(app_token)
            .table_id(table_id)
            .view_id(view_id)
        )
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app_table_view.get",
            lambda: self._parent.client.bitable.v1.app_table_view.get(request, option),
        )
        return self._marshal_data(response.data)

    def search_app_table_record(
        self,
        app_token: str,
        table_id: str,
        *,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        effective_page_size = 500

        def _build_request(next_page_token: str | None) -> SearchAppTableRecordRequest:
            request_builder = (
                SearchAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .page_size(effective_page_size)
                .request_body(
                    SearchAppTableRecordRequestBody.builder()
                    .automatic_fields(False)
                    .build()
                )
            )
            if next_page_token:
                request_builder = request_builder.page_token(next_page_token)
            if user_id_type:
                request_builder = request_builder.user_id_type(user_id_type)
            return request_builder.build()

        response = self._call_with_retry(
            "client.bitable.v1.app_table_record.search",
            lambda: self._parent.client.bitable.v1.app_table_record.search(
                _build_request(None),
                option,
            ),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not isinstance(next_page_token, str) or not next_page_token:
                break

            response = self._call_with_retry(
                "client.bitable.v1.app_table_record.search",
                lambda: self._parent.client.bitable.v1.app_table_record.search(
                    _build_request(next_page_token),
                    option,
                ),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result
