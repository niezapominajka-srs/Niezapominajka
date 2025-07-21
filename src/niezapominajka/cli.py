#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

import readline
from signal import SIGINT, signal

from . import review


def cli(flags=[]):
    deck_list = review.get_deck_list(flags)
    deck_names = None

    print('Decks:')
    if 'q' in flags:
        deck_names = deck_list
        for x in deck_list: print(' ', x)
    else:
        name_max_len = 0
        deck_names = []
        for x in deck_list:
            deck_names.append(x['name'])
            if len(x['name']) > name_max_len: name_max_len = len(x['name'])
        for x in deck_list: print(f" {x['name']}\
{x['num']: >{5 + name_max_len - len(x['name']) + len(str(x['num']))}}")

    non_empty_decks_names = [x['name'] for x in deck_list if x['num'] != 0]

    def completer(text, state):
        options = [x for x in non_empty_decks_names if x.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    while True:
        deck_name = input()
        if deck_name in deck_names:
            print('-------------\n-------------')
            cli_review(deck_name)
            break


def cli_review(deck_name):
    review_session = review.ReviewSession(deck_name)
    while True:
        cards_content = review_session.get_next_card()
        if cards_content:
            try:
                print(cards_content[0])
                input()
                print(cards_content[1])
                print('-------------\n(g)ood  (b)ad')
            except FileNotFoundError:
                print('-------------\n-------------')
                continue
            while True:
                key = input()
                if key == 'g':
                    print('-------------\n-------------')
                    review_session.submit_score(1)
                    break
                if key == 'b':
                    print('-------------\n-------------')
                    review_session.submit_score(0)
                    break
        else: break
    print('Empty deck :)')


def sigint(_sig, _frame):
    print(end='\r')
    raise SystemExit


signal(SIGINT, sigint)
