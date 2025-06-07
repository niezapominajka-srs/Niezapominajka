#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from sys import argv


def main():
    global mode
    mode = 'review'
    argc = len(argv)
    if argc > 1:
        match argv[1]:
            case '--version':
                mode = None
                print('Niezapominajka 0.0.1')
            case '-h' | '--help':
                mode = None
                print('''\
options:
    --version
    --help\
''')

    match mode:
        case 'review':
            from . import cli
            cli.cli()


if __name__ == '__main__':
    main()
