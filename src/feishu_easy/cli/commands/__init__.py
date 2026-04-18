from __future__ import annotations

from .bitable import app as bitable_app
from .board import app as board_app
from .doc import app as doc_app
from .docx import app as docx_app
from .drive import app as drive_app
from .flow import app as flow_app
from .sheets import app as sheets_app
from .wiki import app as wiki_app

__all__ = [
    "bitable_app",
    "board_app",
    "doc_app",
    "docx_app",
    "drive_app",
    "flow_app",
    "sheets_app",
    "wiki_app",
]
