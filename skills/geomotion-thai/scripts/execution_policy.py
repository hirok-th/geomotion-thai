"""Production is opt-in. Package installation/checks never authorize media work."""

from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps

_ACTIVE = ContextVar("geomotion_media_authorized", default=False)


class MediaProductionDisabled(RuntimeError):
    pass


def require_media():
    if not _ACTIVE.get():
        raise MediaProductionDisabled(
            "Media production is disabled. Use --produce-media only after an explicit user request to create a clip; package/check/install requests do not authorize it."
        )


def enable_cli_production(authorized):
    if authorized is not True:
        raise MediaProductionDisabled(
            "Media production is disabled; --produce-media is required after an explicit user clip request."
        )
    _ACTIVE.set(True)


@contextmanager
def production_request(authorized=False):
    if authorized is not True:
        raise MediaProductionDisabled(
            "Media production is disabled; an explicit user clip request is required."
        )
    token = _ACTIVE.set(True)
    try:
        yield
    finally:
        _ACTIVE.reset(token)


def production_only(func):
    @wraps(func)
    def guarded(*args, **kwargs):
        require_media()
        return func(*args, **kwargs)

    return guarded
