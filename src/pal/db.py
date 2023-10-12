"""Database related functions"""
from __future__ import annotations

import pathlib
import sqlite3
from collections import namedtuple

from pal import setup


def namedtuple_factory(cursor, row):
    """Wrap the result of a `sqlite3` statement into a `Row` namedtuple"""
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)


def get_connection(path: str | pathlib.Path | None) -> sqlite3.Connection:
    """Get a `sqlite3.Connection` to the default database"""
    db_path = path or setup.default_db_path()
    con = sqlite3.connect(str(db_path))
    con.row_factory = namedtuple_factory
    return con
