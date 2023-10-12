from __future__ import annotations

import argparse

from pal import setup


def run() -> int:
    return 0


def ensure_setup():
    print("ensuring setup")
    pal_dir = setup.default_pal_directory()
    pal_dir.mkdir(exist_ok=True)
    assert pal_dir.exists()
    print("PAL directory: ", pal_dir.resolve())


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()  # noqa: F841

    ensure_setup()

    raise SystemExit(run())
