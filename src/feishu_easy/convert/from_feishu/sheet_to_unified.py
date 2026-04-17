from __future__ import annotations
from typing import Any
from .normalizer import normalize_title

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

def sheet_to_unified(param: dict[str, Any]) -> UnifiedDocument:
    blocks: list[Block] = []

    for raw in param["obj"]:
        blocks.extend(sheet_page_to_blocks(raw))

    image_urls, link_urls = extract_mark_urls_from_blocks(blocks)
    node = param.get("node") if isinstance(param, dict) else None
    title_value = node.get("title") if isinstance(node, dict) else None
    return UnifiedDocument(
        title=normalize_title(title_value),
        source_type="feishu:sheet",
        blocks=blocks,
        meta=DocumentMeta(extra={"image_urls": image_urls, "link_urls": link_urls}),
    )

def sheet_page_to_blocks(raw: dict[str, Any]) -> list[Block]:
    if raw.get("resource_type") == "sheet":
        sheet_info = raw
        payload = raw.get("data")

        if payload is None:
            raise ValueError("sheet_to_unified requires raw['obj'][*]['data']")

        value_range = payload.get("valueRange", {})
        major_dimension = value_range.get("majorDimension")
        if major_dimension != "ROWS":
            raise ValueError(f"Unsupported sheet majorDimension: {major_dimension}")

        values = value_range.get("values")
        if not isinstance(values, list):
            values = []

        row_size = len(values)
        col_size = max((len(row) for row in values if isinstance(row, list)), default=0)
        merge_ranges = _extract_sheet_merge_ranges(sheet_info, row_size, col_size)
        merge_info = _normalize_sheet_merge_info(merge_ranges, row_size, col_size)
        table_cells = _build_table_cells(values, row_size, col_size, merge_ranges)

        page_blocks: list[Block] = []
        title = sheet_info.get("title") if isinstance(sheet_info, dict) else None
        if isinstance(title, str) and title.strip():
            page_blocks.append(
                Block(
                    type=BlockType.Heading,
                    attrs={"level": 2},
                    inlines=[InlineText(text=title.strip(), marks=[])],
                )
            )

        if row_size > 0 and col_size > 0:
            page_blocks.append(
                Block(
                    type=BlockType.Table,
                    attrs={
                        "row_size": row_size,
                        "column_size": col_size,
                        "merge_info": merge_info,
                    },
                    inlines=[],
                    children=table_cells,
                )
            )

        return page_blocks

    elif raw.get("resource_type") == "bitable":
        from .bitable_to_unified import bitable_page_to_blocks

        return bitable_page_to_blocks(raw)

    else:
        return []

def _convert_table_cell(cell: Any) -> Block:
    return Block(
        type=BlockType.Passthrough,
        inlines=[],
        children=[
            Block(
                type=BlockType.Paragraph, inlines=_convert_cell_inlines(cell), attrs={}
            )
        ],
    )

def _convert_cell_inlines(cell: Any) -> list[InlineText]:
    if isinstance(cell, str):
        return [InlineText(text=cell, marks=[])]

    if isinstance(cell, dict):
        cell_type = cell.get("type")
        text = _to_text(cell.get("text"))

        if cell_type == "url":
            link = cell.get("link")
            if isinstance(link, str) and link:
                return [
                    InlineText(
                        text=text, marks=[Mark(type=MarkType.Link, attrs={"url": link})]
                    )
                ]
            return [InlineText(text=text, marks=[])]

        if cell_type in {"mention", "text", "attachment"}:
            return [InlineText(text=text, marks=[])]

        if cell_type == "embed-image":
            link = cell.get("link")
            if isinstance(link, str) and link:
                return [
                    InlineText(
                        text=text,
                        marks=[Mark(type=MarkType.Image, attrs={"url": link})],
                    )
                ]
            return [InlineText(text=text, marks=[])]

        if cell_type == "#UNSUPPORT VALUE":
            return []

        raise ValueError(f"Unsupported sheet cell type: {cell}")

    if isinstance(cell, list):
        merged: list[InlineText] = []
        for part in cell:
            part_inlines = _convert_cell_inlines(part)
            if not part_inlines:
                continue
            if merged:
                merged.append(InlineText(text=" ", marks=[]))
            merged.extend(part_inlines)
        return merged

    if cell is None:
        return []

    if isinstance(cell, int | float):
        return [InlineText(text=str(cell), marks=[])]

    raise ValueError(f"Unsupported sheet cell value type: {type(cell)}")

def _to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)

def _normalize_sheet_merge_info(
    merge_ranges: list[tuple[int, int, int, int]],
    row_size: int,
    col_size: int,
) -> list[dict[str, int]]:
    if row_size <= 0 or col_size <= 0:
        return []

    total = row_size * col_size
    merge_info: list[dict[str, int]] = [
        {"row_span": 1, "col_span": 1} for _ in range(total)
    ]

    for r0, r1, c0, c1 in merge_ranges:
        row_span = r1 - r0 + 1
        col_span = c1 - c0 + 1
        index = r0 * col_size + c0
        if 0 <= index < total:
            merge_info[index] = {"row_span": row_span, "col_span": col_span}

    return merge_info

def _extract_sheet_merge_ranges(
    sheet_info: Any,
    row_size: int,
    col_size: int,
) -> list[tuple[int, int, int, int]]:
    if row_size <= 0 or col_size <= 0:
        return []
    if not isinstance(sheet_info, dict):
        return []

    merges = sheet_info.get("merges")
    if not isinstance(merges, list):
        return []

    ranges: list[tuple[int, int, int, int]] = []
    for item in merges:
        if not isinstance(item, dict):
            continue

        r0 = _to_int(item.get("start_row_index"))
        r1 = _to_int(item.get("end_row_index"))
        c0 = _to_int(item.get("start_column_index"))
        c1 = _to_int(item.get("end_column_index"))
        if r0 is None or r1 is None or c0 is None or c1 is None:
            continue
        if r0 < 0 or c0 < 0 or r1 < r0 or c1 < c0:
            continue
        if r0 >= row_size or c0 >= col_size:
            continue

        ranges.append((r0, min(r1, row_size - 1), c0, min(c1, col_size - 1)))

    return ranges

def _build_table_cells(
    values: list[Any],
    row_size: int,
    col_size: int,
    merge_ranges: list[tuple[int, int, int, int]],
) -> list[Block]:
    table_cells: list[Block] = []

    covered_cells: dict[int, set[int]] = {}
    for r0, r1, c0, c1 in merge_ranges:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if r == r0 and c == c0:
                    continue
                covered_cells.setdefault(r, set()).add(c)

    for row_index in range(row_size):
        row = values[row_index] if row_index < len(values) else []
        row_values = row if isinstance(row, list) else []
        covered_in_row = covered_cells.get(row_index, set())
        expected_without_covered = max(0, col_size - len(covered_in_row))
        use_compact_mode = len(row_values) <= expected_without_covered
        compact_cursor = 0

        for col in range(col_size):
            if use_compact_mode and col in covered_in_row:
                table_cells.append(_convert_table_cell(None))
                continue

            if use_compact_mode:
                cell = (
                    row_values[compact_cursor]
                    if compact_cursor < len(row_values)
                    else None
                )
                compact_cursor += 1
            else:
                cell = row_values[col] if col < len(row_values) else None

            table_cells.append(_convert_table_cell(cell))

    return table_cells

def _to_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return None
    return None
