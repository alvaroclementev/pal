"""Entry related DB models"""
from __future__ import annotations

import datetime
import sqlite3
from dataclasses import asdict, dataclass
from typing import Optional

from pal.utils import dates


@dataclass
class Entry:
    text: str
    author: str
    project: str
    timestamp: datetime.datetime
    reported: bool = False
    # Fields that are filled automatically during DB insertion
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    def to_json(self, include_id: bool = True) -> dict:
        result = asdict(self)

        # Convert datetimes to strings
        result["timestamp"] = result["timestamp"].isoformat()
        result["created_at"] = (
            result["created_at"].isoformat() if result["created_at"] else None
        )
        result["updated_at"] = (
            result["updated_at"].isoformat() if result["updated_at"] else None
        )

        if not include_id:
            del result["id"]

        return result

    def __post_init__(self):
        # Since SQLite does not store dates natively, when one is read we need to make
        # sure we transform it
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.datetime.fromisoformat(self.timestamp)
        if isinstance(self.created_at, str):
            self.created_at = datetime.datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.datetime.fromisoformat(self.updated_at)


def insert_entry(con: sqlite3.Connection, entry: Entry) -> Entry:
    """Get the current entry and inserts it into the database"""

    # Prepare the common logic
    now = dates.current_time()
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
    con: sqlite3.Connection,
    *,
    author: str,
    project: str,
    n: Optional[int] = None,
    include_reported: bool = False,
) -> list[Entry]:
    """Find the all the entries for a given project"""
    cur = con.cursor()
    query = "SELECT * FROM entry WHERE author = ? AND project = ? {filter} ORDER BY timestamp DESC {limit}"
    params = [author, project]

    include_reported_fmt = "" if include_reported else "AND reported = 0"

    if n is not None:
        limit_fmt = " LIMIT ?"
        params.append(str(n))
    else:
        limit_fmt = ""

    query = query.format(filter=include_reported_fmt, limit=limit_fmt)

    cur.execute(query, params)
    rows = cur.fetchall()
    # Transform into an Entry instance
    # TODO(alvaro): Use the builtin methods for automatically converting the results
    # into an Entry instance (see converters)
    entries = [Entry(**row._asdict()) for row in rows]
    return entries


def delete_entries(
    con: sqlite3.Connection, *, author: str, project: Optional[str]
) -> int:
    """Delete all the rows in the entry table that match the given author and project.

    If `project` is `None`, it will delete the rows for all the projects
    """

    query = "DELETE FROM entry WHERE author = ?"
    params = [author]
    if project is not None:
        query += " AND project = ?"
        params.append(project)

    with con:
        cur = con.execute(query, params)
        n = cur.rowcount
    return int(n)


def report_entries(
    con: sqlite3.Connection, *, author: str, project: Optional[str]
) -> int:
    """Mark all the rows in the entry table that match the given author and project as
    reported.

    If `project` is `None`, it affect all entries for the given author
    """

    query = "UPDATE entry SET reported = 1 WHERE reported = 0 AND author = ?"
    params = [author]
    if project is not None:
        query += " AND project = ?"
        params.append(project)

    with con:
        cur = con.execute(query, params)
        n = cur.rowcount
    return int(n)
