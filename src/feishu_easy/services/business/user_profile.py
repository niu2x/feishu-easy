from __future__ import annotations

import logging
from dataclasses import dataclass

from ...feishu_api import FeishuAPI

_cache: dict[str, UserProfile] = {}

_logger = logging.getLogger(__name__)

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

    try:
        data = api.contact.get_user(
            user_id=open_id,
            user_id_type="open_id",
        )
        user = data.get("user", {})
        profile = UserProfile(
            name=user.get("name", ""),
            email=user.get("email"),
        )
    except Exception as exc:
        _logger.warning("get_user failed for %s, falling back to basic_batch_get_user: %s", open_id, exc)
        data = api.contact.basic_batch_get_user(
            user_ids=[open_id],
            user_id_type="open_id",
        )
        users = data.get("users", [])
        user = users[0] if users else {}
        profile = UserProfile(
            name=user.get("name", ""),
            email=None,
        )

    _cache[open_id] = profile
    return profile
