from __future__ import annotations

from pathlib import Path
from typing import Annotated

import json

import typer

from ..services.board_service import (
    download_whiteboard_as_image,
    list_whiteboard_node as list_whiteboard_node_service,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def list_whiteboard_node(
    whiteboard_id: Annotated[
        str,
        typer.Argument(help="Whiteboard id"),
    ],
    user_id_type: Annotated[
        str,
        typer.Option("--user-id-type", help="User id type"),
    ] = "open_id",
) -> None:
    typer.echo(
        json.dumps(
            list_whiteboard_node_service(
                whiteboard_id=whiteboard_id,
                user_id_type=user_id_type,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def download_as_image(
    whiteboard_id: Annotated[
        str,
        typer.Argument(help="Whiteboard id"),
    ],
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Directory to store downloaded image"),
    ] = Path("."),
    file_name: Annotated[
        str | None,
        typer.Option("--file-name", help="Override saved file name"),
    ] = None,
) -> None:
    typer.echo(
        json.dumps(
            download_whiteboard_as_image(
                whiteboard_id=whiteboard_id,
                output_dir=output_dir,
                file_name=file_name,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
