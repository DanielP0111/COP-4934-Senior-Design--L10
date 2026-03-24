from contextvars import ContextVar
from typing import Optional

_verified_user_id: ContextVar[Optional[int]] = ContextVar('verified_user_id', default=None)

def set_verified_user_id(user_id: int) -> None:
    _verified_user_id.set(user_id)

def get_verified_user_id() -> Optional[int]:
    return _verified_user_id.get()

def clear_verified_user_id() -> None:
    _verified_user_id.set(None)

