from __future__ import annotations

from feishu_easy.services.auth_service import get_tenant_access_token
from feishu_easy.services.doc_service import get_doc_content

class _FakeDocAPI:
    def get_doc_content(self, *, obj_token: str) -> str:
        return f"doc:{obj_token}"

class _FakeAPI:
    def __init__(self) -> None:
        self.doc = _FakeDocAPI()

    def get_tenant_access_token(self) -> dict[str, int]:
        return {"code": 0}

def test_auth_service_accepts_injected_api() -> None:
    payload = get_tenant_access_token(api=_FakeAPI())
    assert payload["code"] == 0

def test_doc_service_accepts_injected_api() -> None:
    content = get_doc_content("tok_001", api=_FakeAPI())
    assert content == "doc:tok_001"
