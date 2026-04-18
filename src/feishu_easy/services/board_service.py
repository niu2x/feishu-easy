from __future__ import annotations

from pathlib import Path
from typing import Any

from ..feishu_api import FeishuAPI
from .errors import ServiceValidationError

def create_plantuml_whiteboard_node(
    whiteboard_id: str,
    plant_uml_code: str,
    *,
    style_type: int | None = None,
    syntax_type: int | None = None,
    diagram_type: int | None = None,
    overwrite: bool | None = None,
    parse_mode: int | None = None,
) -> dict[str, Any]:
    return _create_plantuml_whiteboard_node(
        whiteboard_id,
        plant_uml_code,
        style_type=style_type,
        syntax_type=syntax_type,
        diagram_type=diagram_type,
        overwrite=overwrite,
        parse_mode=parse_mode,
        api=FeishuAPI(),
    )

def _create_plantuml_whiteboard_node(
    whiteboard_id: str,
    plant_uml_code: str,
    *,
    style_type: int | None = None,
    syntax_type: int | None = None,
    diagram_type: int | None = None,
    overwrite: bool | None = None,
    parse_mode: int | None = None,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.board.create_plantuml_whiteboard_node(
        whiteboard_id=whiteboard_id,
        plant_uml_code=plant_uml_code,
        style_type=style_type,
        syntax_type=syntax_type,
        diagram_type=diagram_type,
        overwrite=overwrite,
        parse_mode=parse_mode,
    )

def list_whiteboard_node(
    whiteboard_id: str,
    user_id_type: str = "open_id",
) -> dict[str, Any]:
    return _list_whiteboard_node(
        whiteboard_id,
        user_id_type=user_id_type,
        api=FeishuAPI(),
    )

def _list_whiteboard_node(
    whiteboard_id: str,
    user_id_type: str = "open_id",
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    return feishu_api.board.list_whiteboard_node(
        whiteboard_id=whiteboard_id,
        user_id_type=user_id_type,
    )

def download_whiteboard_as_image(
    whiteboard_id: str,
    output_dir: Path = Path("."),
    file_name: str | None = None,
) -> dict[str, Any]:
    return _download_whiteboard_as_image(
        whiteboard_id,
        output_dir=output_dir,
        file_name=file_name,
        api=FeishuAPI(),
    )

def _download_whiteboard_as_image(
    whiteboard_id: str,
    output_dir: Path = Path("."),
    file_name: str | None = None,
    *,
    api: FeishuAPI,
) -> dict[str, Any]:
    feishu_api = api
    content = feishu_api.board.download_as_image_whiteboard(whiteboard_id=whiteboard_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = file_name or f"{whiteboard_id}.png"
    safe_name = Path(resolved_name).name
    if not safe_name:
        raise ServiceValidationError("Resolved file name is empty")

    output_path = output_dir / safe_name
    output_path.write_bytes(content)

    return {
        "file_name": safe_name,
        "output_path": str(output_path),
        "size": len(content),
    }
