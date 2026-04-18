from __future__ import annotations

class ServiceError(RuntimeError):
    pass

class ServiceValidationError(ValueError):
    pass

__all__ = ["ServiceError", "ServiceValidationError"]
