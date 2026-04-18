from __future__ import annotations

import json
from collections.abc import Callable
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

from .docx_block_type import DOCX_BLOCK_TYPE
from .helper import build_feishu_resource_url
from .normalizer import normalize_title
from .utils import convert_whiteboard_to_mermaid_code_block, extract_dict

Mode = Literal["online", "offline"]

def docx_to_unified(
    raw: dict[str, Any],
    mode: Mode,
    *,
    expand_board: bool = False,
    board_node_fetcher: Callable[[str], dict[str, Any]] | None = None,
) -> UnifiedDocument:
    blocks_dict = build_blocks_dict(raw["obj"])
    unified_blocks = [
        convert_single_block(
            blocks_dict,
            raw["obj"][0]["block_id"],
            mode,
            expand_board=expand_board,
            board_node_fetcher=board_node_fetcher,
        )
    ]
    image_urls, link_urls = extract_mark_urls_from_blocks(unified_blocks)

    return UnifiedDocument(
        title=normalize_title(raw["node"]["title"]),
        source_type="feishu:docx",
        meta=DocumentMeta(
            created_at=int(raw["node"]["obj_create_time"]),
            updated_at=int(raw["node"]["obj_edit_time"]),
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

def build_blocks_dict(blocks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    blocks_dict: dict[str, dict[str, Any]] = {}
    for block in blocks:
        blocks_dict[block["block_id"]] = block
    return blocks_dict

def convert_single_block(
    blocks_dict: dict[str, dict[str, Any]],
    block_id: str,
    mode: Mode,
    *,
    expand_board: bool = False,
    board_node_fetcher: Callable[[str], dict[str, Any]] | None = None,
) -> Block:
    block = blocks_dict[block_id]
    block_type = block["block_type"]

    if block_type == 999:
        return Block(type=BlockType.Paragraph, inlines=[], children=[])

    block_name = DOCX_BLOCK_TYPE[block_type]

    children: list[Block] = []
    if "children" in block:
        children = convert_blocks(
            blocks_dict,
            block["children"],
            mode,
            expand_board=expand_board,
            board_node_fetcher=board_node_fetcher,
        )

    if block_name == "页面":
        return Block(type=BlockType.Passthrough, inlines=[], children=children)
    if block_name == "链接预览":
        return Block(type=BlockType.Paragraph, inlines=[], children=[])

    if (
        block_name == "标题 1"
        or block_name == "标题 2"
        or block_name == "标题 3"
        or block_name == "标题 4"
        or block_name == "标题 5"
        or block_name == "标题 6"
        or block_name == "标题 7"
        or block_name == "标题 8"
        or block_name == "标题 9"
    ):
        level = int(block_name.split(" ")[1].strip())
        return Block(
            type=BlockType.Heading,
            inlines=convert_elements(block[f"heading{level}"]["elements"], mode),
            children=children,
            attrs={"level": level},
        )

    if block_name == "议程项标题":
        return Block(
            type=BlockType.Paragraph,
            inlines=convert_elements(block["agenda_item_title"]["elements"], mode),
            children=children,
            attrs={},
        )

    if block_name == "议程项内容" or block_name == "议程项" or block_name == "议程":
        return Block(type=BlockType.Passthrough, inlines=[], children=children)

    if block_name == "文档小组件":
        if block["add_ons"].get("component_type_id") == "blk_631fefbbae02400430b8f9f4":
            record_raw = block["add_ons"].get("record")
            record = json.loads(record_raw)
            data = record.get("data")
            return Block(
                type=BlockType.Code,
                inlines=[InlineText(text=data, marks=[])],
                children=children,
                attrs={"language": "mermaid"},
            )

        url = build_feishu_resource_url(
            _asset_path(mode, "add_ons"),
            {
                "component_id": block["add_ons"]["component_id"],
                "component_type_id": block["add_ons"]["component_type_id"],
                "record": block["add_ons"]["record"],
                "master_obj_type": "docx",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/文档小组件",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "开放平台小组件":
        url = build_feishu_resource_url(
            _asset_path(mode, "isv"),
            {
                "component_type_id": block["isv"]["component_type_id"],
                "component_id": block["isv"]["component_id"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/开放平台小组件",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "Wiki 子目录":
        url = build_feishu_resource_url(
            _asset_path(mode, "wiki_catalog"),
            {
                "wiki_token": block["wiki_catalog"]["wiki_token"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/Wiki 子目录",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "Wiki 新版子目录":
        url = build_feishu_resource_url(
            _asset_path(mode, "sub_page_list"),
            {
                "wiki_token": block["sub_page_list"]["wiki_token"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/Wiki 新版子目录",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "引用的多维表格":
        url = build_feishu_resource_url(
            _asset_path(mode, "reference_base"),
            {
                "token": block["reference_base"]["token"],
                "view_id": block["reference_base"]["view_id"],
                "master_obj_type": "docx",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/引用的多维表格",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "引用同步块":
        url = build_feishu_resource_url(
            _asset_path(mode, "reference_synced"),
            {
                "source_document_id": block["reference_synced"]["source_document_id"],
                "source_block_id": block["reference_synced"]["source_block_id"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/引用同步块",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "文本":
        return Block(
            type=BlockType.Paragraph,
            inlines=convert_elements(block["text"]["elements"], mode),
            children=children,
            attrs={},
        )

    if block_name == "待办事项":
        return Block(
            type=BlockType.Todo,
            inlines=convert_elements(block["todo"]["elements"], mode),
            children=children,
            attrs={"done": extract_dict(block, "todo/style/done")},
        )

    if block_name == "表格":
        merge_info = block["table"]["property"]["merge_info"]
        return Block(
            type=BlockType.Table,
            children=children,
            attrs={
                "row_size": block["table"]["property"]["row_size"],
                "column_size": block["table"]["property"]["column_size"],
                "merge_info": merge_info,
            },
            inlines=[],
        )

    if block_name == "多维表格":
        url = build_feishu_resource_url(
            _asset_path(mode, "bitable"),
            {
                "master_obj_type": "docx",
                "token": block["bitable"]["token"],
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
            children=children,
        )

    if block_name == "有序列表":
        return Block(
            type=BlockType.List,
            inlines=convert_elements(block["ordered"]["elements"], mode),
            children=children,
            attrs={"ordered": True},
        )

    if block_name == "无序列表":
        return Block(
            type=BlockType.List,
            inlines=convert_elements(block["bullet"]["elements"], mode),
            children=children,
            attrs={"ordered": False},
        )

    if block_name == "图片":
        url = build_feishu_resource_url(
            _asset_path(mode, "image"),
            {
                "file_token": block["image"]["token"],
                "width": block["image"]["width"],
                "height": block["image"]["height"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/图片",
                    marks=[Mark(type=MarkType.Image, attrs={"url": url})],
                )
            ],
            children=children,
            attrs={},
        )

    if block_name == "代码块":
        return Block(
            type=BlockType.Code,
            inlines=convert_elements(block["code"]["elements"], mode),
            children=children,
            attrs={},
        )

    if (
        block_name == "分栏列"
        or block_name == "分栏"
        or block_name == "视图"
        or block_name == "高亮块"
        or block_name == "分割线"
        or block_name == "引用容器"
        or block_name == "源同步块"
    ):
        return Block(type=BlockType.Passthrough, inlines=[], children=children)

    if block_name == "项目":
        url = build_feishu_resource_url(
            _asset_path(mode, "project"),
            {
                "title": block["project"]["title"],
                "url": block["project"]["url"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/项目",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "会话卡片":
        url = build_feishu_resource_url(
            _asset_path(mode, "chat_card"),
            {
                "chat_id": block["chat_card"]["chat_id"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/会话卡片",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "任务":
        url = build_feishu_resource_url(
            _asset_path(mode, "task"),
            {
                "task_id": block["task"]["task_id"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/任务",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "流程图 & UML":
        url = build_feishu_resource_url(
            _asset_path(mode, "flowchart_UML"),
            {
                "master_obj_type": "docx",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/流程图 & UML",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "思维笔记":
        url = build_feishu_resource_url(
            _asset_path(mode, "mindnote"),
            {
                "token": block["mindnote"]["token"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/思维笔记",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "电子表格":
        url = build_feishu_resource_url(
            _asset_path(mode, "sheet"),
            {
                "token": block["sheet"]["token"],
                "master_obj_type": "docx",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/电子表格",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "内嵌网页":
        url = build_feishu_resource_url(
            _asset_path(mode, "iframe"),
            {
                "url": block["iframe"]["component"]["url"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/内嵌网页",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
        )

    if block_name == "表格单元格":
        return Block(type=BlockType.Passthrough, inlines=[], children=children)

    if block_name == "引用":
        return Block(
            type=BlockType.Quote,
            inlines=convert_elements(block["quote"]["elements"], mode),
            children=children,
            attrs={},
        )

    if block_name == "画板":
        if expand_board and board_node_fetcher is not None:
            board_token = block["board"]["token"]
            board_data = board_node_fetcher(board_token)
            board_block = convert_whiteboard_to_mermaid_code_block(board_data)
            board_block.children = [*board_block.children, *children]
            return board_block

        url = build_feishu_resource_url(
            _asset_path(mode, "board"),
            {
                "token": block["board"]["token"],
                "master_obj_type": "docx",
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text="飞书/画板",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
            attrs={},
        )

    if block_name == "文件":
        url = build_feishu_resource_url(
            _asset_path(mode, "file"),
            {
                "file_token": block["file"]["token"],
            },
        )
        return Block(
            type=BlockType.Paragraph,
            inlines=[
                InlineText(
                    text=f"飞书/文件 {block['file']['name']}",
                    marks=[Mark(type=MarkType.Link, attrs={"url": url})],
                )
            ],
            children=children,
            attrs={},
        )

    raise Exception(f"Unsupport block_type {block_type} {block_name}")

def convert_blocks(
    blocks_dict: dict[str, dict[str, Any]],
    ids_list: list[str],
    mode: Mode,
    *,
    expand_board: bool = False,
    board_node_fetcher: Callable[[str], dict[str, Any]] | None = None,
) -> list[Block]:
    return [
        convert_single_block(
            blocks_dict,
            block_id,
            mode,
            expand_board=expand_board,
            board_node_fetcher=board_node_fetcher,
        )
        for block_id in ids_list
    ]

def convert_inline_text_run(text_run: dict[str, Any], mode: Mode) -> InlineText:
    marks: list[Mark] = []

    link_url = extract_dict(text_run, "text_element_style/link/url")

    if extract_dict(text_run, "text_element_style/bold"):
        marks.append(Mark(type=MarkType.Bold, attrs={}))
    if extract_dict(text_run, "text_element_style/italic"):
        marks.append(Mark(type=MarkType.Italic, attrs={}))
    if extract_dict(text_run, "text_element_style/underline"):
        marks.append(Mark(type=MarkType.Underline, attrs={}))
    if extract_dict(text_run, "text_element_style/strikethrough"):
        marks.append(Mark(type=MarkType.Strikethrough, attrs={}))
    if extract_dict(text_run, "text_element_style/inline_code"):
        marks.append(Mark(type=MarkType.InlineCode, attrs={}))

    if link_url is not None:
        marks.append(
            Mark(
                type=MarkType.Link,
                attrs={"url": rewrite_feishu_wiki_link(unquote(link_url), mode)},
            )
        )

    return InlineText(text=text_run["content"], marks=marks)

def convert_inline_link_preview(link_preview: dict[str, Any], mode: Mode) -> InlineText:
    marks = [
        Mark(
            type=MarkType.Link,
            attrs={"url": rewrite_feishu_wiki_link(link_preview["url"], mode)},
        )
    ]
    return InlineText(text=link_preview["title"], marks=marks)

def convert_inline_mention_doc(mention_doc: dict[str, Any], mode: Mode) -> InlineText:
    marks = [
        Mark(
            type=MarkType.Link,
            attrs={"url": rewrite_feishu_wiki_link(mention_doc["url"], mode)},
        )
    ]
    return InlineText(text=mention_doc["title"], marks=marks)

def convert_inline_mention_user(mention_user: dict[str, Any]) -> InlineText:
    return InlineText(text=f"@User({mention_user['user_id']})", marks=[])

def convert_inline_reminder(_: dict[str, Any]) -> InlineText:
    return InlineText(text="", marks=[])

def convert_inline_inline_block(_: dict[str, Any]) -> InlineText:
    return InlineText(text="", marks=[])

def convert_inline_equation(equation: dict[str, Any]) -> InlineText:
    return InlineText(text=equation["content"], marks=[])

def convert_elements(elements: list[dict[str, Any]], mode: Mode) -> list[InlineText]:
    return [
        convert_inline_item(item, elem[item], mode)
        for elem in elements
        for item in elem
    ]

def convert_inline_item(item: str, payload: dict[str, Any], mode: Mode) -> InlineText:
    if item == "text_run":
        return convert_inline_text_run(payload, mode)
    if item == "link_preview":
        return convert_inline_link_preview(payload, mode)
    if item == "mention_doc":
        return convert_inline_mention_doc(payload, mode)
    if item == "mention_user":
        return convert_inline_mention_user(payload)
    if item == "reminder":
        return convert_inline_reminder(payload)
    if item == "inline_block":
        return convert_inline_inline_block(payload)
    if item == "equation":
        return convert_inline_equation(payload)
    raise Exception(f"Unsupport inline item {item}")

def rewrite_feishu_wiki_link(url: str, mode: Mode) -> str:
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
