#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from os import environ
from pathlib import Path

DECKS_DIR = None

if 'XDG_DECKS_DIR' in environ:
    DECKS_DIR = Path(f'{environ["XDG_DATA_HOME"]}/niezapominajka/decks')
else:
    DECKS_DIR = Path(f'{environ["HOME"]}/.local/share/niezapominajka/decks')
if not Path.exists(DECKS_DIR):
    Path(DECKS_DIR).mkdir(parents=True, exist_ok=True)

NEW_CARDS_PER_DAY = 10
