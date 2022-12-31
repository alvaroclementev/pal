from __future__ import annotations

import datetime
import json
from typing import Optional

import typer
from pydantic import BaseModel, parse_obj_as
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

PALFILE_PATH = ".pal"
AUTHOR_ENV_VAR = "PAL_AUTHOR"
TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"


class EntryAlreadyExists(Exception):
    pass


class PalDB:
    """Represents the database of PAL entries"""

    entries: dict[int, Entry]

    def __init__(self, entries: list[Entry]):
        self.entries = {e.id: e for e in sorted(entries, key=lambda x: x.id)}

    def add_entry(self, entry: Entry):
        if entry.id in self.entries:
            raise EntryAlreadyExists()
        self.entries[entry.id] = entry

    def make_entry(self, header: str, body: str, author: str) -> Entry:
        next_id = self._next_id()
        entry = Entry.create(id=next_id, header=header, body=body, author=author)
        return entry

    @classmethod
    def load(cls, path: str = PALFILE_PATH) -> PalDB:
        with open(path) as f:
            lines = f.readlines()

        parsed = [json.loads(line) for line in lines]
        entries = parse_obj_as(list[Entry], parsed)
        return PalDB(entries)

    def write(self, path: str = PALFILE_PATH):
        lines = [e.json() for e in self.entries.values()]
        with open(path, "w") as f:
            for line in lines:
                f.write(f"{line}\n")

    def _next_id(self):
        return (max(key for key in self.entries.keys()) if self.entries else 0) + 1

    def __repr__(self) -> str:
        return f"PalDB(entries={self.entries!r})"


class Entry(BaseModel):
    """An entry from the PAL log"""

    id: int
    author: str
    timestamp: datetime.datetime
    header: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def create(cls, id: int, header: str, body: str, author: str) -> Entry:
        now = datetime.datetime.now()
        return cls(
            id=id,
            author=author,
            timestamp=now,
            header=header,
            body=body,
            created_at=now,
            updated_at=now,
        )


@app.command()
def add(
    header: str = typer.Option(..., "-h", "--header"),
    body: str = typer.Option("", "-b", "--body"),
    author: str = typer.Option(..., "-a", "--author", envvar=AUTHOR_ENV_VAR),
):
    console.print("Executing [green]add[/green]")
    db = PalDB.load()
    console.print(f"Before {db}")

    # Create a new entry
    entry = db.make_entry(author=author, header=header, body=body)
    db.add_entry(entry)
    console.print(f"After {db}")
    db.write()


@app.command()
def log(limit: Optional[int] = typer.Option(None, "-l", "--limit")):
    db = PalDB.load()
    table = Table(title="Personal Activity Log")

    # Prepare the columns
    table.add_column("Timestamp", justify="right", style="cyan", no_wrap=True)
    table.add_column("Header", justify="left", style="orange1")
    table.add_column("Body", justify="right", overflow="ellipsis")

    entries = sorted(db.entries.values(), key=lambda x: x.timestamp, reverse=True)
    if limit is not None:
        entries = entries[:limit]
    # Prepare the rows
    for entry in entries:
        # Timestamp
        # TODO(alvaro): Proper locale handling
        table.add_row(entry.timestamp.strftime(TIMESTAMP_FMT), entry.header, entry.body)
    # Print the actual table
    console.print(table)


def run() -> int:
    app()
    return 0
