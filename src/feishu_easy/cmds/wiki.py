from __future__ import annotations

from typing import Annotated, Literal

import json

import typer

from ..services.wiki_service import (
    create_wiki_space_node as create_wiki_space_node_service,
)
from ..services.wiki_service import get_wiki_space_node as get_wiki_space_node_service
from ..services.wiki_service import get_wiki_space as get_wiki_space_service
from ..services.wiki_service import (
    update_wiki_node_title as update_wiki_node_title_service,
)
from ..services.wiki_service import move_wiki_space_node as move_wiki_space_node_service
from ..services.wiki_service import (
    list_wiki_space_member as list_wiki_space_member_service,
)
from ..services.wiki_service import (
    list_wiki_space_node as list_wiki_space_node_service,
)
from ..services.wiki_service import list_wiki_space as list_wiki_space_service

app = typer.Typer(no_args_is_help=True)
NodeType = Literal["origin", "shortcut"]
WikiNodeObjType = Literal[
    "file",
    "docx",
    "bitable",
    "doc",
    "sheet",
    "mindnote",
    "shortcut",
    "slides",
]

def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

def _require_option(value: str | None, option_name: str, reason: str) -> str:
    if value:
        return value
    raise typer.BadParameter(
        f"{option_name} is required when {reason}",
        param_hint=f"--{option_name}",
    )

def _create_space_node(
    *,
    space_id: int,
    obj_type: WikiNodeObjType,
    parent_node_token: str,
    node_type: NodeType,
    title: str,
    origin_node_token: str = "",
) -> None:
    _echo_json(
        create_wiki_space_node_service(
            space_id=space_id,
            obj_type=obj_type,
            parent_node_token=parent_node_token,
            node_type=node_type,
            origin_node_token=origin_node_token,
            title=title,
        )
    )

@app.command()
def get_space_node(
    node_token: Annotated[
        str,
        typer.Argument(help="Wiki node token"),
    ],
) -> None:
    _echo_json(get_wiki_space_node_service(node_token))

@app.command()
def get_space(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
    lang: Annotated[
        str,
        typer.Option("--lang", help="Language, e.g. zh or en"),
    ] = "zh",
) -> None:
    _echo_json(get_wiki_space_service(space_id=space_id, lang=lang))

@app.command()
def update_node_title(
    node_token: Annotated[
        str,
        typer.Argument(help="Wiki node token"),
    ],
    title: Annotated[
        str,
        typer.Argument(help="New wiki node title"),
    ],
) -> None:
    update_wiki_node_title_service(node_token=node_token, title=title)
    typer.echo("Wiki node title updated successfully", err=True)

@app.command()
def move_space_node(
    node_token: Annotated[
        str,
        typer.Argument(help="Wiki node token to move"),
    ],
    space_id: Annotated[
        int,
        typer.Argument(help="Current wiki space ID"),
    ],
    target_parent_token: Annotated[
        str,
        typer.Option(
            "--target-parent-token",
            help="Target parent node token",
        ),
    ],
    target_space_id: Annotated[
        int | None,
        typer.Option(
            "--target-space-id",
            help="Optional target wiki space ID",
        ),
    ] = None,
) -> None:
    _echo_json(
        move_wiki_space_node_service(
            node_token=node_token,
            space_id=space_id,
            target_parent_token=target_parent_token,
            target_space_id=target_space_id,
        )
    )

@app.command()
def create_space_node_origin(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
    obj_type: Annotated[
        WikiNodeObjType,
        typer.Option(
            "--obj-type",
            help="Node object type: file/docx/bitable/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
    parent_node_token: Annotated[
        str,
        typer.Option("--parent-node-token", help="Parent wiki node token"),
    ],
    title: Annotated[
        str,
        typer.Option("--title", help="New node title"),
    ],
) -> None:
    _create_space_node(
        space_id=space_id,
        obj_type=obj_type,
        parent_node_token=parent_node_token,
        node_type="origin",
        title=title,
    )

@app.command()
def create_space_node_shortcut(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
    obj_type: Annotated[
        WikiNodeObjType,
        typer.Option(
            "--obj-type",
            help="Node object type: file/docx/bitable/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
    parent_node_token: Annotated[
        str,
        typer.Option("--parent-node-token", help="Parent wiki node token"),
    ],
    title: Annotated[
        str,
        typer.Option("--title", help="New node title"),
    ],
    origin_node_token: Annotated[
        str,
        typer.Option("--origin-node-token", help="Origin node token for shortcut"),
    ],
) -> None:
    _create_space_node(
        space_id=space_id,
        obj_type=obj_type,
        parent_node_token=parent_node_token,
        node_type="shortcut",
        title=title,
        origin_node_token=origin_node_token,
    )

@app.command()
def create_space_node(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
    node_type: Annotated[
        NodeType,
        typer.Option("--node-type", help="Node type: origin or shortcut"),
    ],
    obj_type: Annotated[
        WikiNodeObjType,
        typer.Option(
            "--obj-type",
            help="Node object type: file/docx/bitable/doc/sheet/mindnote/shortcut/slides",
        ),
    ],
    parent_node_token: Annotated[
        str,
        typer.Option("--parent-node-token", help="Parent wiki node token"),
    ],
    title: Annotated[
        str,
        typer.Option("--title", help="New node title"),
    ],
    origin_node_token: Annotated[
        str | None,
        typer.Option("--origin-node-token", help="Origin node token for shortcut"),
    ] = None,
) -> None:
    if node_type == "shortcut":
        origin_node_token = _require_option(
            origin_node_token,
            "origin-node-token",
            "node-type is shortcut",
        )

    _create_space_node(
        space_id=space_id,
        obj_type=obj_type,
        parent_node_token=parent_node_token,
        node_type=node_type,
        title=title,
        origin_node_token=origin_node_token or "",
    )

@app.command()
def list_space() -> None:
    _echo_json(list_wiki_space_service())

@app.command()
def list_space_member(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
) -> None:
    _echo_json(list_wiki_space_member_service(space_id=space_id))

@app.command()
def list_space_node(
    space_id: Annotated[
        int,
        typer.Argument(help="Wiki space ID"),
    ],
    parent_node_token: Annotated[
        str | None,
        typer.Option(
            "--parent-node-token", help="Parent wiki node token to filter children"
        ),
    ] = None,
) -> None:
    _echo_json(
        list_wiki_space_node_service(
            space_id=space_id,
            parent_node_token=parent_node_token,
        )
    )
