from __future__ import annotations

import os

def configure_feishu_api_from_env(*, required: bool = False) -> None:
    from .feishu_api import FeishuAPI

    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")

    if required:
        if not app_id:
            raise RuntimeError("FEISHU_APP_ID environment variable is required")
        if not app_secret:
            raise RuntimeError("FEISHU_APP_SECRET environment variable is required")

    if app_id and app_secret:
        FeishuAPI.configure_defaults(app_id=app_id, app_secret=app_secret)
