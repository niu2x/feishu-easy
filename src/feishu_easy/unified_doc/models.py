from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class BlockType(StrEnum):
    Unknown = "unknown"

    Passthrough = "passthrough"

    Code = "code"
    Heading = "heading"
    Paragraph = "paragraph"
    Quote = "quote"
    Todo = "todo"

    Table = "table"

    List = "list"


class MarkType(StrEnum):
    Bold = "bold"
    Italic = "italic"
    Underline = "underline"
    Link = "link"
    Image = "image"
    Strikethrough = "strikethrough"
    InlineCode = "inline_code"


class DocumentMeta(BaseModel):
    created_at: int | None = None
    updated_at: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class Mark(BaseModel):
    type: MarkType
    attrs: dict[str, Any] = Field(default_factory=dict)


class InlineText(BaseModel):
    text: str
    marks: list[Mark] = Field(default_factory=list)


class Block(BaseModel):
    type: BlockType = BlockType.Unknown
    attrs: dict[str, Any] = Field(default_factory=dict)
    inlines: list[InlineText] = Field(default_factory=list)
    children: list[Block] = Field(default_factory=list)


class UnifiedDocument(BaseModel):
    title: str | None = None
    source_type: str
    blocks: list[Block] = Field(default_factory=list)
    meta: DocumentMeta = Field(default_factory=DocumentMeta)


def extract_mark_urls_from_blocks(blocks: list[Block]) -> tuple[list[str], list[str]]:
    image_urls: list[str] = []
    link_urls: list[str] = []
    seen_image_urls: set[str] = set()
    seen_link_urls: set[str] = set()

    def add_url(mark_type: MarkType, url: str) -> None:
        if mark_type == MarkType.Image:
            if url not in seen_image_urls:
                seen_image_urls.add(url)
                image_urls.append(url)
            return

        if mark_type == MarkType.Link:
            if url not in seen_link_urls:
                seen_link_urls.add(url)
                link_urls.append(url)

    def walk(block: Block) -> None:
        for inline in block.inlines:
            for mark in inline.marks:
                url = mark.attrs.get("url")
                if isinstance(url, str) and url:
                    add_url(mark.type, url)

        for child in block.children:
            walk(child)

    for block in blocks:
        walk(block)

    return image_urls, link_urls
