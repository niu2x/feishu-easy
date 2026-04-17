from __future__ import annotations

import logging
import os

import typer
from dotenv import load_dotenv

from ..config import configure_feishu_api_from_env
from ..feishu_api import FeishuAPI

def bootstrap_auth(run_as_user: bool) -> None:
    load_dotenv()

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")

    if run_as_user:

        user_access_token = _auth.ensure_scopes(
            ["docx:document.block:convert"], open_browser=True, token=None
        )
        FeishuAPI.configure_defaults(
            app_id=app_id,
            user_access_token=user_access_token,
        )
        return

    if not app_id:
        raise typer.BadParameter(
            "FEISHU_APP_ID is required",
            param_hint="environment variables",
        )
    if not app_secret:
        raise typer.BadParameter(
            "FEISHU_APP_SECRET is required",
            param_hint="environment variables",
        )

    configure_feishu_api_from_env()

def bootstrap_logging(log_level_name: str) -> None:
    normalized_level = log_level_name.upper()
    if not hasattr(logging, normalized_level):
        raise typer.BadParameter(
            f"Invalid log level: {log_level_name}",
            param_hint="--log-level",
        )

    log_level = getattr(logging, normalized_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
