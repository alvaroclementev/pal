from __future__ import annotations

import argparse
import datetime
import os
from typing import Optional

from pal import db, models, setup
from pal.models import entry


def init_db():
    """Initialize the Database with all the required tables"""
    print("initializing the db")

    # TODO(alvaro): We should check that the schema is the correct one...
    # although that would be heavy... maybe we can query the version of the DB
    # schema in some way, and have some migration path ready

    # Create the entry table
    con = db.get_connection()
    with con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author TEXT NOT NULL,
                project TEXT NOT NULL,
                timestamp STRING NOT NULL,
                created_at STRING NOT NULL,
                updated_at STRING NOT NULL
            );
            """
        )


def create_entry(
    text: str, author: str, project: str, timestamp: Optional[datetime.datetime] = None
) -> models.Entry:
    """Insert a new entry in the table"""

    if not timestamp:
        timestamp = datetime.datetime.now()

    e = models.Entry(
        text=text,
        author=author,
        project=project,
        timestamp=timestamp,
    )

    # Actually insert the entry
    con = db.get_connection()
    inserted = entry.insert_entry(con, e)

    return inserted


def display_entries(
    author: str, project: str, pretty: bool = True, n: Optional[int] = None
):
    """Display the entries"""

    # Find the entries
    con = db.get_connection()
    entries = entry.find_entries(con, author=author, project=project)

    # Format the entries
    for i, e in enumerate(entries):
        header = f"{e.author} - {e.project} - {e.timestamp}"
        print(header)
        print("".join(["-"] * len(header)))
        print(e.text)

        if i != len(entries):
            print()


def author_or_default(requested_author: Optional[str]) -> str:
    """Get the author for interactions.

    The value will be picked from the following sources, in descending priority:
        - CLI argument
        - $PAL_AUTHOR environment variable
        - current OS username ($USER environment variable)
    """
    # TODO(alvaro): Add support for configuration based author (either from global
    # or local config)
    actual_author = (
        requested_author or os.environ.get("PAL_AUTHOR") or os.environ.get("USER")
    )
    if not actual_author:
        raise setup.SetupError("could not find an author for filtering")
    return actual_author


def project_or_default(requested_project: Optional[str]) -> str:
    """Get the project for interactions.

    The value will be picked from the following sources, in descending priority:
        - CLI argument
        - $PAL_PROJECT environment variable
        - "default"
    """
    # TODO(alvaro): Add support for configuration based project (either from global
    # or local config)
    actual_project = requested_project or os.environ.get("PAL_PROJECT", "default")
    if not actual_project:
        raise setup.SetupError("could not find a project for filtering")
    return actual_project


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text for an entry", nargs="*")
    parser.add_argument("-a", "--author", help="Author for the entries", default=None)
    parser.add_argument("-p", "--project", help="Project for the entries", default=None)

    args = parser.parse_args()  # noqa: F841
    text = args.text
    author_arg = args.author
    project_arg = args.project

    # Run the right command
    if text:
        # Create a new entry
        setup.ensure_setup()

        author = author_or_default(author_arg)
        project = project_or_default(project_arg)
        create_entry(" ".join(text), author=author, project=project)
    else:
        # Just display the entries
        init_db()
        setup.ensure_setup()

        # Get the default author
        author = author_or_default(author_arg)
        project = project_or_default(project_arg)

        display_entries(author=author, project=project, pretty=True)
