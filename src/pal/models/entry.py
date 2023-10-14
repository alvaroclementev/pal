"""Entry related DB models"""
from __future__ import annotations

import datetime
import sqlite3
from dataclasses import dataclass
from typing import Optional

from pal import utils


@dataclass
class Entry:
    text: str
    author: str
    project: str
    timestamp: datetime.datetime
    # Fields that are filled automatically during DB insertion
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


def insert_entry(con: sqlite3.Connection, entry: Entry) -> Entry:
    """Get the current entry and inserts it into the database"""

    # Prepare the common logic
    now = utils.current_time()
    is_creation = entry.id is None

    if is_creation:
        # The entry will be INSERTed, so the need to set the `created_at`
        created_at = now
    # Set the updated_at
    updated_at = now

    with con:
        cur = con.execute(
            """INSERT INTO entry(text, author, project, timestamp, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                entry.text,
                entry.author,
                entry.project,
                entry.timestamp,
                created_at,
                updated_at,
            ),
        )
        assert cur.lastrowid is not None, "The last rowid must exist"
        # Retrieve the inserted entry, with the DB fields filled
        entry = find_by_rowid(con, cur.lastrowid)
    return entry


def find_by_id(con: sqlite3.Connection, id: int) -> Entry:
    """Find an Entry by id"""
    cur = con.cursor()
    cur.execute("SELECT * FROM entry WHERE id = ?", (id,))
    row = cur.fetchone()
    return Entry(**row._asdict())


def find_by_rowid(con: sqlite3.Connection, rowid: int) -> Entry:
    """Find an Entry by rowid"""
    cur = con.cursor()
    cur.execute("SELECT * FROM entry WHERE _rowid_ = ?", (rowid,))
    row = cur.fetchone()
    return Entry(**row._asdict())


def find_entries(
    con: sqlite3.Connection, *, author: str, project: str, n: Optional[int] = None
) -> list[Entry]:
    """Find the all the entries for a given project"""
    cur = con.cursor()
    query = "SELECT * FROM entry WHERE author = ? AND project = ?"
    params = [author, project]
    if n is not None:
        query += " LIMIT ?"
        params.append(str(n))
    cur.execute(query, params)
    rows = cur.fetchall()
    # Transform into an Entry instance
    # TODO(alvaro): Use the builtin methods for automatically converting the results
    # into an Entry instance (see converters)
    entries = [Entry(**row._asdict()) for row in rows]
    return entries
