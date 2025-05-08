#!/usr/bin/env python
from os import environ
from pathlib import Path

from args import MODE

if 'XDG_STATE_HOME' in environ:
    STATE_HOME = Path(f'{environ["XDG_STATE_HOME"]}/niezapominajka')
else:
    STATE_HOME = Path(f'{environ["HOME"]}/.local/state/niezapominajka')
if not Path.exists(STATE_HOME): Path.mkdir(STATE_HOME)


def run_cli():
    import cli
    cli.cli()


def run_gui():
    import gui
    gui.gui()


if __name__ == '__main__':
    if MODE == 'cli':
        run_cli()
    else:
        run_gui()
