"""PAL setup functions"""
from __future__ import annotations

import os
import pathlib

DEFAULT_DB_FILENAME = "pal.db"


class SetupError(Exception):
    """An error raised during the setup of PAL environment"""

    pass


def ensure_setup():
    """Ensure that the basic setup is created.

    This includes creating the PAL directory
    """
    pal_dir = default_pal_directory()
    pal_dir.mkdir(exist_ok=True)
    assert pal_dir.exists()


def default_pal_directory() -> pathlib.Path:
    """Return the default path for the PAL directory.

    The default location of the PAL directory is in a folder inside `$XDG_DATA_HOME`, which
    by default is at `$HOME/.local/share`. The PAL directory is the `pal` directory at
    that location.
    """
    path_home_str = os.environ.get("XDG_DATA_HOME") or os.path.expanduser(
        "~/.local/share"
    )
    path_home = pathlib.Path(path_home_str)
    if not path_home.exists():
        raise SetupError(f"directory for PAL_DB does not exist: {path_home.resolve()}")

    # Create the `pal` directory if it does not exist already
    pal_directory = path_home / "pal"
    return pal_directory


def default_db_path(filename: str = DEFAULT_DB_FILENAME) -> pathlib.Path:
    """Return the default path for the PAL db file.

    The PAL db file is located inside the PAL directory, by default named `pal.db`.
    """
    return default_pal_directory() / filename
