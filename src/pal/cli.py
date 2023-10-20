from __future__ import annotations

import argparse
import datetime
import os
from enum import Enum
from typing import Optional

from rich.console import Console
from rich.table import Table

from pal import db, models, setup
from pal.models import entry
from pal.utils import interact

PAL_COMMAND_COMMIT = "commit"
PAL_COMMAND_LOG = "log"
PAL_COMMAND_CLEAN = "clean"
PAL_COMMAND_REPORT = "report"


class OutputFormat(str, Enum):
    """Supported output formats for log"""

    RICH = "rich"
    JSON = "json"


def init_db():
    """Initialize the Database with all the required tables"""
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
                reported BOOLEAN DEFAULT 0 NOT NULL,
                created_at STRING NOT NULL,
                updated_at STRING NOT NULL
            );
            """
        )


def request_confirmation_delete(author: str, project: Optional[str]) -> bool:
    """Request confirmation from the user for deletion action"""
    if project is None:
        msg = f"Delete all entries from '{author}'?"
    else:
        msg = f"Delete all entries from '{author}' in project '{project}'?"
    return interact.ask_for_confirmation(msg)


def request_confirmation_report(author: str, project: Optional[str]) -> bool:
    """Request confirmation from the user for report action"""
    if project is None:
        msg = f"Mark all entries from '{author}' as reported?"
    else:
        msg = f"Mark all entries from '{author}' in project '{project}' as reported?"
    return interact.ask_for_confirmation(msg)


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
    author: str,
    project: str,
    pretty: bool = True,
    n: Optional[int] = None,
    format: OutputFormat = OutputFormat.RICH,
    include_reported: bool = False,
):
    """Display the entries"""

    # Find the entries
    con = db.get_connection()
    entries = entry.find_entries(
        con, author=author, project=project, include_reported=include_reported
    )

    if format == OutputFormat.JSON:
        import json

        print(json.dumps([e.to_json(include_id=False) for e in entries]))
    elif format == OutputFormat.RICH:
        table = Table()
        table.add_column("timestamp", justify="right", style="yellow")
        table.add_column("project", style="green")
        if include_reported:
            table.add_column("reported", justify="center")
        table.add_column("text")

        for e in entries:
            timestamp_str = e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if include_reported:
                reported_emoji = (
                    ":white_heavy_check_mark:" if e.reported else ":cross_mark:"
                )
                table.add_row(timestamp_str, e.project, reported_emoji, e.text)
            else:
                table.add_row(timestamp_str, e.project, e.text)

        # Display the table
        console = Console()
        console.print(table)
    else:
        raise ValueError(f"invalid output format: {format!r}")


def delete_entries(author: str, project: Optional[str]):
    """Remove the entries that belong to the given `author` and `project`.

    If the `project` is `None`, this will remove entries across all projects
    """

    # Find the entries
    con = db.get_connection()
    deleted = entry.delete_entries(con, author=author, project=project)
    print(f"{deleted} entries deleted")


def report_entries(author: str, project: Optional[str]):
    """Mark the entries that belong to the given `author` and `project` as reported.

    If the `project` is `None`, this will report entries across all projects
    """

    # Find the entries
    con = db.get_connection()
    reported = entry.report_entries(con, author=author, project=project)
    print(f"{reported} entries marked as reported")


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


def handle_clean(
    author: Optional[str], project: Optional[str], all: bool, auto_yes: bool = False
):
    """Handle the `clean` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Handle the default values for author and project
    actual_author = author_or_default(author)
    actual_project = None if all else project_or_default(project)

    # Ask for confirmation
    if auto_yes or request_confirmation_delete(
        author=actual_author, project=actual_project
    ):
        delete_entries(author=actual_author, project=actual_project)


def handle_report(
    author: Optional[str],
    project: Optional[str],
    all: bool = False,
    auto_yes: bool = False,
):
    """Handle the `report` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Handle the default values for author and project
    actual_author = author_or_default(author)
    actual_project = None if all else project_or_default(project)

    # Ask for confirmation
    if auto_yes or request_confirmation_report(
        author=actual_author, project=actual_project
    ):
        report_entries(author=actual_author, project=actual_project)


def handle_log(
    author: Optional[str],
    project: Optional[str],
    json: bool = False,
    include_reported: bool = False,
):
    """Handle the `log` command for PAL"""

    # Make sure PAL is setup
    setup.ensure_setup()

    # Prepare the DB for use
    init_db()

    # Get the default author
    actual_author = author_or_default(author)
    actual_project = project_or_default(project)

    format = OutputFormat.JSON if json else OutputFormat.RICH

    display_entries(
        author=actual_author,
        project=actual_project,
        pretty=True,
        format=format,
        include_reported=include_reported,
    )


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
    parser.add_argument("-a", "--author", help="Author of the entries", default=None)
    parser.add_argument(
        "-p", "--project", help="Project associated to the entries", default=None
    )
    parser.add_argument(
        "--show-db",
        help="Show the full path to the DB file and exit",
        action="store_true",
    )

    subparser = parser.add_subparsers(dest="command", metavar="command")

    # Prepare the commit command
    commit_parser = subparser.add_parser(
        PAL_COMMAND_COMMIT, help="Commit a new entry to the PAL log"
    )
    commit_parser.add_argument(
        "text", help="Text for the body of the entry to commit", nargs="*"
    )

    # Prepare the log command
    log_parser = subparser.add_parser(PAL_COMMAND_LOG, help="Show the activity log")
    log_parser.add_argument(
        "--json", help="output the log in JSON format", action="store_true"
    )
    log_parser.add_argument(
        "-r",
        "--include-reported",
        help="Include entries already marked as reported",
        action="store_true",
    )

    # Prepare the clean command
    clean_parser = subparser.add_parser(PAL_COMMAND_CLEAN, help="Clean the log entries")
    clean_parser.add_argument(
        "-A",
        "--all",
        help="Clean the entries for all projects for the selected author",
        action="store_true",
    )
    clean_parser.add_argument(
        "-y", "--yes", help="Skip confirmation prompt", action="store_true"
    )

    # Prepare the report command
    report_parser = subparser.add_parser(
        PAL_COMMAND_REPORT, help="Handle report for entries"
    )
    report_parser.add_argument(
        "-A",
        "--all",
        help="Clean the entries across all projects for the selected author",
        action="store_true",
    )
    report_parser.add_argument(
        "-y", "--yes", help="Skip confirmation prompt", action="store_true"
    )

    args = parser.parse_args()  # noqa: F841
    command = args.command
    author_arg = args.author
    project_arg = args.project
    show_db = args.show_db

    if show_db:
        print(setup.default_db_path().resolve())
        return

    # Handle implicit command
    command = command or PAL_COMMAND_LOG

    # Run the command
    if command == PAL_COMMAND_LOG:
        # If the log command is implicit, we don't have the arguments
        json = getattr(args, "json", False)
        include_reported = getattr(args, "include_reported", False)
        handle_log(
            author=author_arg,
            project=project_arg,
            json=json,
            include_reported=include_reported,
        )
    elif command == PAL_COMMAND_COMMIT:
        text = " ".join(args.text)
        handle_commit(text, author=author_arg, project=project_arg)
    elif command == PAL_COMMAND_CLEAN:
        all = args.all
        yes = args.yes
        handle_clean(author=author_arg, project=project_arg, all=all, auto_yes=yes)
    elif command == PAL_COMMAND_REPORT:
        all = args.all
        yes = args.yes
        handle_report(author=author_arg, project=project_arg, all=all, auto_yes=yes)
    else:
        raise ValueError(f"invalid command {command!r}")
