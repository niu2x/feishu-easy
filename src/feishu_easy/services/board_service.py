from __future__ import annotations

from pathlib import Path
from typing import Any

from ..feishu_api import FeishuAPI
from .errors import ServiceValidationError

def list_whiteboard_node(
    whiteboard_id: str,
    user_id_type: str = "open_id",
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.board.list_whiteboard_node(
        whiteboard_id=whiteboard_id,
        user_id_type=user_id_type,
    )

def download_whiteboard_as_image(
    whiteboard_id: str,
    output_dir: Path = Path("."),
    file_name: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
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
