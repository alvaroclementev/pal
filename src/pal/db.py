"""Database related functions"""
from __future__ import annotations

import datetime
import pathlib
import sqlite3
from collections import namedtuple

from pal import setup
from pal.utils import dates


# Register the adapters and converters
def adapt_datetime(value: datetime.datetime) -> str:
    """Transform a timestamp into a ISO 8601 string.

    If the value does not have a timezone, the local timezone is assumed.
    """
    return dates.dt_make_aware(value).isoformat()


def convert_datetime(value: bytes) -> datetime.datetime:
    """Convert a string representing a datetime in the DB into a datetime"""
    return datetime.datetime.fromisoformat(value.decode())


sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


def namedtuple_factory(cursor, row):
    """Wrap the result of a `sqlite3` statement into a `Row` namedtuple"""
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)


def get_connection(path: str | pathlib.Path | None = None) -> sqlite3.Connection:
    """Get a `sqlite3.Connection` to the default database"""
    db_path = path or setup.default_db_path()
    con = sqlite3.connect(str(db_path))
    con.row_factory = namedtuple_factory
    return con
