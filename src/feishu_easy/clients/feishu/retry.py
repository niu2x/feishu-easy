from __future__ import annotations

from typing import Any, Callable

import lark_oapi as lark
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from json import JSONDecodeError
from .errors import FeishuRateLimitError


def before_sleep_log(retry_state: RetryCallState) -> None:
    if retry_state.outcome is None:
        return
    exception = retry_state.outcome.exception()
    if exception is None:
        return
    lark.logger.warning(
        "Retrying Feishu request after error: %s (attempt %s)",
        exception,
        retry_state.attempt_number,
    )


def call_with_retry(
    action: str,
    call: Callable[[], Any],
    *,
    validate_response: Callable[[str, Any], None],
) -> Any:
    @retry(
        stop=stop_after_attempt(16),
        wait=wait_exponential(multiplier=1, min=1, max=120),
        retry=retry_if_exception_type(
            (JSONDecodeError, FeishuRateLimitError, ConnectionError, TimeoutError)
        ),
        before_sleep=before_sleep_log,
        reraise=True,
    )
    def _wrapped_call() -> Any:
        response = call()
        validate_response(action, response)
        return response

    return _wrapped_call()


__all__ = ["call_with_retry", "before_sleep_log"]
