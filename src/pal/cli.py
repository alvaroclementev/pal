from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def main():
    console.print("Hello from your [green]Personal Activity Log[/green]")


def run() -> int:
    typer.run(main)
    return 0
