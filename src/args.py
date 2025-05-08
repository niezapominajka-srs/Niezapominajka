#!/usr/bin/env python
from sys import argv

MODE = 'gui'

for arg in argv[1:]:
    if arg == '--cli': MODE = 'cli'
    else:
        print(f'usage: {argv[0]} [--cli]')
