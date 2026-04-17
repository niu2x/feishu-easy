from __future__ import annotations

from typing import Any, Literal
from urllib.parse import parse_qsl, unquote, urlencode, urlparse

from ...unified_doc import (
    Block,
    BlockType,
    DocumentMeta,
    InlineText,
    Mark,
    MarkType,
    UnifiedDocument,
    extract_mark_urls_from_blocks,
)

from .helper import build_feishu_resource_url
from .normalizer import normalize_title
from .utils import extract_dict

Mode = Literal["online", "offline"]


def doc_to_unified(raw: dict[str, Any], mode: Mode) -> UnifiedDocument:
    node = raw["node"]
    obj = raw["obj"]
    blocks = extract_dict(obj, "body/blocks") or []
    unified_blocks = [_convert_block(block, mode) for block in blocks]
    image_urls, link_urls = extract_mark_urls_from_blocks(unified_blocks)

    return UnifiedDocument(
        title=normalize_title(node["title"]),
        source_type="feishu:doc",
        meta=DocumentMeta(
            created_at=_to_int(node.get("obj_create_time")),
            updated_at=_to_int(node.get("obj_edit_time")),
            extra={
                "image_urls": image_urls,
                "link_urls": link_urls,
            },
        ),
        blocks=unified_blocks,
    )


def _asset_path(mode: Mode, asset: str) -> str:
    if mode not in ("online", "offline"):
        raise ValueError(f"Unsupported mode: {mode}")
    return f"/feishu/{mode}/assets/{asset}"


def _convert_block(node: dict[str, Any], mode: Mode) -> Block:
    node_type = node.get("type")

    if node_type == "paragraph":
        return _convert_paragraph(node, mode)

    if node_type == "gallery":
        image_list = extract_dict(node, "gallery/imageList") or []
        inlines: list[InlineText] = []
        for image in image_list:
            url = build_feishu_resource_url(
                _asset_path(mode, "image"),
                {
                    "file_token": image.get("fileToken"),
                },
            )
            inlines.append(
                InlineText(
                    text="",
                    marks=[Mark(type=MarkType.Image, attrs={"url": url})],
                )
            )
        return Block(type=BlockType.Paragraph, inlines=inlines, attrs={})

    if node_type == "table":
        row_size = _to_int(extract_dict(node, "table/rowSize"))
        col_size = _to_int(extract_dict(node, "table/columnSize"))
        merged_cells = extract_dict(node, "table/mergedCells") or []
        merge_info = _normalize_doc_merge_info(merged_cells, row_size, col_size)

        children: list[Block] = []
        for row in extract_dict(node, "table/tableRows") or []:
            for cell in row.get("tableCells", []):
                children.append(_convert_table_cell(cell, mode))

        return Block(
            type=BlockType.Table,
            attrs={
                "row_size": row_size,
                "column_size": col_size,
                "merge_info": merge_info,
            },
            children=children,
            inlines=[],
        )

    if node_type == "callout":
        return Block(
            type=BlockType.Passthrough,
            children=[
                _convert_block(block, mode)
                for block in extract_dict(node, "callout/body/blocks") or []
            ],
            inlines=[],
        )

    if node_type == "horizontalLine":
        return Block(type=BlockType.Passthrough, inlines=[], children=[])

    if node_type == "file":
        file_data = node.get("file", {})
        url = build_feishu_resource_url(
            _asset_path(mode, "file"),
            {
                "file_token": file_data.get("fileToken"),
            },
        )
        file_name = file_data.get("fileName") or ""
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text=f"飞书/文件 {file_name}".strip(),
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            attrs={},
        )

    if node_type == "undefinedBlock":
        return Block(type=BlockType.Passthrough, inlines=[], children=[])

    if node_type == "code":
        return Block(
            type=BlockType.Passthrough,
            children=[
                _convert_block(block, mode)
                for block in extract_dict(node, "code/body/blocks") or []
            ],
            inlines=[],
        )

    if node_type == "diagram":
        diagram_data = node.get("diagram", {})
        url = build_feishu_resource_url(
            _asset_path(mode, "diagram"),
            {
                "diagram_type": diagram_data.get("diagramType"),
                "diagram_token": diagram_data.get("token"),
                "master_obj_type": "doc",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/diagram",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            attrs={},
        )

    if node_type == "sheet":
        sheet_data = node.get("sheet", {})
        url = build_feishu_resource_url(
            _asset_path(mode, "sheet"),
            {
                "token": sheet_data.get("token"),
                "master_obj_type": "doc",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/sheet",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            attrs={},
        )

    if node_type == "bitable":
        bitable_data = node.get("bitable", {})
        url = build_feishu_resource_url(
            _asset_path(mode, "bitable"),
            {
                "token": bitable_data.get("token"),
                "master_obj_type": "doc",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/多维表格",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            attrs={},
        )

    if node_type == "docsApp":
        docs_app = node.get("docsApp", {})
        url = build_feishu_resource_url(
            _asset_path(mode, "docs_app"),
            {
                "type_id": docs_app.get("typeId"),
                "instance_id": docs_app.get("instanceId"),
                "master_obj_type": "doc",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/docsApp",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            attrs={},
        )

    raise Exception(f"Unsupport node_type {node_type}")


def _convert_paragraph(node: dict[str, Any], mode: Mode) -> Block:
    paragraph_data = node.get("paragraph", {})
    inlines = _convert_elements(paragraph_data.get("elements", []), mode)

    style = paragraph_data.get("style", {})
    heading_level = style.get("headingLevel")
    if isinstance(heading_level, int) and heading_level > 0:
        return Block(
            type=BlockType.Heading,
            inlines=inlines,
            attrs={"level": heading_level},
        )

    list_data = style.get("list")
    if isinstance(list_data, dict):
        list_type = str(list_data.get("type") or "").lower()
        is_ordered = "number" in list_type
        return Block(
            type=BlockType.List, inlines=inlines, attrs={"ordered": is_ordered}
        )

    return Block(type=BlockType.Paragraph, inlines=inlines, attrs={})


def _convert_table_cell(cell: dict[str, Any], mode: Mode) -> Block:
    blocks = extract_dict(cell, "body/blocks") or []
    return Block(
        type=BlockType.Passthrough,
        inlines=[],
        children=[_convert_block(block, mode) for block in blocks],
    )


def _normalize_doc_merge_info(
    merged_cells: list[dict[str, Any]],
    row_size: int | None,
    col_size: int | None,
) -> list[dict[str, int]]:
    if not isinstance(row_size, int) or row_size <= 0:
        return []
    if not isinstance(col_size, int) or col_size <= 0:
        return []

    total = row_size * col_size
    merge_info: list[dict[str, int]] = [
        {"row_span": 1, "col_span": 1} for _ in range(total)
    ]

    for item in merged_cells:
        r0 = _to_int(item.get("rowStartIndex"))
        r1 = _to_int(item.get("rowEndIndex"))
        c0 = _to_int(item.get("columnStartIndex"))
        c1 = _to_int(item.get("columnEndIndex"))
        if r0 is None or r1 is None or c0 is None or c1 is None:
            continue
        if r0 < 0 or c0 < 0 or r1 <= r0 or c1 <= c0:
            continue
        if r0 >= row_size or c0 >= col_size:
            continue

        row_span = min(r1, row_size) - r0
        col_span = min(c1, col_size) - c0
        index = r0 * col_size + c0
        if 0 <= index < total:
            merge_info[index] = {"row_span": row_span, "col_span": col_span}

    return merge_info


def _convert_elements(elements: list[dict[str, Any]], mode: Mode) -> list[InlineText]:
    inlines: list[InlineText] = []

    for elem in elements:
        for key, value in elem.items():
            if key == "type":
                continue

            if key == "textRun":
                inlines.append(_convert_inline_text_run(value, mode))
            elif key == "file":
                inlines.append(_convert_inline_file(value, mode))
            elif key == "docsLink":
                inlines.append(_convert_inline_docs_link(value, mode))
            elif key == "person":
                inlines.append(_convert_inline_person(value))
            elif key == "reminder":
                inlines.append(InlineText(text="", marks=[]))
            else:
                raise Exception(f"Unsupport elem {key}")

    return inlines


def _convert_inline_text_run(text_run: dict[str, Any], mode: Mode) -> InlineText:
    marks: list[Mark] = []

    style = text_run.get("style", {})
    if style.get("bold"):
        marks.append(Mark(type=MarkType.Bold, attrs={}))
    if style.get("italic"):
        marks.append(Mark(type=MarkType.Italic, attrs={}))
    if style.get("underline"):
        marks.append(Mark(type=MarkType.Underline, attrs={}))
    if style.get("strikethrough"):
        marks.append(Mark(type=MarkType.Strikethrough, attrs={}))
    if style.get("inlineCode"):
        marks.append(Mark(type=MarkType.InlineCode, attrs={}))

    link_url = extract_dict(text_run, "style/link/url")
    if link_url:
        marks.append(
            Mark(
                type=MarkType.Link,
                attrs={"url": _rewrite_feishu_wiki_link(unquote(link_url), mode)},
            )
        )

    return InlineText(text=text_run.get("text", ""), marks=marks)


def _convert_inline_file(file_content: dict[str, Any], mode: Mode) -> InlineText:
    url = build_feishu_resource_url(
        _asset_path(mode, "file"),
        {
            "file_token": file_content.get("fileToken"),
        },
    )
    file_name = file_content.get("fileName") or ""
    return InlineText(
        text=f"飞书/文件 {file_name}".strip(),
        marks=[Mark(type=MarkType.Link, attrs={"url": url})],
    )


def _convert_inline_docs_link(docs_link: dict[str, Any], mode: Mode) -> InlineText:
    url = docs_link.get("url")
    rewritten_url = (
        _rewrite_feishu_wiki_link(url, mode) if isinstance(url, str) else url
    )
    return InlineText(
        text="飞书/docsLink",
        marks=[Mark(type=MarkType.Link, attrs={"url": rewritten_url})],
    )


def _convert_inline_person(person: dict[str, Any]) -> InlineText:
    return InlineText(text=f"@User({person.get('openId')})", marks=[])


def _rewrite_feishu_wiki_link(url: str, mode: Mode) -> str:
    parsed = urlparse(url)
    if parsed.netloc != "rzvo5fieru.feishu.cn":
        return url

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2 or path_parts[0] != "wiki":
        return url

    node_token = path_parts[1]
    if not node_token:
        return url

    query_pairs = [
        ("node_token", node_token),
        *parse_qsl(parsed.query, keep_blank_values=True),
    ]
    return f"/feishu/{mode}/markdown_preview?{urlencode(query_pairs)}"


def _to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None
