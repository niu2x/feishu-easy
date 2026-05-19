from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ...services.convert_service import (
    get_online_markdown_raw_by_node_token as get_online_markdown_raw_by_node_token_service,
)
from ...services.convert_service import (
    get_online_unified_document_by_node_token as get_online_unified_document_by_node_token_service,
)
from ...services.upload_service import upload_markdown as upload_markdown_service
from ...services.business.user_profile import get_user_profile as get_user_profile_service

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
    document_id, batch_count = upload_markdown_service(
        markdown_file=markdown_file,
        node_token=node_token,
        skip_failed_images=skip_failed_images,
    )

    typer.echo(
        f"Uploaded markdown into document {document_id} in {batch_count} batch(es)",
        err=True,
    )

@app.command("get-markdown")
def get_markdown(
    node_token: Annotated[
        str,
        typer.Argument(help="Feishu wiki node_token"),
    ],
    expand_board: Annotated[
        bool,
        typer.Option(
            "--expand-board/--no-expand-board",
            help="Expand docx board blocks (currently supports mind map)",
        ),
    ] = False,
    expand_sheets: Annotated[
        bool,
        typer.Option(
            "--expand-sheets/--no-expand-sheets",
            help="Expand docx sheet blocks into tables",
        ),
    ] = False,
    expand_bitable: Annotated[
        bool,
        typer.Option(
            "--expand-bitable/--no-expand-bitable",
            help="Expand docx bitable blocks into tables",
        ),
    ] = False,
) -> None:
    typer.echo(
        get_online_markdown_raw_by_node_token_service(
            node_token=node_token,
            expand_board=expand_board,
            expand_sheets=expand_sheets,
            expand_bitable=expand_bitable,
        )
    )

@app.command("get-unified")
def get_unified(
    node_token: Annotated[
        str,
        typer.Argument(help="Feishu wiki node_token"),
    ],
    expand_board: Annotated[
        bool,
        typer.Option(
            "--expand-board/--no-expand-board",
            help="Expand docx board blocks (currently supports mind map)",
        ),
    ] = False,
    expand_sheets: Annotated[
        bool,
        typer.Option(
            "--expand-sheets/--no-expand-sheets",
            help="Expand docx sheet blocks into tables",
        ),
    ] = False,
    expand_bitable: Annotated[
        bool,
        typer.Option(
            "--expand-bitable/--no-expand-bitable",
            help="Expand docx bitable blocks into tables",
        ),
    ] = False,
) -> None:
    unified_document = get_online_unified_document_by_node_token_service(
        node_token=node_token,
        expand_board=expand_board,
        expand_sheets=expand_sheets,
        expand_bitable=expand_bitable,
    )
    typer.echo(json.dumps(unified_document.model_dump(), indent=2, ensure_ascii=False))

@app.command("get-user-profile")
def get_user_profile_cmd(
    open_id: Annotated[
        str,
        typer.Argument(help="User open_id"),
    ],
) -> None:
    profile = get_user_profile_service(open_id)
    typer.echo(json.dumps({"name": profile.name, "email": profile.email}, indent=2, ensure_ascii=False))
