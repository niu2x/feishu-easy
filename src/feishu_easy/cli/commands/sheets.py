from __future__ import annotations

from typing import Annotated

import json

import typer

from ...services.sheets_service import (
    create_spreadsheet as create_spreadsheet_service,
    get_sheet_content as get_sheet_content_service,
    get_spreadsheet_metainfo as get_spreadsheet_metainfo_service,
    get_spreadsheet as get_spreadsheet_service,
    get_spreadsheet_sheet as get_spreadsheet_sheet_service,
    get_sheet_values as get_sheet_values_service,
    query_spreadsheet_sheet as query_spreadsheet_sheet_service,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def get_spreadsheet_sheet(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
    sheet_id: Annotated[
        str,
        typer.Argument(help="Sheet id"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            get_spreadsheet_sheet_service(
                spreadsheet_token=spreadsheet_token,
                sheet_id=sheet_id,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def query_spreadsheet_sheet(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            query_spreadsheet_sheet_service(spreadsheet_token=spreadsheet_token),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_spreadsheet(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    typer.echo(
        json.dumps(
            get_spreadsheet_service(
                spreadsheet_token=spreadsheet_token,
                user_id_type=user_id_type,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_spreadsheet_metainfo(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
    ext_fields: Annotated[
        str | None,
        typer.Option(
            "--ext-fields",
            help="Extra fields, e.g. protectedRange",
        ),
    ] = None,
    user_id_type: Annotated[
        str | None,
        typer.Option("--user-id-type", help="User id type, e.g. open_id"),
    ] = None,
) -> None:
    typer.echo(
        json.dumps(
            get_spreadsheet_metainfo_service(
                spreadsheet_token=spreadsheet_token,
                ext_fields=ext_fields,
                user_id_type=user_id_type,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def create_spreadsheet(
    title: Annotated[
        str,
        typer.Argument(help="Spreadsheet title"),
    ],
    folder_token: Annotated[
        str | None,
        typer.Option("--folder-token", help="Target folder token"),
    ] = None,
) -> None:
    typer.echo(
        json.dumps(
            create_spreadsheet_service(title=title, folder_token=folder_token),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_sheet_values(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
    value_range: Annotated[
        str,
        typer.Argument(help="Range, e.g. Sheet1!A1:B2"),
    ],
    value_render_option: Annotated[
        str | None,
        typer.Option("--value-render-option", help="valueRenderOption"),
    ] = None,
    date_time_render_option: Annotated[
        str | None,
        typer.Option(
            "--date-time-render-option",
            help="dateTimeRenderOption",
        ),
    ] = None,
) -> None:
    typer.echo(
        json.dumps(
            get_sheet_values_service(
                spreadsheet_token=spreadsheet_token,
                value_range=value_range,
                value_render_option=value_render_option,
                date_time_render_option=date_time_render_option,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def get_sheet_content(
    spreadsheet_token: Annotated[
        str,
        typer.Argument(help="Spreadsheet token"),
    ],
    sheet_id: Annotated[
        str,
        typer.Argument(help="Sheet id"),
    ],
) -> None:
    typer.echo(
        json.dumps(
            get_sheet_content_service(
                spreadsheet_token=spreadsheet_token,
                sheet_id=sheet_id,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
