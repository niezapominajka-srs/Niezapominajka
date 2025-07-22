#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from os import environ
from pathlib import Path

DATA_HOME = None

if 'XDG_DATA_HOME' in environ:
    DATA_HOME = Path(f'{environ["XDG_DATA_HOME"]}/niezapominajka')
else:
    DATA_HOME = Path(f'{environ["HOME"]}/.local/share/niezapominajka')
if not Path.exists(DATA_HOME):
    Path(DATA_HOME).mkdir(parents=True, exist_ok=True)

NEW_CARDS_PER_DAY = 10
