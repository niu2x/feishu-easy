from __future__ import annotations

import sys
from json import dumps
from typing import Literal

import typer

from .commands.board import app as board_app
from .commands.bitable import app as bitable_app
from .commands.contact import app as contact_app
from .commands.doc import app as doc_app
from .commands.docx import app as docx_app
from .commands.drive import app as drive_app
from .commands.flow import app as flow_app
from .commands.im import app as im_app
from .commands.sheets import app as sheets_app
from .commands.wiki import app as wiki_app
from ..services.auth_service import (
    get_tenant_access_token as get_tenant_access_token_service,
)
from ..services.convert_service import (
    convert_from_feishu as convert_from_feishu_service,
)
from .bootstrap import bootstrap_auth, bootstrap_logging

app = typer.Typer(no_args_is_help=True)

@app.callback()
def before_main(
    run_as_user: bool = typer.Option(
        False,
        "--run-as-user",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
) -> None:
    bootstrap_auth(run_as_user)
    bootstrap_logging(log_level)

@app.command()
def get_tenant_access_token() -> None:
    typer.echo(
        dumps(
            get_tenant_access_token_service(),
            indent=2,
            ensure_ascii=False,
        )
    )

app.add_typer(wiki_app, name="wiki")
app.add_typer(board_app, name="board")
app.add_typer(bitable_app, name="bitable")
app.add_typer(contact_app, name="contact")
app.add_typer(drive_app, name="drive")
app.add_typer(doc_app, name="doc")
app.add_typer(docx_app, name="docx")
app.add_typer(flow_app, name="flow")
app.add_typer(sheets_app, name="sheets")
app.add_typer(im_app, name="im")
