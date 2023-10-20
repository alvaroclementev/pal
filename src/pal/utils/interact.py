"""Interaction related utilities"""

from __future__ import annotations


def ask_for_confirmation(msg: str, default_yes: bool = False) -> bool:
    """Prompt the user to confirm some action.

    It will print `msg` with interaction instructions, and return `True` or `False`
    based on the user's input.

    Set `default_yes` to `True` if you want the default action to be `yes`
    """

    instr = "[Y/n]" if default_yes else "[y/N]"

    answer = input(f"{msg} {instr}: ")
    return (answer == "" and default_yes) or answer == "y"
