#!/usr/bin/env python
from os import environ
from pathlib import Path

if 'XDG_STATE_HOME' in environ:
    STATE_HOME = Path(f'{environ["XDG_STATE_HOME"]}/niezapominajka')
else:
    STATE_HOME = Path(f'{environ["HOME"]}/.local/state/niezapominajka')
if not Path.exists(STATE_HOME): Path.mkdir(STATE_HOME)


if __name__ == '__main__':
    import cli
    cli.cli()
