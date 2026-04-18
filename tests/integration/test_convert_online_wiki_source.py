from __future__ import annotations

import json

import pytest

from feishu_easy.services.convert_service import (
    get_online_wiki_node_source_by_node_token,
)
from feishu_easy.services.errors import ServiceValidationError


class _FakeWikiAPI:
    def __init__(self, node: dict[str, object]) -> None:
        self._node = node

    def get_node(self, _: str) -> dict[str, object]:
        return self._node


class _FakeDocxAPI:
    def list_document_block(
        self,
        *,
        document_id: str,
        document_revision_id: int,
    ) -> dict[str, list[dict[str, str]]]:
        assert document_id == "docx_token"
        assert document_revision_id == -1
        return {"items": [{"block_id": "blk_1"}]}


class _FakeAPI:
    def __init__(self, node: dict[str, object]) -> None:
        self.wiki = _FakeWikiAPI(node)
        self.docx = _FakeDocxAPI()


def test_docx_wiki_node_source_with_mocked_api() -> None:
    source = get_online_wiki_node_source_by_node_token(
        "node_1",
        api=_FakeAPI(
            {
                "obj_type": "docx",
                "obj_token": "docx_token",
                "title": "Demo",
            }
        ),
    )

    payload = json.loads(source["payload"])
    assert source["obj_type"] == "docx"
    assert payload["node"]["obj_type"] == "docx"
    assert payload["obj"] == [{"block_id": "blk_1"}]


def test_unsupported_wiki_node_source_with_mocked_api() -> None:
    with pytest.raises(ServiceValidationError):
        get_online_wiki_node_source_by_node_token(
            "node_2",
            api=_FakeAPI(
                {
                    "obj_type": "slides",
                    "obj_token": "slides_token",
                }
            ),
        )
