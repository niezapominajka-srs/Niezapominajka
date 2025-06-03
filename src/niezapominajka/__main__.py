#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from .constants import MODE


def run_cli():
    from . import cli
    cli.cli()


def run_gui():
    from . import gui
    gui.gui()


if __name__ == '__main__':
    if MODE == 'cli':
        run_cli()
    else:
        run_gui()
