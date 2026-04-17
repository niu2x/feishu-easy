from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ..services.upload_service import upload_markdown as upload_markdown_service

app = typer.Typer(no_args_is_help=True)

@app.command()
def upload_markdown(
    markdown_file: Annotated[
        Path,
        typer.Argument(help="Local markdown file path"),
    ],
    node_token: Annotated[
        str,
        typer.Argument(help="Target wiki node token"),
    ],
    skip_failed_images: Annotated[
        bool,
        typer.Option(
            "--skip-failed-images/--no-skip-failed-images",
            help="Skip failed image downloads instead of raising error",
        ),
    ] = False,
) -> None:
    try:
        document_id, batch_count = upload_markdown_service(
            markdown_file=markdown_file,
            node_token=node_token,
            skip_failed_images=skip_failed_images,
        )
    except FileNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Uploaded markdown into document {document_id} in {batch_count} batch(es)",
        err=True,
    )
