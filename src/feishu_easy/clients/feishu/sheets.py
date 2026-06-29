from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests
from lark_oapi.api.sheets.v3 import (
    CreateSpreadsheetRequest,
    GetSpreadsheetSheetFloatImageRequest,
    GetSpreadsheetSheetRequest,
    GetSpreadsheetRequest,
    QuerySpreadsheetSheetFloatImageRequest,
    QuerySpreadsheetSheetRequest,
    Spreadsheet,
)

from .base import _BaseAPIGroup, _FeishuAPIResponse
from .errors import FeishuAuthError, FeishuHTTPError, FeishuResponseError

class FeishuSheetsAPI(_BaseAPIGroup):
    def get_spreadsheet_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetSpreadsheetSheetRequest.builder()
            .spreadsheet_token(spreadsheet_token)
            .sheet_id(sheet_id)
            .build()
        )

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet_sheet.get",
            lambda: self._parent.client.sheets.v3.spreadsheet_sheet.get(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def query_spreadsheet_sheet(self, spreadsheet_token: str) -> dict[str, Any]:
        option = self._request_option()
        request = (
            QuerySpreadsheetSheetRequest.builder()
            .spreadsheet_token(spreadsheet_token)
            .build()
        )

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet_sheet.query",
            lambda: self._parent.client.sheets.v3.spreadsheet_sheet.query(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def get_spreadsheet(
        self,
        spreadsheet_token: str,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_builder = GetSpreadsheetRequest.builder().spreadsheet_token(
            spreadsheet_token
        )
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet.get",
            lambda: self._parent.client.sheets.v3.spreadsheet.get(request, option),
        )
        return self._marshal_data(response.data)

    def get_spreadsheet_metainfo(
        self,
        spreadsheet_token: str,
        *,
        ext_fields: str | None = None,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        access_token = self._parent.get_access_token()
        if not isinstance(access_token, str) or not access_token:
            raise FeishuAuthError(
                "open-apis.sheets.v2.spreadsheets.metainfo.get failed: access_token missing",
                action="open-apis.sheets.v2.spreadsheets.metainfo.get",
            )

        query_params: dict[str, str] = {}
        if ext_fields is not None:
            query_params["extFields"] = ext_fields
        if user_id_type is not None:
            query_params["user_id_type"] = user_id_type

        encoded_spreadsheet_token = quote(spreadsheet_token, safe="")
        url = (
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
            f"{encoded_spreadsheet_token}/metainfo"
        )

        def _call() -> _FeishuAPIResponse:
            try:
                response = requests.get(
                    url,
                    params=query_params or None,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30,
                )
            except requests.Timeout as exc:
                raise TimeoutError(
                    "open-apis.sheets.v2.spreadsheets.metainfo.get timeout"
                ) from exc
            except requests.ConnectionError as exc:
                raise ConnectionError(
                    "open-apis.sheets.v2.spreadsheets.metainfo.get connection error"
                ) from exc
            except requests.RequestException as exc:
                raise FeishuHTTPError(
                    f"open-apis.sheets.v2.spreadsheets.metainfo.get failed: {exc}",
                    action="open-apis.sheets.v2.spreadsheets.metainfo.get",
                ) from exc

            try:
                payload = response.json()
            except ValueError as exc:
                raise FeishuHTTPError(
                    "open-apis.sheets.v2.spreadsheets.metainfo.get failed: invalid json response",
                    action="open-apis.sheets.v2.spreadsheets.metainfo.get",
                ) from exc

            if not isinstance(payload, dict):
                raise FeishuHTTPError(
                    "open-apis.sheets.v2.spreadsheets.metainfo.get failed: invalid json payload",
                    action="open-apis.sheets.v2.spreadsheets.metainfo.get",
                )

            return _FeishuAPIResponse(payload)

        wrapped_response = self._call_with_retry(
            "open-apis.sheets.v2.spreadsheets.metainfo.get",
            _call,
        )
        if not isinstance(wrapped_response.data, dict):
            raise FeishuResponseError(
                "open-apis.sheets.v2.spreadsheets.metainfo.get failed: data missing",
                action="open-apis.sheets.v2.spreadsheets.metainfo.get",
            )

        return wrapped_response.data

    def get_spreadsheet_sheet_float_image(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        float_image_id: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetSpreadsheetSheetFloatImageRequest.builder()
            .spreadsheet_token(spreadsheet_token)
            .sheet_id(sheet_id)
            .float_image_id(float_image_id)
            .build()
        )

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet_sheet_float_image.get",
            lambda: self._parent.client.sheets.v3.spreadsheet_sheet_float_image.get(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def query_spreadsheet_sheet_float_images(
        self,
        spreadsheet_token: str,
        sheet_id: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            QuerySpreadsheetSheetFloatImageRequest.builder()
            .spreadsheet_token(spreadsheet_token)
            .sheet_id(sheet_id)
            .build()
        )

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet_sheet_float_image.query",
            lambda: self._parent.client.sheets.v3.spreadsheet_sheet_float_image.query(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def create_spreadsheet(
        self,
        title: str,
        folder_token: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        spreadsheet_builder = Spreadsheet.builder().title(title)
        if folder_token:
            spreadsheet_builder = spreadsheet_builder.folder_token(folder_token)

        request = (
            CreateSpreadsheetRequest.builder()
            .request_body(spreadsheet_builder.build())
            .build()
        )

        response = self._call_with_retry(
            "client.sheets.v3.spreadsheet.create",
            lambda: self._parent.client.sheets.v3.spreadsheet.create(request, option),
        )
        return self._marshal_data(response.data)

    def get_sheet_values(
        self,
        spreadsheet_token: str,
        value_range: str,
        value_render_option: str | None = None,
        date_time_render_option: str | None = None,
    ) -> dict[str, Any]:
        access_token = self._parent.get_access_token()
        if not isinstance(access_token, str) or not access_token:
            raise FeishuAuthError(
                "open-apis.sheets.v2.spreadsheets.values.get failed: access_token missing",
                action="open-apis.sheets.v2.spreadsheets.values.get",
            )

        query_params: dict[str, str] = {}
        if value_render_option is not None:
            query_params["valueRenderOption"] = value_render_option
        if date_time_render_option is not None:
            query_params["dateTimeRenderOption"] = date_time_render_option

        encoded_range = quote(value_range, safe="!:")
        url = (
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
            f"{spreadsheet_token}/values/{encoded_range}"
        )

        def _call() -> _FeishuAPIResponse:
            try:
                response = requests.get(
                    url,
                    params=query_params or None,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30,
                )
            except requests.Timeout as exc:
                raise TimeoutError(
                    "open-apis.sheets.v2.spreadsheets.values.get timeout"
                ) from exc
            except requests.ConnectionError as exc:
                raise ConnectionError(
                    "open-apis.sheets.v2.spreadsheets.values.get connection error"
                ) from exc
            except requests.RequestException as exc:
                raise FeishuHTTPError(
                    f"open-apis.sheets.v2.spreadsheets.values.get failed: {exc}",
                    action="open-apis.sheets.v2.spreadsheets.values.get",
                ) from exc

            try:
                payload = response.json()
            except ValueError as exc:
                raise FeishuHTTPError(
                    "open-apis.sheets.v2.spreadsheets.values.get failed: invalid json response",
                    action="open-apis.sheets.v2.spreadsheets.values.get",
                ) from exc

            if not isinstance(payload, dict):
                raise FeishuHTTPError(
                    "open-apis.sheets.v2.spreadsheets.values.get failed: invalid json payload",
                    action="open-apis.sheets.v2.spreadsheets.values.get",
                )

            return _FeishuAPIResponse(payload)

        wrapped_response = self._call_with_retry(
            "open-apis.sheets.v2.spreadsheets.values.get",
            _call,
        )
        if not isinstance(wrapped_response.data, dict):
            raise FeishuResponseError(
                "open-apis.sheets.v2.spreadsheets.values.get failed: data missing",
                action="open-apis.sheets.v2.spreadsheets.values.get",
            )

        return wrapped_response.data
