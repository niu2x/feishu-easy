from __future__ import annotations

from typing import Any
from pathlib import Path

from ..feishu_api import FeishuAPI
from .errors import ServiceValidationError


def list_drive_file(
    folder_token: str | None = None,
    order_by: str | None = None,
    direction: str | None = None,
    user_id_type: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.list_file(
        folder_token=folder_token,
        order_by=order_by,
        direction=direction,
        user_id_type=user_id_type,
    )


def delete_drive_file(
    file_token: str,
    file_type: str = "file",
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.delete_file(file_token=file_token, file_type=file_type)


def batch_query_drive_meta(
    request_docs: list[tuple[str, str]],
    with_url: bool = True,
    user_id_type: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.batch_query_meta(
        request_docs=request_docs,
        with_url=with_url,
        user_id_type=user_id_type,
    )


def get_drive_file_statistics(
    file_token: str,
    file_type: str = "file",
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.get_file_statistics(
        file_token=file_token, file_type=file_type
    )


def list_drive_file_view_record(
    file_token: str,
    file_type: str = "file",
    viewer_id_type: str | None = "open_id",
    page_size: int | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.list_file_view_record(
        file_token=file_token,
        file_type=file_type,
        viewer_id_type=viewer_id_type,
        page_size=page_size,
    )


def list_drive_file_version(
    file_token: str,
    obj_type: str,
    page_size: int | None = None,
    user_id_type: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.list_file_version(
        file_token=file_token,
        obj_type=obj_type,
        page_size=page_size,
        user_id_type=user_id_type,
    )


def copy_drive_file(
    file_token: str,
    file_type: str = "file",
    folder_token: str | None = None,
    name: str | None = None,
    user_id_type: str | None = None,
    extra: dict[str, Any] | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.copy_file(
        file_token=file_token,
        file_type=file_type,
        folder_token=folder_token,
        name=name,
        user_id_type=user_id_type,
        extra=extra,
    )


def move_drive_file(
    file_token: str,
    file_type: str = "file",
    folder_token: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.move_file(
        file_token=file_token,
        file_type=file_type,
        folder_token=folder_token,
    )


def upload_drive_file(
    local_file: Path,
    folder_token: str,
    file_name: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.upload_file(
        local_file=local_file,
        folder_token=folder_token,
        file_name=file_name,
    )


def download_drive_file(
    file_token: str,
    output_dir: Path = Path("."),
    file_name: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    remote_file_name, content = feishu_api.drive.download_file(file_token=file_token)

    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = file_name or remote_file_name
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


def download_drive_media(
    file_token: str,
    output_dir: Path = Path("."),
    file_name: str | None = None,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    remote_file_name, content = feishu_api.drive.download_media(file_token=file_token)

    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = file_name or remote_file_name
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


def subscribe_drive_file(
    file_token: str,
    file_type: str,
    event_type: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.subscribe_file(
        file_token=file_token,
        file_type=file_type,
        event_type=event_type,
    )


def delete_subscribe_drive_file(
    file_token: str,
    file_type: str,
    event_type: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.delete_subscribe_file(
        file_token=file_token,
        file_type=file_type,
        event_type=event_type,
    )


def get_subscribe_drive_file(
    file_token: str,
    file_type: str,
    event_type: str,
    *,
    api: FeishuAPI | None = None,
) -> dict[str, Any]:
    feishu_api = api or FeishuAPI()
    return feishu_api.drive.get_subscribe_file(
        file_token=file_token,
        file_type=file_type,
        event_type=event_type,
    )
