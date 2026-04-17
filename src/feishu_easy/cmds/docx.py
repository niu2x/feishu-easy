from __future__ import annotations

from typing import Annotated

import json

import typer

from ..services.document_service import create_document as create_document_service
from ..services.document_service import (
    batch_delete_document_block_children as batch_delete_document_block_children_service,
)
from ..services.document_service import (
    get_document_block as get_document_block_service,
)
from ..services.document_service import (
    get_document_block_children as get_document_block_children_service,
)
from ..services.document_service import get_document as get_document_service
from ..services.document_service import (
    list_document_block as list_document_block_service,
)
from ..services.document_service import raw_content as raw_content_service

app = typer.Typer(no_args_is_help=True)


@app.command()
def get_document(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            get_document_service(document_id=document_id),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def raw_content(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
    lang: Annotated[
        int,
        typer.Option("--lang", help="Language code for raw content"),
    ] = 0,
) -> None:
    typer.echo(
        json.dumps(
            raw_content_service(document_id=document_id, lang=lang),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def create_document(
    title: Annotated[
        str,
        typer.Argument(help="New document title"),
    ],
    folder_token: Annotated[
        str,
        typer.Option("--folder-token", help="Target folder token"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            create_document_service(title=title, folder_token=folder_token),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def list_document_block(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
    document_revision_id: Annotated[
        int,
        typer.Option(
            "--document-revision-id",
            help="Document revision ID, use -1 for latest",
        ),
    ] = -1,
) -> None:
    typer.echo(
        json.dumps(
            list_document_block_service(
                document_id=document_id,
                document_revision_id=document_revision_id,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_document_block(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
    block_id: Annotated[
        str,
        typer.Argument(help="Block ID"),
    ],
    document_revision_id: Annotated[
        int,
        typer.Option(
            "--document-revision-id",
            help="Document revision ID, use -1 for latest",
        ),
    ] = -1,
) -> None:
    typer.echo(
        json.dumps(
            get_document_block_service(
                document_id=document_id,
                block_id=block_id,
                document_revision_id=document_revision_id,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_document_block_children(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
    block_id: Annotated[
        str,
        typer.Argument(help="Block ID"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            get_document_block_children_service(document_id, block_id),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def batch_delete_document_block_children(
    document_id: Annotated[
        str,
        typer.Argument(help="Document ID"),
    ],
    block_id: Annotated[
        str,
        typer.Argument(help="Block ID"),
    ],
    start_index: Annotated[
        int,
        typer.Argument(help="Start index (inclusive)"),
    ],
    end_index: Annotated[
        int,
        typer.Argument(help="End index (exclusive)"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            batch_delete_document_block_children_service(
                document_id,
                block_id,
                start_index,
                end_index,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
