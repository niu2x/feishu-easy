from __future__ import annotations

from typing import Any

from ..feishu_api import FeishuAPI

def get_spreadsheet_sheet(
    spreadsheet_token: str,
    sheet_id: str,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.get_spreadsheet_sheet(
        spreadsheet_token=spreadsheet_token,
        sheet_id=sheet_id,
    )

def query_spreadsheet_sheet(spreadsheet_token: str) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.query_spreadsheet_sheet(spreadsheet_token=spreadsheet_token)

def get_spreadsheet(
    spreadsheet_token: str,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.get_spreadsheet(
        spreadsheet_token=spreadsheet_token,
        user_id_type=user_id_type,
    )

def get_spreadsheet_metainfo(
    spreadsheet_token: str,
    ext_fields: str | None = None,
    user_id_type: str | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.get_spreadsheet_metainfo(
        spreadsheet_token=spreadsheet_token,
        ext_fields=ext_fields,
        user_id_type=user_id_type,
    )

def create_spreadsheet(
    title: str,
    folder_token: str | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.create_spreadsheet(title=title, folder_token=folder_token)

def get_sheet_values(
    spreadsheet_token: str,
    value_range: str,
    value_render_option: str | None = None,
    date_time_render_option: str | None = None,
) -> dict[str, Any]:
    api = FeishuAPI()
    return api.sheets.get_sheet_values(
        spreadsheet_token=spreadsheet_token,
        value_range=value_range,
        value_render_option=value_render_option,
        date_time_render_option=date_time_render_option,
    )

def _num_to_col(num: int) -> str:
    if num <= 0:
        raise ValueError("column count must be positive")

    result = ""
    while num > 0:
        num -= 1
        result = chr(ord("A") + num % 26) + result
        num //= 26
    return result

def get_sheet_content(
    spreadsheet_token: str,
    sheet_id: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    sheet_payload = feishu_api.sheets.get_spreadsheet_sheet(
        spreadsheet_token=spreadsheet_token,
        sheet_id=sheet_id,
    )

    sheet = sheet_payload.get("sheet")
    if not isinstance(sheet, dict):
        raise RuntimeError("get_spreadsheet_sheet failed: missing sheet data")

    if sheet.get("resource_type") != "sheet":
        raise RuntimeError("get_spreadsheet_sheet failed: resource_type is not sheet")

    grid_properties = sheet.get("grid_properties")
    if not isinstance(grid_properties, dict):
        raise RuntimeError("get_spreadsheet_sheet failed: missing grid_properties")

    row_count = grid_properties.get("row_count")
    column_count = grid_properties.get("column_count")
    if (
        not isinstance(row_count, int)
        or row_count <= 0
        or not isinstance(column_count, int)
        or column_count <= 0
    ):
        raise RuntimeError(
            "get_spreadsheet_sheet failed: invalid row_count or column_count"
        )

    value_range = f"{sheet_id}!A1:{_num_to_col(column_count)}{row_count}"
    return feishu_api.sheets.get_sheet_values(
        spreadsheet_token=spreadsheet_token,
        value_range=value_range,
    )

def list_spreadsheet_sheet_resources(
    spreadsheet_token: str,
    *,
    api: FeishuAPI | None = None,
) -> list[dict[str, Any]]:
    feishu_api = api or FeishuAPI()
    spreadsheet_data = feishu_api.sheets.query_spreadsheet_sheet(
        spreadsheet_token=spreadsheet_token,
    )

    sheets = spreadsheet_data.get("sheets")
    if not isinstance(sheets, list):
        raise RuntimeError("query_spreadsheet_sheet failed: missing sheets")

    return [
        sheet
        for sheet in sheets
        if isinstance(sheet, dict)
        and (
            sheet.get("resource_type") == "sheet"
            or sheet.get("resource_type") == "bitable"
        )
        and isinstance(sheet.get("sheet_id"), str)
        and bool(str(sheet.get("sheet_id") or "").strip())
    ]
