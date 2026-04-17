from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal

import json

import typer

from ..services.drive_service import delete_drive_file as delete_drive_file_service
from ..services.drive_service import (
    batch_query_drive_meta as batch_query_drive_meta_service,
)
from ..services.drive_service import copy_drive_file as copy_drive_file_service
from ..services.drive_service import (
    get_drive_file_statistics as get_drive_file_statistics_service,
)
from ..services.drive_service import list_drive_file as list_drive_file_service
from ..services.drive_service import (
    download_drive_media as download_drive_media_service,
)
from ..services.drive_service import (
    download_drive_file as download_drive_file_service,
)
from ..services.drive_service import (
    list_drive_file_view_record as list_drive_file_view_record_service,
)
from ..services.drive_service import (
    list_drive_file_version as list_drive_file_version_service,
)
from ..services.drive_service import move_drive_file as move_drive_file_service
from ..services.drive_service import upload_drive_file as upload_drive_file_service
from ..services.drive_service import (
    subscribe_drive_file as subscribe_drive_file_service,
)
from ..services.drive_service import (
    delete_subscribe_drive_file as delete_subscribe_drive_file_service,
)
from ..services.drive_service import (
    get_subscribe_drive_file as get_subscribe_drive_file_service,
)

app = typer.Typer(no_args_is_help=True)
DriveFileType = Literal[
    "file",
    "docx",
    "bitable",
    "folder",
    "doc",
    "sheet",
    "mindnote",
    "shortcut",
    "slides",
]
DRIVE_DOC_TYPES: set[str] = {
    "file",
    "docx",
    "bitable",
    "folder",
    "doc",
    "sheet",
    "mindnote",
    "shortcut",
    "slides",
}

def _parse_doc_option_values(docs: list[str]) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for item in docs:
        doc_type, sep, doc_token = item.partition(":")
        if not sep or not doc_type or not doc_token:
            raise typer.BadParameter(
                "Each --doc must be in '<doc_type>:<doc_token>' format, "
                "for example '--doc docx:doxcn123'",
                param_hint="--doc",
            )
        if doc_type not in DRIVE_DOC_TYPES:
            supported = ", ".join(sorted(DRIVE_DOC_TYPES))
            raise typer.BadParameter(
                f"Unsupported doc_type '{doc_type}'. Supported: {supported}",
                param_hint="--doc",
            )
        parsed.append((doc_token, doc_type))
    if not parsed:
        raise typer.BadParameter(
            "At least one --doc is required",
            param_hint="--doc",
        )
    return parsed

def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

def _parse_extra_json(extra: str | None) -> dict[str, Any] | None:
    if not extra:
        return None
    try:
        parsed = json.loads(extra)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(
            f"--extra must be valid JSON: {exc.msg}",
            param_hint="--extra",
        ) from exc
    if not isinstance(parsed, dict):
        raise typer.BadParameter(
            "--extra must be a JSON object",
            param_hint="--extra",
        )
    return parsed

@app.command()
def delete_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option(
            "--type",
            help="Drive file type: file/docx/bitable/folder/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
) -> None:
    _echo_json(delete_drive_file_service(file_token=file_token, file_type=file_type))

@app.command()
def list_file(
    folder_token: Annotated[
        str | None,
        typer.Option("--folder-token", help="Folder token to list files in"),
    ] = None,
    order_by: Annotated[
        str | None,
        typer.Option("--order-by", help="Sort field, e.g. EditedTime"),
    ] = None,
    direction: Annotated[
        str | None,
        typer.Option("--direction", help="Sort direction: ASC or DESC"),
    ] = None,
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    _echo_json(
        list_drive_file_service(
            folder_token=folder_token,
            order_by=order_by,
            direction=direction,
            user_id_type=user_id_type,
        )
    )

@app.command()
def batch_query_meta(
    docs: Annotated[
        list[str],
        typer.Option(
            "--doc",
            help="Document selector in '<doc_type>:<doc_token>' format, repeatable",
        ),
    ],
    with_url: Annotated[
        bool,
        typer.Option(
            "--with-url/--no-with-url",
            help="Whether to include URL fields in metadata",
        ),
    ] = True,
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    _echo_json(
        batch_query_drive_meta_service(
            request_docs=_parse_doc_option_values(docs),
            with_url=with_url,
            user_id_type=user_id_type,
        )
    )

@app.command()
def get_file_statistics(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option(
            "--type",
            help="File type: file/docx/bitable/folder/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
) -> None:
    _echo_json(
        get_drive_file_statistics_service(file_token=file_token, file_type=file_type)
    )

@app.command()
def list_file_view_record(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option(
            "--type",
            help="File type: file/docx/bitable/folder/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
    viewer_id_type: Annotated[
        str | None,
        typer.Option("--viewer-id-type", help="Viewer id type, e.g. open_id"),
    ] = "open_id",
    page_size: Annotated[
        int | None,
        typer.Option("--page-size", help="Page size for each API request"),
    ] = None,
) -> None:
    _echo_json(
        list_drive_file_view_record_service(
            file_token=file_token,
            file_type=file_type,
            viewer_id_type=viewer_id_type,
            page_size=page_size,
        )
    )

@app.command()
def list_file_version(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option(
            "--type",
            help="File object type: file/docx/bitable/folder/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    _echo_json(
        list_drive_file_version_service(
            file_token=file_token,
            obj_type=file_type,
            user_id_type=user_id_type,
        )
    )

@app.command()
def copy_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option("--type", help="Source file type"),
    ],
    folder_token: Annotated[
        str,
        typer.Option("--folder-token", help="Target folder token"),
    ],
    name: Annotated[
        str,
        typer.Option("--name", help="New file name for copied file"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
    extra: Annotated[
        str | None,
        typer.Option("--extra", help="JSON object for advanced extra parameters"),
    ] = None,
) -> None:
    _echo_json(
        copy_drive_file_service(
            file_token=file_token,
            file_type=file_type,
            folder_token=folder_token,
            name=name,
            user_id_type=user_id_type,
            extra=_parse_extra_json(extra),
        )
    )

@app.command()
def move_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option("--type", help="Source file type"),
    ],
    folder_token: Annotated[
        str,
        typer.Option("--folder-token", help="Target folder token"),
    ],
) -> None:
    _echo_json(
        move_drive_file_service(
            file_token=file_token,
            file_type=file_type,
            folder_token=folder_token,
        )
    )

@app.command()
def upload_file(
    local_file: Annotated[
        Path,
        typer.Argument(help="Local file path to upload"),
    ],
    folder_token: Annotated[
        str,
        typer.Option("--folder-token", help="Target folder token"),
    ],
    file_name: Annotated[
        str | None,
        typer.Option(
            "--file-name", help="Target file name, defaults to local file name"
        ),
    ] = None,
) -> None:
    _echo_json(
        upload_drive_file_service(
            local_file=local_file,
            folder_token=folder_token,
            file_name=file_name,
        )
    )

@app.command()
def download_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Directory to store downloaded file"),
    ] = Path("."),
    file_name: Annotated[
        str | None,
        typer.Option("--file-name", help="Override saved file name"),
    ] = None,
) -> None:
    _echo_json(
        download_drive_file_service(
            file_token=file_token,
            output_dir=output_dir,
            file_name=file_name,
        )
    )

@app.command()
def download_media(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive media file token"),
    ],
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Directory to store downloaded media file"),
    ] = Path("."),
    file_name: Annotated[
        str | None,
        typer.Option("--file-name", help="Override saved file name"),
    ] = None,
) -> None:
    _echo_json(
        download_drive_media_service(
            file_token=file_token,
            output_dir=output_dir,
            file_name=file_name,
        )
    )

@app.command()
def subscribe_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option("--type", help="File type to subscribe"),
    ],
    event_type: Annotated[
        str,
        typer.Option(
            "--event-type",
            help="Event type to subscribe, e.g. file.created_in_folder_v1",
        ),
    ],
) -> None:
    _echo_json(
        subscribe_drive_file_service(
            file_token=file_token,
            file_type=file_type,
            event_type=event_type,
        )
    )

@app.command()
def delete_subscribe_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option("--type", help="File type"),
    ],
    event_type: Annotated[
        str,
        typer.Option("--event-type", help="Event type to unsubscribe"),
    ],
) -> None:
    _echo_json(
        delete_subscribe_drive_file_service(
            file_token=file_token,
            file_type=file_type,
            event_type=event_type,
        )
    )

@app.command()
def get_subscribe_file(
    file_token: Annotated[
        str,
        typer.Argument(help="Drive file token"),
    ],
    file_type: Annotated[
        DriveFileType,
        typer.Option("--type", help="File type"),
    ],
    event_type: Annotated[
        str,
        typer.Option("--event-type", help="Event type to query"),
    ],
) -> None:
    _echo_json(
        get_subscribe_drive_file_service(
            file_token=file_token,
            file_type=file_type,
            event_type=event_type,
        )
    )
