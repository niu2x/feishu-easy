from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Literal

from ..unified_doc import (
    Block,
    UnifiedDocument,
    unified_to_markdown,
)
from .errors import ServiceError, ServiceValidationError

from ..convert.from_feishu import (
    bitable_to_unified,
    doc_to_unified,
    docx_to_unified,
    sheet_to_unified,
)
from ..feishu_api import FeishuAPI

SourceType = Literal["doc", "docx", "sheet", "bitable"]
TargetType = Literal["unified", "markdown"]
Mode = Literal["online", "offline"]

def convert_from_feishu(
    raw_content: str,
    *,
    source_type: SourceType,
    target_type: TargetType,
    mode: Mode,
    expand_board: bool = False,
    board_node_fetcher: Callable[[str], dict[str, Any]] | None = None,
    expand_sheets: bool = False,
    sheet_block_fetcher: Callable[[str], list[Block]] | None = None,
) -> dict[str, Any] | str:
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ServiceValidationError(f"Input is not valid JSON: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ServiceValidationError("Input JSON must be an object")

    normalized = normalize_payload(payload, source_type=source_type)
    if source_type == "doc":
        result = doc_to_unified(normalized, mode)
    elif source_type == "docx":
        if not normalized["obj"]:
            raise ServiceValidationError(
                "docx blocks are empty, cannot convert to unified"
            )
        result = docx_to_unified(
            normalized,
            mode,
            expand_board=expand_board,
            board_node_fetcher=board_node_fetcher,
            expand_sheets=expand_sheets,
            sheet_block_fetcher=sheet_block_fetcher,
        )
    elif source_type == "sheet":
        result = sheet_to_unified(normalized)
    elif source_type == "bitable":
        result = bitable_to_unified(normalized)
    else:
        raise ServiceValidationError(f"Unsupported source type: {source_type}")

    if target_type == "unified":
        return result.model_dump()
    if target_type == "markdown":
        return unified_to_markdown(result)
    raise ServiceValidationError(f"Unsupported target type: {target_type}")

def get_online_unified_document_by_node_token(
    node_token: str,
    *,
    api: FeishuAPI | None = None,
    expand_board: bool = False,
    expand_sheets: bool = False,
) -> UnifiedDocument:
    feishu_api = api or FeishuAPI()

    source = get_online_wiki_node_source_by_node_token(node_token, api=feishu_api)
    unified_payload = convert_online_wiki_node_source(
        source,
        target_type="unified",
        expand_board=expand_board,
        board_node_fetcher=(
            feishu_api.board.list_whiteboard_node if expand_board else None
        ),
        expand_sheets=expand_sheets,
        sheet_block_fetcher=(
            _build_online_sheet_block_fetcher(api=feishu_api) if expand_sheets else None
        ),
    )
    if not isinstance(unified_payload, dict):
        raise ServiceError("Unexpected conversion result for unified document")
    return UnifiedDocument.model_validate(unified_payload)

def get_online_markdown_raw_by_node_token(
    node_token: str,
    *,
    api: FeishuAPI | None = None,
    expand_board: bool = False,
    expand_sheets: bool = False,
) -> str:
    feishu_api = api or FeishuAPI()

    source = get_online_wiki_node_source_by_node_token(node_token, api=feishu_api)
    markdown = convert_online_wiki_node_source(
        source,
        target_type="markdown",
        expand_board=expand_board,
        board_node_fetcher=(
            feishu_api.board.list_whiteboard_node if expand_board else None
        ),
        expand_sheets=expand_sheets,
        sheet_block_fetcher=(
            _build_online_sheet_block_fetcher(api=feishu_api) if expand_sheets else None
        ),
    )
    if not isinstance(markdown, str):
        raise ServiceError("Unexpected conversion result for markdown")
    return markdown

def get_online_wiki_node_source_by_node_token(
    node_token: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, str]:
    feishu_api = api or FeishuAPI()
    node = feishu_api.wiki.get_node(node_token)

    obj_type = node.get("obj_type")
    if obj_type not in {"doc", "docx", "sheet", "bitable"}:
        raise ServiceValidationError(
            "Only doc/docx/sheet/bitable wiki node is supported"
        )

    obj_token = node.get("obj_token")
    if not isinstance(obj_token, str) or not obj_token:
        raise ServiceValidationError("Invalid node: obj_token is missing")

    if obj_type == "docx":
        raw_payload = feishu_api.docx.list_document_block(
            document_id=obj_token,
            document_revision_id=-1,
        )
        raw_content = raw_payload

        return {
            "payload": json.dumps(
                {
                    "node": node,
                    "obj": raw_content["items"],
                },
                ensure_ascii=False,
            ),
            "obj_type": obj_type,
        }

    elif obj_type == "doc":
        raw_content = json.loads(feishu_api.doc.get_doc_content(obj_token=obj_token))

        return {
            "payload": json.dumps(
                {
                    "node": node,
                    "obj": raw_content,
                },
                ensure_ascii=False,
            ),
            "obj_type": obj_type,
        }

    elif obj_type == "sheet":
        sheets = _list_spreadsheet_sheet_resources_with_online_data(
            obj_token, api=feishu_api
        )
        return _build_online_sheet_source(
            sheets=sheets, node_title=str(node.get("title") or "")
        )

    elif obj_type == "bitable":
        tables = _list_bitable_table_resources(obj_token, api=feishu_api)

        bitable_items: list[dict[str, Any]] = []
        for table in tables:
            table_id = table.get("table_id")
            if not isinstance(table_id, str):
                continue

            bitable_items.append(
                {
                    "app_token": obj_token,
                    "table": table,
                    "data": feishu_api.bitable.search_app_table_record(
                        obj_token,
                        table_id,
                    ).get("items", []),
                    "fields": feishu_api.bitable.list_app_table_field(
                        obj_token, table_id
                    ).get("items", []),
                }
            )

        if not bitable_items:
            raise ServiceError("list_app_table failed: no table resource found")

        return {
            "payload": json.dumps(
                {
                    "node": node,
                    "obj": bitable_items,
                },
                ensure_ascii=False,
            ),
            "obj_type": obj_type,
        }

def get_online_sheet_asset_source_by_token(
    token: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, str]:
    spreadsheet_token, sheet_token = resolve_sheet_asset_tokens(token)
    feishu_api = api or FeishuAPI()

    sheets = _list_spreadsheet_sheet_resources_with_online_data(
        spreadsheet_token,
        api=feishu_api,
        target_sheet_id=sheet_token,
    )
    if not sheets:
        raise ServiceError("query_spreadsheet_sheet failed: sheet resource not found")

    return _build_online_sheet_source(
        sheets=sheets, node_title=str(sheets[0].get("title") or "")
    )

def resolve_sheet_asset_tokens(token: str) -> tuple[str, str]:
    text = token.strip()
    if text:
        parts = text.rsplit("_", maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]

    raise ServiceValidationError(
        "Invalid sheet token, expected token=<spreadsheet_token>_<sheet_token>"
    )

def _list_spreadsheet_sheet_resources_with_online_data(
    spreadsheet_token: str,
    *,
    api: FeishuAPI,
    target_sheet_id: str | None = None,
) -> list[dict[str, Any]]:
    from .sheets_service import get_sheet_content, list_spreadsheet_sheet_resources

    sheets = list_spreadsheet_sheet_resources(spreadsheet_token, api=api)
    if isinstance(target_sheet_id, str):
        sheets = [sheet for sheet in sheets if sheet.get("sheet_id") == target_sheet_id]

    metainfo: dict[str, Any] | None = None

    for sheet in sheets:
        current_sheet_id = sheet.get("sheet_id")
        if not isinstance(current_sheet_id, str):
            continue

        if sheet.get("resource_type") == "sheet":
            sheet["data"] = get_sheet_content(
                spreadsheet_token=spreadsheet_token,
                sheet_id=current_sheet_id,
                api=api,
            )
            continue

        if sheet.get("resource_type") != "bitable":
            continue

        if metainfo is None:
            metainfo_payload = api.sheets.get_spreadsheet_metainfo(spreadsheet_token)
            metainfo = metainfo_payload if isinstance(metainfo_payload, dict) else {}

        meta = _find_sheet_meta_by_sheet_id(metainfo.get("sheets"), current_sheet_id)
        sheet["meta"] = meta
        if not isinstance(meta, dict):
            continue

        block_info = meta.get("blockInfo")
        if not isinstance(block_info, dict):
            continue
        if block_info.get("blockType") != "BITABLE_BLOCK":
            continue

        block_token = block_info.get("blockToken")
        if not isinstance(block_token, str) or "_" not in block_token:
            continue

        app_token, table_id = block_token.split("_", maxsplit=1)
        sheet["data"] = api.bitable.search_app_table_record(app_token, table_id).get(
            "items", []
        )
        sheet["fields"] = api.bitable.list_app_table_field(app_token, table_id).get(
            "items", []
        )

    return sheets

def _build_online_sheet_source(
    *, sheets: list[dict[str, Any]], node_title: str
) -> dict[str, str]:
    payload = {
        "node": {
            "title": node_title,
        },
        "obj": sheets,
    }
    return {
        "payload": json.dumps(payload, ensure_ascii=False),
        "obj_type": "sheet",
    }

def _find_sheet_meta_by_sheet_id(
    raw_sheets_meta: Any,
    sheet_id: str,
) -> dict[str, Any] | None:
    if not isinstance(raw_sheets_meta, list):
        return None

    for item in raw_sheets_meta:
        if not isinstance(item, dict):
            continue
        if item.get("sheetId") == sheet_id:
            return item
    return None

def _list_bitable_table_resources(
    app_token: str,
    *,
    api: FeishuAPI,
) -> list[dict[str, Any]]:
    payload = api.bitable.list_app_table(app_token=app_token)
    tables = payload.get("items")
    if not isinstance(tables, list):
        raise ServiceError("list_app_table failed: missing items")
    return [table for table in tables]

def _build_online_sheet_block_fetcher(
    *,
    api: FeishuAPI,
) -> Callable[[str], list[Block]]:
    def fetch_sheet_blocks(token: str) -> list[Block]:
        source = get_online_sheet_asset_source_by_token(token, api=api)
        unified_payload = convert_online_wiki_node_source(
            source,
            target_type="unified",
        )
        if not isinstance(unified_payload, dict):
            raise ServiceError("Unexpected conversion result for sheet asset")
        return UnifiedDocument.model_validate(unified_payload).blocks

    return fetch_sheet_blocks

def convert_online_wiki_node_source(
    source: dict[str, str],
    *,
    target_type: TargetType,
    expand_board: bool = False,
    board_node_fetcher: Callable[[str], dict[str, Any]] | None = None,
    expand_sheets: bool = False,
    sheet_block_fetcher: Callable[[str], list[Block]] | None = None,
) -> dict[str, Any] | str:
    return convert_from_feishu(
        source["payload"],
        source_type=source["obj_type"],
        target_type=target_type,
        mode="online",
        expand_board=expand_board,
        board_node_fetcher=board_node_fetcher,
        expand_sheets=expand_sheets,
        sheet_block_fetcher=sheet_block_fetcher,
    )

def normalize_payload(
    payload: dict[str, Any], *, source_type: SourceType
) -> dict[str, Any]:
    if source_type == "doc":
        return _normalize_doc_payload(payload)
    if source_type == "docx":
        return _normalize_docx_payload(payload)
    if source_type == "sheet":
        return _normalize_sheet_payload(payload)
    if source_type == "bitable":
        return _normalize_bitable_payload(payload)
    raise ServiceValidationError(f"Unsupported source type: {source_type}")

def _normalize_doc_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("node"), dict) and payload.get("obj") is not None:
        return payload

    raise ServiceValidationError("Unsupported doc payload")

def _normalize_docx_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("node"), dict) and isinstance(payload.get("obj"), list):
        return payload

    raise ServiceValidationError("Unsupported docx payload")

def _normalize_sheet_payload(payload: dict[str, Any]) -> dict[str, Any]:
    node = payload.get("node")
    obj = payload.get("obj")
    if isinstance(node, dict) and isinstance(obj, list):
        return payload

    raise ServiceValidationError(
        "Unsupported sheet payload: expected {'node': {...}, 'obj': [...]} "
    )

def _normalize_bitable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    node = payload.get("node")
    obj = payload.get("obj")
    if not isinstance(node, dict) or not isinstance(obj, list):
        raise ServiceValidationError("Unsupported bitable payload")

    normalized_items: list[dict[str, Any]] = []
    for item in obj:
        if not isinstance(item, dict):
            continue

        app_token = item.get("app_token")
        table = item.get("table")
        data = item.get("data")
        fields = item.get("fields")
        if not isinstance(app_token, str):
            continue
        if not isinstance(table, dict):
            continue
        if not isinstance(data, list):
            continue
        if not isinstance(fields, list):
            continue

        normalized_items.append(
            {
                "app_token": app_token,
                "table": table,
                "data": data,
                "fields": fields,
            }
        )

    if not normalized_items:
        raise ServiceValidationError("Unsupported bitable payload")

    return {
        "node": node,
        "obj": normalized_items,
    }
