from __future__ import annotations

from datetime import datetime
from typing import Any

from ...unified_doc import (
    Block,
    BlockType,
    DocumentMeta,
    InlineText,
    Mark,
    MarkType,
    UnifiedDocument,
)

from .normalizer import normalize_title

def bitable_to_unified(param: dict[str, Any]) -> UnifiedDocument:
    blocks: list[Block] = []

    for raw in param["obj"]:
        blocks.extend(bitable_page_to_blocks(raw))

    node = param.get("node") if isinstance(param, dict) else None
    title_value = node.get("title") if isinstance(node, dict) else None
    return UnifiedDocument(
        blocks=blocks,
        title=normalize_title(title_value),
        source_type="feishu:bitable",
        meta=DocumentMeta(extra={}),
    )

def bitable_page_to_blocks(raw: dict[str, Any]) -> list[Block]:
    payload = raw.get("data")
    raw_fields = raw.get("fields")

    if payload is None:
        raise ValueError("bitable_to_unified requires raw['obj'][*]['data']")
    if not isinstance(raw_fields, list):
        raise ValueError("bitable_to_unified requires raw['obj'][*]['fields']")

    page_blocks: list[Block] = []
    title = raw.get("title") if isinstance(raw, dict) else None
    if not (isinstance(title, str) and title.strip()):
        title = raw.get("table", {}).get("name")
    if isinstance(title, str) and title.strip():
        page_blocks.append(
            Block(
                type=BlockType.Heading,
                attrs={"level": 2},
                inlines=[InlineText(text=title.strip(), marks=[])],
            )
        )

    field_defs = _build_field_definitions(raw_fields)
    row_size = len(payload) + 1
    headers = [item["field_name"] for item in field_defs]
    col_size = len(headers)

    table_cells: list[Block] = []

    for header in headers:
        table_cells.append(
            Block(
                type=BlockType.Paragraph,
                inlines=[InlineText(text=header.strip(), marks=[])],
            )
        )

    for row in payload:
        row_fields = row.get("fields")
        if not isinstance(row_fields, dict):
            raise ValueError(
                "Unsupported bitable record: expected record.fields object"
            )

        for definition in field_defs:
            header = definition["field_name"]
            if header in row_fields:
                table_cells.append(
                    _bitable_value_to_cell_block(
                        row_fields.get(header),
                        field_type=definition["type"],
                        ui_type=definition["ui_type"],
                        field_name=header,
                    )
                )
            else:
                table_cells.append(_empty_table_cell())

    page_blocks.append(
        Block(
            type=BlockType.Table,
            attrs={
                "row_size": row_size,
                "column_size": col_size,
            },
            inlines=[],
            children=table_cells,
        )
    )

    return page_blocks

def _empty_table_cell() -> Block:
    return Block(type=BlockType.Paragraph, inlines=[InlineText(text="", marks=[])])

def _build_field_definitions(raw_fields: list[Any]) -> list[dict[str, Any]]:
    field_defs: list[dict[str, Any]] = []
    for item in raw_fields:
        if not isinstance(item, dict):
            continue

        field_name = item.get("field_name")
        field_type = item.get("type")
        ui_type = item.get("ui_type")

        if not isinstance(field_name, str) or not field_name:
            continue
        if not isinstance(field_type, int):
            continue
        if not isinstance(ui_type, str) or not ui_type:
            continue

        field_defs.append(
            {
                "field_name": field_name,
                "type": field_type,
                "ui_type": ui_type,
            }
        )

    if not field_defs:
        raise ValueError(
            "Unsupported bitable fields metadata: no valid field definitions"
        )

    return field_defs

def _bitable_value_to_cell_block(
    value: Any,
    *,
    field_type: int,
    ui_type: str,
    field_name: str,
) -> Block:
    if field_type == 17 and ui_type == "Attachment":
        if value is None:
            return _empty_table_cell()
        if not isinstance(value, list):
            _raise_value_type_error(
                field_name, field_type, ui_type, "list[attachment]", value
            )

        children: list[Block] = []
        for item in value:
            if not isinstance(item, dict):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "attachment object", item
                )

            url = item.get("url")
            if not isinstance(url, str) or not url:
                _raise_value_type_error(
                    field_name, field_type, ui_type, "attachment.url=str", item
                )

            name = item.get("name")
            if not isinstance(name, str) or not name:
                _raise_value_type_error(
                    field_name, field_type, ui_type, "attachment.name=str", item
                )

            children.append(
                Block(
                    type=BlockType.Paragraph,
                    inlines=[
                        InlineText(
                            text=name,
                            marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                        )
                    ],
                )
            )

        if not children:
            return _empty_table_cell()

        return Block(type=BlockType.Passthrough, inlines=[], children=children)

    lines = _bitable_value_to_lines(
        value,
        field_type=field_type,
        ui_type=ui_type,
        field_name=field_name,
    )

    if not lines:
        return _empty_table_cell()

    return Block(
        type=BlockType.Passthrough,
        inlines=[],
        children=[
            Block(type=BlockType.Paragraph, inlines=[InlineText(text=line, marks=[])])
            for line in lines
        ],
    )

def _bitable_value_to_lines(
    value: Any,
    *,
    field_type: int,
    ui_type: str,
    field_name: str,
) -> list[str]:
    if value is None:
        return []

    if field_type == 3:
        if isinstance(value, str):
            return [value]
        _raise_value_type_error(field_name, field_type, ui_type, "string", value)

    if field_type == 2 and ui_type == "Number":
        if isinstance(value, int | float) and not isinstance(value, bool):
            return [str(value)]
        _raise_value_type_error(field_name, field_type, ui_type, "number", value)

    if field_type == 5 and ui_type == "DateTime":
        if isinstance(value, int | float) and not isinstance(value, bool):
            return [_format_unix_timestamp_millis_local(value)]
        _raise_value_type_error(
            field_name, field_type, ui_type, "number(timestamp millis)", value
        )

    if field_type == 1005 and ui_type == "AutoNumber":
        if isinstance(value, str):
            return [value]
        _raise_value_type_error(field_name, field_type, ui_type, "string", value)

    if field_type == 1001 and ui_type == "CreatedTime":
        if isinstance(value, int | float):
            return [_format_unix_timestamp_millis_local(value)]
        _raise_value_type_error(
            field_name, field_type, ui_type, "number(timestamp millis)", value
        )

    if field_type == 1003 and ui_type == "CreatedUser":
        if not isinstance(value, list):
            _raise_value_type_error(
                field_name, field_type, ui_type, "list[user]", value
            )

        names: list[str] = []
        for item in value:
            if not isinstance(item, dict):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "user object", item
                )

            en_name = item.get("en_name")
            if not isinstance(en_name, str):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "user.en_name=str", item
                )
            names.append(en_name)

        return names

    if field_type == 11 and ui_type == "User":
        if not isinstance(value, list):
            _raise_value_type_error(
                field_name, field_type, ui_type, "list[user]", value
            )

        names: list[str] = []
        for item in value:
            if not isinstance(item, dict):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "user object", item
                )

            en_name = item.get("en_name")
            if not isinstance(en_name, str):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "user.en_name=str", item
                )
            names.append(en_name)

        return names

    if field_type == 18 and ui_type == "SingleLink":
        if value is None:
            return []
        if isinstance(value, dict) and not value:
            return []
        _raise_value_type_error(field_name, field_type, ui_type, "empty object", value)

    if field_type == 20 and ui_type == "Formula":
        if not isinstance(value, dict):
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "object(type=1,value=list[text])",
                value,
            )

        formula_type = value.get("type")
        if formula_type != 1:
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "object(type=1,value=list[text])",
                value,
            )

        formula_value = value.get("value")
        if not isinstance(formula_value, list):
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "object(type=1,value=list[text])",
                value,
            )

        lines: list[str] = []
        for item in formula_value:
            if not isinstance(item, dict):
                _raise_value_type_error(
                    field_name,
                    field_type,
                    ui_type,
                    "value item object(type=text,text=str)",
                    item,
                )
            if item.get("type") != "text":
                _raise_value_type_error(
                    field_name,
                    field_type,
                    ui_type,
                    "value item type=text",
                    item,
                )

            text = item.get("text")
            if not isinstance(text, str):
                _raise_value_type_error(
                    field_name,
                    field_type,
                    ui_type,
                    "value item text=str",
                    item,
                )
            lines.append(text)

        return lines

    if field_type == 4 and ui_type == "MultiSelect":
        if not isinstance(value, list):
            _raise_value_type_error(
                field_name, field_type, ui_type, "list[string]", value
            )

        lines: list[str] = []
        for item in value:
            if not isinstance(item, str):
                _raise_value_type_error(
                    field_name, field_type, ui_type, "list item string", item
                )
            lines.append(item)

        return lines

    if field_type != 1:
        raise ValueError(
            f"Unsupported bitable field type for now: type={field_type}, ui_type={ui_type!r}, "
            f"field={field_name!r}"
        )

    if not isinstance(value, list):
        _raise_value_type_error(field_name, field_type, ui_type, "list[text]", value)

    lines: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "list item object(type=text,text=str)",
                item,
            )
        if item.get("type") != "text":
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "list item type=text",
                item,
            )
        text = item.get("text")
        if not isinstance(text, str):
            _raise_value_type_error(
                field_name,
                field_type,
                ui_type,
                "list item text=str",
                item,
            )
        lines.append(text)
    return lines

def _raise_value_type_error(
    field_name: str,
    field_type: int,
    ui_type: str,
    expected: str,
    value: Any,
) -> None:
    raise ValueError(
        "Unsupported bitable cell value "
        f"for field={field_name!r}, type={field_type}, ui_type={ui_type!r}: "
        f"expected {expected}, got {type(value).__name__}"
    )

def _format_unix_timestamp_millis_local(timestamp_millis: int | float) -> str:
    dt = datetime.fromtimestamp(float(timestamp_millis) / 1000).astimezone()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
