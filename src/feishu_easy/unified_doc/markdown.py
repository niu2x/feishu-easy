from __future__ import annotations

import html
import textwrap
import unicodedata

from .models import Block, BlockType, InlineText, Mark, MarkType, UnifiedDocument

def unified_to_markdown(document: UnifiedDocument) -> str:
    markdown = _render_document_to_markdown(document)
    return _normalize_markdown(markdown)

def _render_document_to_markdown(document: UnifiedDocument) -> str:
    lines: list[str] = []

    for block in document.blocks:
        rendered = _block_to_markdown(block)
        if rendered:
            lines.extend(rendered)

    return "\n".join(lines).strip()

def _normalize_markdown(markdown: str) -> str:
    from mistletoe.markdown_renderer import MarkdownRenderer
    from mistletoe import Document

    doc = Document(markdown)
    with MarkdownRenderer() as renderer:
        return renderer.render(doc)

def _block_to_markdown(block: Block, list_depth: int = 0) -> list[str]:
    text = _inlines_to_markdown(block.inlines)
    indent = "  " * list_depth

    if block.type == BlockType.Heading:
        level = block.attrs.get("level", 1)
        if not isinstance(level, int) or level < 1:
            level = 1
        level = min(level, 6)
        lines = [textwrap.indent(f"{'#' * level} {text}".rstrip(), indent)]
        lines.append("")
        lines.extend(_render_children(block.children, list_depth))
        return [line for line in lines]

    elif block.type == BlockType.List:
        ordered = bool(block.attrs.get("ordered"))
        marker = "1." if ordered else "-"
        item = textwrap.indent(f"{marker} {text}".rstrip(), indent)
        lines = [item]
        lines.append("")
        for child in block.children:
            lines.extend(_block_to_markdown(child, list_depth + 1))
        return [line for line in lines]

    elif block.type == BlockType.Todo:
        done = bool(block.attrs.get("done"))
        marker = "x" if done else " "
        item = textwrap.indent(f"- [{marker}] {text}".rstrip(), indent)
        lines = [item]
        lines.append("")
        for child in block.children:
            lines.extend(_block_to_markdown(child, list_depth + 1))
        return [line for line in lines]

    elif block.type == BlockType.Table:
        table_lines = _render_table_block(block, indent)
        if table_lines:
            return table_lines + [""]

        lines: list[str] = []
        if text:
            lines.append(textwrap.indent(text, indent))
        lines.append("")
        lines.extend(_render_children(block.children, list_depth))
        return [line for line in lines]

    elif block.type == BlockType.Paragraph:
        lines = [textwrap.indent(text, indent)] if text else []
        lines.append("")
        lines.extend(_render_children(block.children, list_depth))
        return [line for line in lines]

    elif block.type == BlockType.Quote:
        lines = [textwrap.indent(text, indent)] if text else []
        lines.append("")
        lines.extend(_render_children(block.children, list_depth))
        return _to_blockquote_lines(lines, indent)

    elif block.type == BlockType.Code:
        code_text = _inlines_to_plain_text(block.inlines)
        language = (
            block.attrs.get("language") if isinstance(block.attrs, dict) else None
        )
        fence = "```"
        if isinstance(language, str) and language.strip():
            fence = f"```{language.strip()}"
        lines = (
            [textwrap.indent(fence, indent)]
            + ([textwrap.indent(code_text, indent)] if code_text else [])
            + [textwrap.indent("```", indent)]
        )
        lines.append("")
        lines.extend(_render_children(block.children, list_depth))
        return lines

    elif block.type == BlockType.Passthrough:
        lines = _render_children(block.children, list_depth)
        return [line for line in lines]
    else:
        raise Exception(f"Unsupport BlockType {block.type}")

def _render_children(children: list[Block], list_depth: int) -> list[str]:
    lines: list[str] = []
    for child in children:
        child_lines = _block_to_markdown(child, list_depth)
        if child_lines:
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(child_lines)
    return lines

def _to_blockquote_lines(lines: list[str], indent: str) -> list[str]:
    quoted: list[str] = []
    for line in lines:
        if line.strip():
            content = (
                line[len(indent) :] if indent and line.startswith(indent) else line
            )
            quoted.append(f"{indent}> {content}")
        else:
            quoted.append(f"{indent}>")
    return quoted

def _render_table_block(block: Block, indent: str) -> list[str]:
    row_size = _to_positive_int(block.attrs.get("row_size"))
    col_size = _to_positive_int(block.attrs.get("column_size"))
    merge_info = block.attrs.get("merge_info")

    if not block.children:
        return []

    if _has_merged_cells(merge_info) or _table_contains_list(block.children):
        return _render_table_block_html(block, indent, row_size, col_size, merge_info)

    cells = [
        _normalize_table_cell_text(_extract_block_text(cell)) for cell in block.children
    ]
    if not any(cells):
        return []

    if col_size is None and row_size is not None:
        col_size = max(1, (len(cells) + row_size - 1) // row_size)
    if row_size is None and col_size is not None:
        row_size = max(1, (len(cells) + col_size - 1) // col_size)
    if col_size is None:
        col_size = max(1, len(cells))
    if row_size is None:
        row_size = max(1, (len(cells) + col_size - 1) // col_size)

    total = row_size * col_size
    if len(cells) < total:
        cells.extend([""] * (total - len(cells)))
    else:
        cells = cells[:total]

    rows = [cells[i : i + col_size] for i in range(0, total, col_size)]
    if not rows:
        return []

    header = rows[0]
    body = rows[1:]

    lines = [textwrap.indent(_make_table_row(header), indent)]
    lines.append(textwrap.indent(_make_table_row(["---"] * col_size), indent))
    for row in body:
        lines.append(textwrap.indent(_make_table_row(row), indent))
    return lines

def _has_merged_cells(merge_info: object) -> bool:
    if not isinstance(merge_info, list):
        return False

    for item in merge_info:
        if not isinstance(item, dict):
            continue
        row_span = _to_positive_int(item.get("row_span")) or 1
        col_span = _to_positive_int(item.get("col_span")) or 1
        if row_span > 1 or col_span > 1:
            return True
    return False

def _table_contains_list(cells: list[Block]) -> bool:
    for cell in cells:
        if _contains_block_type(cell, BlockType.List):
            return True
    return False

def _contains_block_type(block: Block, target: BlockType) -> bool:
    if block.type == target:
        return True
    for child in block.children:
        if _contains_block_type(child, target):
            return True
    return False

def _render_table_block_html(
    block: Block,
    indent: str,
    row_size: int | None,
    col_size: int | None,
    merge_info: object,
) -> list[str]:
    if row_size is None and col_size is None:
        col_size = max(1, len(block.children))
        row_size = 1
    elif row_size is None:
        row_size = max(1, (len(block.children) + col_size - 1) // col_size)
    elif col_size is None:
        col_size = max(1, (len(block.children) + row_size - 1) // row_size)

    assert row_size is not None
    assert col_size is not None

    rows = _build_html_table_cells(block.children, row_size, col_size, merge_info)
    if not rows:
        return []

    lines = [textwrap.indent("<table>", indent)]
    for row in rows:
        lines.append(textwrap.indent("<tr>", f"{indent}  "))
        for cell in row:
            attrs: list[str] = []
            if cell["row_span"] > 1:
                attrs.append(f'rowspan="{cell["row_span"]}"')
            if cell["col_span"] > 1:
                attrs.append(f'colspan="{cell["col_span"]}"')
            attr_text = f" {' '.join(attrs)}" if attrs else ""
            lines.append(
                textwrap.indent(
                    f"<td{attr_text}>{cell['content']}</td>",
                    f"{indent}    ",
                )
            )
        lines.append(textwrap.indent("</tr>", f"{indent}  "))
    lines.append(textwrap.indent("</table>", indent))
    return lines

def _build_html_table_cells(
    cells: list[Block],
    row_size: int,
    col_size: int,
    merge_info: object,
) -> list[list[dict[str, int | str]]]:
    if row_size <= 0 or col_size <= 0:
        return []

    occupied = [[False for _ in range(col_size)] for _ in range(row_size)]
    anchors: list[list[dict[str, int | str] | None]] = [
        [None for _ in range(col_size)] for _ in range(row_size)
    ]

    span_info = merge_info if isinstance(merge_info, list) else []
    total_slots = row_size * col_size

    if len(cells) >= total_slots:
        for index in range(total_slots):
            r = index // col_size
            c = index % col_size

            if occupied[r][c]:
                continue

            cell_block = cells[index]
            item = (
                span_info[index]
                if index < len(span_info) and isinstance(span_info[index], dict)
                else {}
            )
            row_span = _to_positive_int(item.get("row_span")) or 1
            col_span = _to_positive_int(item.get("col_span")) or 1
            row_span = min(row_span, row_size - r)
            col_span = min(col_span, col_size - c)

            for rr in range(r, r + row_span):
                for cc in range(c, c + col_span):
                    occupied[rr][cc] = True

            anchors[r][c] = {
                "row_span": row_span,
                "col_span": col_span,
                "content": _extract_block_html(cell_block),
            }
    else:
        cursor = 0
        for index, cell_block in enumerate(cells):
            while cursor < total_slots:
                r = cursor // col_size
                c = cursor % col_size
                if not occupied[r][c]:
                    break
                cursor += 1

            if cursor >= total_slots:
                break

            r = cursor // col_size
            c = cursor % col_size

            item = (
                span_info[index]
                if index < len(span_info) and isinstance(span_info[index], dict)
                else {}
            )
            row_span = _to_positive_int(item.get("row_span")) or 1
            col_span = _to_positive_int(item.get("col_span")) or 1
            row_span = min(row_span, row_size - r)
            col_span = min(col_span, col_size - c)

            for rr in range(r, r + row_span):
                for cc in range(c, c + col_span):
                    occupied[rr][cc] = True

            anchors[r][c] = {
                "row_span": row_span,
                "col_span": col_span,
                "content": _extract_block_html(cell_block),
            }

    rows: list[list[dict[str, int | str]]] = []
    for r in range(row_size):
        row_cells: list[dict[str, int | str]] = []
        for c in range(col_size):
            anchor = anchors[r][c]
            if anchor is not None:
                row_cells.append(anchor)
        if row_cells:
            rows.append(row_cells)
    return rows

def _extract_block_text(block: Block) -> str:
    lines = _block_to_markdown(block)
    return "\n".join(lines)

def _extract_block_html(block: Block) -> str:
    lines = _block_to_html(block)
    return "".join(line.strip() for line in lines if line.strip())

def _block_to_html(block: Block) -> list[str]:
    text = _inlines_to_html(block.inlines)

    if block.type == BlockType.Heading:
        level = block.attrs.get("level", 1)
        if not isinstance(level, int) or level < 1:
            level = 1
        level = min(level, 6)
        lines = [f"<h{level}>{text}</h{level}>"] if text else []
        lines.extend(_render_children_html(block.children))
        return lines

    if block.type == BlockType.List:
        ordered = bool(block.attrs.get("ordered"))
        tag = "ol" if ordered else "ul"
        lines = [f"<{tag}><li>{text}</li></{tag}>"]
        lines.extend(_render_children_html(block.children))
        return lines

    if block.type == BlockType.Todo:
        done = bool(block.attrs.get("done"))
        checked = " checked" if done else ""
        lines = [f'<ul><li><input type="checkbox" disabled{checked}/> {text}</li></ul>']
        lines.extend(_render_children_html(block.children))
        return lines

    if block.type == BlockType.Code:
        lines = [f"<pre><code>{text}</code></pre>"]
        lines.extend(_render_children_html(block.children))
        return lines

    if block.type == BlockType.Table:
        nested = _render_table_block_html(
            block,
            indent="",
            row_size=_to_positive_int(block.attrs.get("row_size")),
            col_size=_to_positive_int(block.attrs.get("column_size")),
            merge_info=block.attrs.get("merge_info"),
        )
        if nested:
            return nested

    lines = [text] if text else []
    lines.extend(_render_children_html(block.children))
    return lines

def _render_children_html(children: list[Block]) -> list[str]:
    lines: list[str] = []
    for child in children:
        lines.extend(_block_to_html(child))
    return lines

def _normalize_table_cell_text(text: str) -> str:
    return text.replace("|", "\\|").strip().replace("\n", "<br>")

def _make_table_row(cells: list[str]) -> str:
    return f"| {' | '.join(cells)} |"

def _to_positive_int(value: object) -> int | None:
    if isinstance(value, int) and value > 0:
        return value
    return None

def _inlines_to_markdown(inlines: list[InlineText]) -> str:
    return "".join(_inline_to_markdown(inline) for inline in inlines)

def _inlines_to_plain_text(inlines: list[InlineText]) -> str:
    return "".join(inline.text for inline in inlines)

def _inlines_to_html(inlines: list[InlineText]) -> str:
    return "".join(_inline_to_html(inline) for inline in inlines)

def _inline_to_markdown(inline: InlineText) -> str:
    value = _escape_text(inline.text)
    style_order = (
        MarkType.InlineCode,
        MarkType.Italic,
        MarkType.Underline,
        MarkType.Strikethrough,
        MarkType.Bold,
    )

    has_bold = any(mark.type == MarkType.Bold for mark in inline.marks)

    for mark_type in style_order:
        for mark in inline.marks:
            if mark.type == mark_type:
                value = _apply_mark(value, mark)

    for mark in inline.marks:
        if mark.type in {MarkType.Link, MarkType.Image}:
            value = _apply_mark(value, mark)

    if has_bold and _ends_with_punctuation(inline.text) and not value.endswith(" "):
        value += " "

    return value

def _inline_to_html(inline: InlineText) -> str:
    value = html.escape(inline.text)
    style_order = (
        MarkType.InlineCode,
        MarkType.Italic,
        MarkType.Underline,
        MarkType.Strikethrough,
        MarkType.Bold,
    )

    has_bold = any(mark.type == MarkType.Bold for mark in inline.marks)

    for mark_type in style_order:
        for mark in inline.marks:
            if mark.type == mark_type:
                value = _apply_mark_html(value, mark)

    for mark in inline.marks:
        if mark.type in {MarkType.Link, MarkType.Image}:
            value = _apply_mark_html(value, mark)

    if has_bold and _ends_with_punctuation(inline.text) and not value.endswith(" "):
        value += " "

    return value

def _apply_mark(text: str, mark: Mark) -> str:
    if mark.type == MarkType.Link:
        url = mark.attrs.get("url")
        return f"[{text}]({url})" if url else text
    if mark.type == MarkType.Image:
        url = mark.attrs.get("url")
        alt = text if text else "image"
        return f"![{alt}]({url})" if url else text

    if text.strip() == "":
        return ""

    if mark.type == MarkType.InlineCode:
        return f"`{text}`"
    if mark.type == MarkType.Bold:
        return f"**{text}**"
    if mark.type == MarkType.Italic:
        return f"*{text}*"
    if mark.type == MarkType.Underline:
        return f"<u>{text}</u>"
    if mark.type == MarkType.Strikethrough:
        return f"~~{text}~~"

    return text

def _apply_mark_html(text: str, mark: Mark) -> str:
    if mark.type == MarkType.InlineCode:
        return f"<code>{text}</code>"
    if mark.type == MarkType.Bold:
        return f"<strong>{text}</strong>"
    if mark.type == MarkType.Italic:
        return f"<em>{text}</em>"
    if mark.type == MarkType.Underline:
        return f"<u>{text}</u>"
    if mark.type == MarkType.Strikethrough:
        return f"<del>{text}</del>"

    if mark.type == MarkType.Link:
        url = mark.attrs.get("url")
        if url:
            return f'<a href="{str(url)}">{text}</a>'
        return text
    if mark.type == MarkType.Image:
        url = mark.attrs.get("url")
        if url:
            return f'<img src="{str(url)}" alt="{text or "image"}" />'
        return text
    return text

def _escape_text(text: str) -> str:
    escaped = text.replace("\\", "\\\\")
    for token in ("*", "`", "[", "]"):
        escaped = escaped.replace(token, f"\\{token}")
    return escaped

def _ends_with_punctuation(text: str) -> bool:
    stripped = text.rstrip()
    if not stripped:
        return False
    return unicodedata.category(stripped[-1]).startswith("P")
