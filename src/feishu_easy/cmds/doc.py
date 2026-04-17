from __future__ import annotations

from typing import Annotated

import typer

from ..services.doc_service import get_doc_content as get_doc_content_service

app = typer.Typer(no_args_is_help=True)


@app.command()
def get_content(
    obj_token: Annotated[
        str,
        typer.Argument(help="Doc object token"),
    ],
) -> None:
    typer.echo(get_doc_content_service(obj_token=obj_token))
