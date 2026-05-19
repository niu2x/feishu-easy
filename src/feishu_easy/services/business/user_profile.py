from __future__ import annotations

from dataclasses import dataclass

from ...feishu_api import FeishuAPI

_cache: dict[str, UserProfile] = {}

@dataclass
class UserProfile:
    name: str
    email: str | None

def get_user_profile(
    open_id: str,
    *,
    api: FeishuAPI | None = None,
) -> UserProfile:
    cached = _cache.get(open_id)
    if cached is not None:
        return cached

    if api is None:
        api = FeishuAPI()
    data = api.contact.get_user(
        user_id=open_id,
        user_id_type="open_id",
    )
    user = data.get("user", {})
    profile = UserProfile(
        name=user.get("name", ""),
        email=user.get("email"),
    )
    _cache[open_id] = profile
    return profile
