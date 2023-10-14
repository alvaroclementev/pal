from __future__ import annotations

import argparse
import datetime
import os
from typing import Optional

from pal import db, models, setup
from pal.models import entry

PAL_COMMAND_COMMIT = "commit"
PAL_COMMAND_LOG = "log"
PAL_COMMAND_CLEAN = "clean"


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

    # Create an entry
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


def delete_entries(author: str, project: Optional[str]):
    """Remove the entries that belong to the given `author` and `project`.

    If the `project` is `None`, this will remove all the entries for the given user
    """

    # Find the entries
    con = db.get_connection()
    deleted = entry.delete_entries(con, author=author, project=project)
    print(f"{deleted} entries deleted")


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


def handle_clean(text: str, author: Optional[str], project: Optional[str], all: bool):
    """Handle the `clean` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Handle the default values for author and project
    actual_author = author_or_default(author)
    actual_project = None if all else project_or_default(project)
    delete_entries(author=actual_author, project=actual_project)


def handle_log(author: Optional[str], project: Optional[str]):
    """Handle the `log` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Get the default author
    actual_author = author_or_default(author)
    actual_project = project_or_default(project)

    display_entries(author=actual_author, project=actual_project, pretty=True)


def handle_commit(text: str, author: Optional[str], project: Optional[str]):
    """Handle the `commit` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Handle the default values for author and project
    actual_author = author_or_default(author)
    actual_project = project_or_default(project)

    create_entry(text, author=actual_author, project=actual_project)


def main():
    parser = argparse.ArgumentParser()

    # Global options
    parser.add_argument("text", help="Text for an entry", nargs="*")
    parser.add_argument("-a", "--author", help="Author of the entries", default=None)
    parser.add_argument(
        "-p", "--project", help="Project associated to the entries", default=None
    )

    subparser = parser.add_subparsers(dest="command", metavar="command")

    # Prepare the commit command
    subparser.add_parser(PAL_COMMAND_COMMIT, help="Commit a new entry to the PAL log")

    # Prepare the log command
    subparser.add_parser(PAL_COMMAND_LOG, help="Show the activity log")

    # Prepare the clean command
    clean_parser = subparser.add_parser(PAL_COMMAND_CLEAN, help="Clean the log entries")
    clean_parser.add_argument(
        "-A", "--all", help="Clean the entries for all projects for the selected"
    )

    args = parser.parse_args()  # noqa: F841
    command = args.command
    text_args = args.text
    author_arg = args.author
    project_arg = args.project

    # Handle implicit commands
    if command is None:
        command = PAL_COMMAND_COMMIT if text_args else PAL_COMMAND_LOG

    # Run the command
    if command == PAL_COMMAND_LOG:
        handle_log(author=author_arg, project=project_arg)
    elif command == PAL_COMMAND_COMMIT:
        text = " ".join(text_args)
        handle_commit(text, author=author_arg, project=project_arg)
    elif command == PAL_COMMAND_CLEAN:
        all = args.all
        handle_clean(author=author_arg, project=project_arg, all=all)
