from __future__ import annotations

from typing import Annotated, Literal

import json

import typer

from ...services.im_service import get_chat as get_chat_service
from ...services.im_service import list_all_messages as list_all_messages_service

app = typer.Typer(no_args_is_help=True)

ContainerIdType = Literal["chat", "thread"]
SortType = Literal["ByCreateTimeAsc", "ByCreateTimeDesc"]
UserIdType = Literal["open_id", "user_id", "union_id"]

def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

@app.command("get-chat")
def get_chat_cmd(
    chat_id: Annotated[
        str,
        typer.Option("--chat-id", help="Chat ID"),
    ],
    user_id_type: Annotated[
        UserIdType,
        typer.Option("--user-id-type", help="User ID type"),
    ] = "open_id",
) -> None:
    _echo_json(get_chat_service(chat_id=chat_id, user_id_type=user_id_type))

@app.command("list")
def list_messages(
    container_id: Annotated[
        str,
        typer.Option("--container-id", help="Container ID (chat_id or thread_id)"),
    ],
    container_id_type: Annotated[
        ContainerIdType,
        typer.Option(
            "--container-id-type",
            help="Container type: chat or thread",
        ),
    ] = "chat",
    start_time: Annotated[
        str | None,
        typer.Option("--start-time", help="Start time in seconds (epoch)"),
    ] = None,
    end_time: Annotated[
        str | None,
        typer.Option("--end-time", help="End time in seconds (epoch)"),
    ] = None,
    sort_type: Annotated[
        SortType | None,
        typer.Option("--sort-type", help="Sort order: ByCreateTimeAsc or ByCreateTimeDesc"),
    ] = None,
    page_size: Annotated[
        int,
        typer.Option("--page-size", help="Page size (1-50)"),
    ] = 50,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Max number of messages to return"),
    ] = None,
) -> None:
    _echo_json(
        list_all_messages_service(
            container_id_type=container_id_type,
            container_id=container_id,
            start_time=start_time,
            end_time=end_time,
            sort_type=sort_type,
            page_size=page_size,
            limit=limit,
        )
    )
