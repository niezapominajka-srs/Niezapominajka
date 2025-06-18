#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from sys import argv


def main():
    mode = 'review'
    flags = []
    argc = len(argv)
    if argc > 1:
        match argv[1]:
            case '--version':
                mode = None
                print('Niezapominajka 0.0.1')
            case '-h' | '--help':
                mode = None
                print('''\
subcommands:
    review (default)
        options:
            -q, --quiet
                do not fetch and show the number of cards in today's review session next
                to the deck name.
options:
    --version
    --help\
''')
            case '-q' | '--quiet': flags.append('q')

    match mode:
        case 'review':
            from . import cli
            cli.cli(flags)


if __name__ == '__main__':
    main()
