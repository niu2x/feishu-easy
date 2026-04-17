from __future__ import annotations

import json
from typing import Annotated

import typer

from ..services.bitable_service import (
    get_app_table_view as get_app_table_view_service,
    get_app as get_app_service,
    list_app_table_field as list_app_table_field_service,
    list_app_table as list_app_table_service,
    list_app_table_view as list_app_table_view_service,
    search_app_table_record as search_app_table_record_service,
)

app = typer.Typer(no_args_is_help=True)

@app.command()
def get_app(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    payload = get_app_service(
        app_token=app_token,
        user_id_type=user_id_type,
    )
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

@app.command()
def list_app_table(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
) -> None:
    payload = list_app_table_service(app_token=app_token)
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

@app.command()
def list_app_table_field(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
    table_id: Annotated[
        str,
        typer.Argument(help="Bitable table id"),
    ],
    view_id: Annotated[
        str | None,
        typer.Option("--view-id", help="Optional Bitable view id"),
    ] = None,
    text_field_as_array: Annotated[
        bool | None,
        typer.Option(
            "--text-field-as-array/--no-text-field-as-array",
            help="Return text field value as array when supported",
        ),
    ] = None,
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    payload = list_app_table_field_service(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        text_field_as_array=text_field_as_array,
        user_id_type=user_id_type,
    )
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

@app.command()
def list_app_table_view(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
    table_id: Annotated[
        str,
        typer.Argument(help="Bitable table id"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    payload = list_app_table_view_service(
        app_token=app_token,
        table_id=table_id,
        user_id_type=user_id_type,
    )
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

@app.command()
def get_app_table_view(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
    table_id: Annotated[
        str,
        typer.Argument(help="Bitable table id"),
    ],
    view_id: Annotated[
        str,
        typer.Argument(help="Bitable view id"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    payload = get_app_table_view_service(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        user_id_type=user_id_type,
    )
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

@app.command()
def search_app_table_record(
    app_token: Annotated[
        str,
        typer.Argument(help="Bitable app token"),
    ],
    table_id: Annotated[
        str,
        typer.Argument(help="Bitable table id"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    payload = search_app_table_record_service(
        app_token=app_token,
        table_id=table_id,
        user_id_type=user_id_type,
    )
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
