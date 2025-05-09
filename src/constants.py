#!/usr/bin/env python
from os import environ
from pathlib import Path
from sys import argv

STATE_HOME = None
MODE = 'gui'

if 'XDG_STATE_HOME' in environ:
    STATE_HOME = Path(f'{environ["XDG_STATE_HOME"]}/niezapominajka')
else:
    STATE_HOME = Path(f'{environ["HOME"]}/.local/state/niezapominajka')
if not Path.exists(STATE_HOME): Path.mkdir(STATE_HOME)

for arg in argv[1:]:
    if arg == '--cli': MODE = 'cli'
    else:
        print(f'usage: {argv[0]} [--cli]')
