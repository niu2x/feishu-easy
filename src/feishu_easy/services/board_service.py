from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

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

    image = Image.open(BytesIO(content))
    cropped = crop_blank_border(image)

    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = file_name or f"{whiteboard_id}.png"
    safe_name = Path(resolved_name).name
    if not safe_name:
        raise ServiceValidationError("Resolved file name is empty")

    output_path = output_dir / safe_name
    cropped.save(output_path, format="PNG")

    return {
        "file_name": safe_name,
        "output_path": str(output_path),
        "size": output_path.stat().st_size,
    }

def crop_blank_border(
    image: Image.Image,
    *,
    alpha_threshold: int = 0,
    white_tolerance: int = 8,
    padding: int = 0,
) -> Image.Image:
    """Crop transparent and near-white blank borders from an image.

    Pixels are treated as blank when:
    - alpha <= ``alpha_threshold`` (for images that have alpha), or
    - RGB channels are all >= ``255 - white_tolerance``.

    Args:
        image: Input image.
        alpha_threshold: Max alpha considered transparent blank. Range 0-255.
        white_tolerance: Near-white tolerance. Range 0-255.
        padding: Extra pixels kept around detected content.

    Returns:
        Cropped image. If no non-blank content is found, returns the original image.
    """

    alpha_threshold = _clamp_u8(alpha_threshold)
    white_tolerance = _clamp_u8(white_tolerance)
    padding = max(0, int(padding))

    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    left = width
    top = height
    right = -1
    bottom = -1

    white_floor = 255 - white_tolerance

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            is_transparent_blank = a <= alpha_threshold
            is_near_white_blank = r >= white_floor and g >= white_floor and b >= white_floor

            if is_transparent_blank or is_near_white_blank:
                continue

            if x < left:
                left = x
            if y < top:
                top = y
            if x > right:
                right = x
            if y > bottom:
                bottom = y

    if right < left or bottom < top:
        return image

    crop_left = max(0, left - padding)
    crop_top = max(0, top - padding)
    crop_right = min(width, right + 1 + padding)
    crop_bottom = min(height, bottom + 1 + padding)

    return image.crop((crop_left, crop_top, crop_right, crop_bottom))

def _clamp_u8(value: int) -> int:
    return max(0, min(255, int(value)))
