from __future__ import annotations

from typing import Annotated, Literal

import json

import typer

from ...services.contact_service import batch_get_user as batch_get_user_service
from ...services.contact_service import basic_batch_get_user as basic_batch_get_user_service
from ...services.contact_service import get_user as get_user_service

app = typer.Typer(no_args_is_help=True)

UserIdType = Literal["open_id", "user_id", "union_id"]
DepartmentIdType = Literal["open_department_id", "department_id"]

def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

@app.command("batch-get-user")
def batch_get_user_cmd(
    user_ids: Annotated[
        list[str],
        typer.Option("--user-id", help="User ID, can be specified multiple times"),
    ],
    user_id_type: Annotated[
        UserIdType,
        typer.Option("--user-id-type", help="User ID type"),
    ] = "open_id",
) -> None:
    _echo_json(
        batch_get_user_service(user_ids=user_ids, user_id_type=user_id_type)
    )

@app.command("basic-batch-get-user")
def basic_batch_get_user_cmd(
    user_ids: Annotated[
        list[str],
        typer.Option("--user-id", help="User ID, can be specified multiple times"),
    ],
    user_id_type: Annotated[
        UserIdType,
        typer.Option("--user-id-type", help="User ID type"),
    ] = "open_id",
) -> None:
    _echo_json(
        basic_batch_get_user_service(user_ids=user_ids, user_id_type=user_id_type)
    )

@app.command("get-user")
def get_user_cmd(
    user_id: Annotated[
        str,
        typer.Option("--user-id", help="User ID"),
    ],
    user_id_type: Annotated[
        UserIdType,
        typer.Option("--user-id-type", help="User ID type"),
    ] = "open_id",
    department_id_type: Annotated[
        DepartmentIdType,
        typer.Option("--department-id-type", help="Department ID type"),
    ] = "open_department_id",
) -> None:
    _echo_json(
        get_user_service(
            user_id=user_id, user_id_type=user_id_type, department_id_type=department_id_type
        )
    )
