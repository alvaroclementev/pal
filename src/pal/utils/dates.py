"""General utility functions used across the project"""
from __future__ import annotations

import datetime
from typing import Optional


def current_time() -> datetime.datetime:
    """Return the current time with local timezone information"""
    return datetime.datetime.now().astimezone()


def local_timezone() -> datetime.timezone:
    """Return the `tzinfo` object representing the local timezone"""
    return current_time().tzinfo  # type: ignore


def dt_is_aware(dt: datetime.datetime) -> bool:
    """Return `True` if the timezone is aware"""

    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def dt_make_aware(
    dt: datetime.datetime, tz: Optional[datetime.timezone] = None
) -> datetime.datetime:
    """Make sure the `dt` is localized, and if it's not, localize it to the given `tz`
    or the local timezone (by default)
    """
    if dt_is_aware(dt):
        return dt

    tz = tz or local_timezone()
    return dt.replace(tzinfo=tz)
