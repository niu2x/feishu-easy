from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import json

import typer

from ...services.board_service import (
    create_plantuml_whiteboard_node as create_plantuml_whiteboard_node_service,
    download_whiteboard_as_image,
    list_whiteboard_node as list_whiteboard_node_service,
)

app = typer.Typer(no_args_is_help=True)

def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

@app.command()
def create_plantuml_node(
    whiteboard_id: Annotated[
        str,
        typer.Argument(help="Whiteboard id"),
    ],
    plant_uml_code: Annotated[
        str | None,
        typer.Option(
            "--code",
            "--plant-uml-code",
            help="Diagram source code (PlantUML or Mermaid)",
        ),
    ] = None,
    plant_uml_file: Annotated[
        Path | None,
        typer.Option(
            "--file",
            "--plant-uml-file",
            help="Path to diagram source file (PlantUML or Mermaid)",
        ),
    ] = None,
    syntax: Annotated[
        Literal["plantuml", "mermaid"],
        typer.Option(
            "--syntax",
            help="Diagram syntax type",
            case_sensitive=False,
        ),
    ] = "plantuml",
    style: Annotated[
        Literal["board", "classic"],
        typer.Option(
            "--style",
            help="Render style: board(可编辑节点) or classic(图片)",
            case_sensitive=False,
        ),
    ] = "board",
    style_type: Annotated[
        int | None,
        typer.Option(
            "--style-type",
            help="Raw API value override for style type (1/2)",
        ),
    ] = None,
    syntax_type: Annotated[
        int | None,
        typer.Option(
            "--syntax-type",
            help="Raw API value override for syntax type (1/2)",
        ),
    ] = None,
    diagram_type: Annotated[
        int | None,
        typer.Option("--diagram-type", help="PlantUML diagram type, refer to Feishu API"),
    ] = None,
    overwrite: Annotated[
        bool | None,
        typer.Option("--overwrite", help="Whether to overwrite existing node"),
    ] = None,
    parse_mode: Annotated[
        int | None,
        typer.Option("--parse-mode", help="Parse mode, refer to Feishu API"),
    ] = None,
) -> None:
    if (plant_uml_code is None) == (plant_uml_file is None):
        raise typer.BadParameter(
            "Exactly one of --code or --file must be provided",
            param_hint="--code/--file",
        )

    resolved_plant_uml_code = plant_uml_code
    if plant_uml_file is not None:
        if not plant_uml_file.exists():
            raise typer.BadParameter(
                f"File not found: {plant_uml_file}",
                param_hint="--plant-uml-file",
            )
        if not plant_uml_file.is_file():
            raise typer.BadParameter(
                f"Not a regular file: {plant_uml_file}",
                param_hint="--plant-uml-file",
            )
        resolved_plant_uml_code = plant_uml_file.read_text(encoding="utf-8")

    if resolved_plant_uml_code is None or not resolved_plant_uml_code.strip():
        raise typer.BadParameter(
            "Diagram source code must not be empty",
            param_hint="--code/--file",
        )

    resolved_syntax_type = syntax_type
    if resolved_syntax_type is None:
        resolved_syntax_type = 1 if syntax.lower() == "plantuml" else 2

    resolved_style_type = style_type
    if resolved_style_type is None:
        resolved_style_type = 1 if style.lower() == "board" else 2

    resolved_diagram_type = diagram_type
    if resolved_diagram_type is None and resolved_syntax_type == 2:
        resolved_diagram_type = 0

    if resolved_syntax_type == 2 and resolved_style_type == 2:
        raise typer.BadParameter(
            "Mermaid does not support classic style; use --style board",
            param_hint="--style",
        )

    _echo_json(
        create_plantuml_whiteboard_node_service(
            whiteboard_id=whiteboard_id,
            plant_uml_code=resolved_plant_uml_code,
            style_type=resolved_style_type,
            syntax_type=resolved_syntax_type,
            diagram_type=resolved_diagram_type,
            overwrite=overwrite,
            parse_mode=parse_mode,
        )
    )

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
    _echo_json(
        list_whiteboard_node_service(
            whiteboard_id=whiteboard_id,
            user_id_type=user_id_type,
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
    _echo_json(
        download_whiteboard_as_image(
            whiteboard_id=whiteboard_id,
            output_dir=output_dir,
            file_name=file_name,
        )
    )
