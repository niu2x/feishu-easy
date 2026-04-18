from __future__ import annotations


class FeishuClientError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        action: str | None = None,
        code: int | None = None,
        log_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.action = action
        self.code = code
        self.log_id = log_id


class FeishuAPIError(FeishuClientError):
    pass


class FeishuHTTPError(FeishuClientError):
    pass


class FeishuAuthError(FeishuClientError):
    pass


class FeishuResponseError(FeishuClientError):
    pass


class FeishuRateLimitError(FeishuAPIError):
    pass


__all__ = [
    "FeishuClientError",
    "FeishuAPIError",
    "FeishuHTTPError",
    "FeishuAuthError",
    "FeishuResponseError",
    "FeishuRateLimitError",
]
