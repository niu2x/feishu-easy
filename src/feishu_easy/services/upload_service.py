from __future__ import annotations

import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import filetype
import imagesize
import mistletoe
from mistletoe import Document
from mistletoe.utils import traverse

from ..feishu_api import FeishuAPI

IMAGE_BLOCK_TYPE = 27
TABLE_BLOCK_TYPE = 31


def _collect_descendants(
    root_ids: list[str], block_map: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    descendants: list[dict[str, Any]] = []
    todo_ids = list(root_ids)

    while todo_ids:
        block_id = todo_ids.pop()
        block = block_map[block_id]
        descendants.append(block)
        todo_ids.extend(block.get("children", []))

    return descendants


def _build_block_map(descendants: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    block_map: dict[str, dict[str, Any]] = {}

    for block in descendants:
        normalized = dict(block)
        if normalized.get("block_type") == TABLE_BLOCK_TYPE:
            table = dict(normalized.get("table", {}))
            table_property = dict(table.get("property", {}))
            table_property.pop("merge_info", None)
            table["property"] = table_property
            normalized["table"] = table

        block_map[normalized["block_id"]] = normalized

    return block_map


def _split_descendant_request(
    request_body: dict[str, Any], max_descendants: int = 1000
) -> list[dict[str, Any]]:
    if len(request_body["descendants"]) <= max_descendants:
        block_map = _build_block_map(request_body["descendants"])
        descendants = [
            block_map[block["block_id"]] for block in request_body["descendants"]
        ]
        return [{**request_body, "descendants": descendants}]

    children_ids = request_body["children_id"]
    if len(children_ids) <= 1:
        raise RuntimeError("cannot split request with a single root block")

    half = len(children_ids) // 2
    left_ids = children_ids[:half]
    right_ids = children_ids[half:]
    block_map = _build_block_map(request_body["descendants"])

    left_request = {
        "index": 0,
        "children_id": left_ids,
        "descendants": _collect_descendants(left_ids, block_map),
    }
    right_request = {
        "index": 0,
        "children_id": right_ids,
        "descendants": _collect_descendants(right_ids, block_map),
    }

    requests = _split_descendant_request(left_request) + _split_descendant_request(
        right_request
    )
    for index, req in enumerate(requests):
        req["index"] = index
    return requests


def _download_remote_image(
    image_src: str, temp_dir: Path, index: int, skip_failed: bool
) -> Path | None:
    try:
        with urllib.request.urlopen(image_src, timeout=30) as response:
            image_content = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        if skip_failed:
            return None
        raise ValueError(f"failed to download image: {image_src}") from exc

    kind = filetype.guess(image_content)
    if kind is not None:
        suffix = f".{kind.extension}"
    else:
        parsed_url = urllib.parse.urlparse(image_src)
        suffix = Path(parsed_url.path).suffix or ".img"

    temp_path = temp_dir / f"image_{index}{suffix}"
    temp_path.write_bytes(image_content)
    return temp_path


def _extract_markdown_image_paths(
    content: str, markdown_file: Path, temp_dir: Path, skip_failed_images: bool
) -> list[tuple[int, Path]]:
    image_paths: list[tuple[int, Path]] = []
    image_index = 0

    for cursor in traverse(Document(content)):
        node = cursor.node
        if not isinstance(node, mistletoe.span_token.Image):
            continue

        image_src = node.src.strip()
        current_index = image_index
        image_index += 1

        if image_src.lower().startswith(("http://", "https://")):
            result = _download_remote_image(
                image_src, temp_dir, index=current_index, skip_failed=skip_failed_images
            )
            if result is None:
                continue
            image_paths.append((current_index, result))
            continue

        image_path = (markdown_file.parent / image_src).expanduser().resolve()
        if not image_path.is_file():
            if skip_failed_images:
                continue
            raise FileNotFoundError(f"image file not found: {image_src}")

        image_paths.append((current_index, image_path))

    return image_paths


def _collect_image_block_ids(request_body: dict[str, Any]) -> list[str]:
    image_block_ids: list[str] = []
    block_map = _build_block_map(request_body["descendants"])

    todo_ids = list(request_body["children_id"])
    todo_ids.reverse()
    while todo_ids:
        block_id = todo_ids.pop()
        block = block_map[block_id]

        if block.get("block_type") == IMAGE_BLOCK_TYPE:
            image_block_ids.append(block["block_id"])

        children = list(block.get("children", []))
        children.reverse()
        todo_ids.extend(children)

    return image_block_ids


def _resolve_document_id(api: FeishuAPI, node_token: str) -> str:
    node = api.wiki.get_node(node_token)
    if node["obj_type"] != "docx":
        raise RuntimeError("Only support docx")
    return node["obj_token"]


def _build_descendant_request_body(converted: dict[str, Any]) -> dict[str, Any]:
    return {
        "index": 0,
        "children_id": converted["first_level_block_ids"],
        "descendants": converted["blocks"],
    }


def _clear_document_children(api: FeishuAPI, document_id: str) -> None:
    current_children = api.docx.get_document_block_children(
        document_id=document_id,
        block_id=document_id,
    )
    children_count = len(current_children.get("items", []))
    if children_count <= 0:
        return

    api.docx.batch_delete_document_block_children(
        document_id=document_id,
        block_id=document_id,
        start_index=0,
        end_index=children_count,
    )


def _create_descendants(
    api: FeishuAPI, document_id: str, request_body: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    requests = _split_descendant_request(request_body)
    block_id_relations: list[dict[str, Any]] = []
    for req in requests:
        ret = api.docx.create_document_block_descendant(document_id, document_id, req)

        block_id_relations.extend(ret["block_id_relations"])
    return requests, block_id_relations


def _build_block_id_relations_map(
    block_id_relations: list[dict[str, Any]],
) -> dict[str, str]:
    return {
        relation["temporary_block_id"]: relation["block_id"]
        for relation in block_id_relations
    }


def _resolve_real_image_blocks(
    image_block_ids: list[str], block_id_relations_map: dict[str, str]
) -> list[str]:
    real_block_ids: list[str] = []
    for temporary_block_id in image_block_ids:
        real_block_id = block_id_relations_map.get(temporary_block_id)
        if real_block_id is None:
            raise RuntimeError(
                f"Missing block relation for image block: {temporary_block_id}"
            )
        real_block_ids.append(real_block_id)
    return real_block_ids


def _replace_document_images(
    api: FeishuAPI,
    document_id: str,
    image_real_blocks: list[str],
    indexed_image_paths: list[tuple[int, Path]],
) -> None:
    for image_index, image_path in indexed_image_paths:
        if image_index >= len(image_real_blocks):
            raise RuntimeError(f"Image index {image_index} out of range")
        block_id = image_real_blocks[image_index]

        upload_result = api.drive.upload_media(
            local_file=image_path,
            parent_type="docx_image",
            parent_node=block_id,
        )
        file_token = upload_result["file_token"]

        width, height = imagesize.get(str(image_path))
        if width <= 0 or height <= 0:
            raise RuntimeError(f"Failed to detect image size: {image_path}")

        api.docx.patch_document_block(
            document_id=document_id,
            block_id=block_id,
            request_body={
                "replace_image": {
                    "token": file_token,
                    "width": int(width),
                    "height": int(height),
                }
            },
        )


class MarkdownUploadFlow:
    def __init__(self, api: FeishuAPI | None = None) -> None:
        self.api = api or FeishuAPI()

    def upload(
        self, markdown_file: Path, node_token: str, skip_failed_images: bool = False
    ) -> tuple[str, int]:
        if not markdown_file.exists() or not markdown_file.is_file():
            raise FileNotFoundError(f"file not found: {markdown_file}")

        content = markdown_file.read_text(encoding="utf-8")
        document_id = _resolve_document_id(self.api, node_token)
        if not content.strip():
            _clear_document_children(self.api, document_id)
            return document_id, 0

        with tempfile.TemporaryDirectory(prefix="feishu_flow_") as temp_dir_path:
            image_paths = _extract_markdown_image_paths(
                content, markdown_file, Path(temp_dir_path), skip_failed_images
            )

            converted = self.api.docx.convert_document(
                content=content,
                content_type="markdown",
            )
            request_body = _build_descendant_request_body(converted)

            _clear_document_children(self.api, document_id)

            image_block_ids = _collect_image_block_ids(request_body)
            requests, block_id_relations = _create_descendants(
                self.api,
                document_id,
                request_body,
            )

            self.api.wiki.update_node_title(node_token, markdown_file.stem)

            block_id_relations_map = _build_block_id_relations_map(block_id_relations)
            image_real_blocks = _resolve_real_image_blocks(
                image_block_ids,
                block_id_relations_map,
            )
            _replace_document_images(
                self.api,
                document_id,
                image_real_blocks,
                image_paths,
            )

        return document_id, len(requests)


def upload_markdown(
    markdown_file: Path, node_token: str, skip_failed_images: bool = False
) -> tuple[str, int]:
    flow = MarkdownUploadFlow()
    return flow.upload(
        markdown_file=markdown_file,
        node_token=node_token,
        skip_failed_images=skip_failed_images,
    )
