#!/usr/bin/env python
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
