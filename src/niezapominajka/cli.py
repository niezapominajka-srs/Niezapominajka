#!/usr/bin/env python
import readline
from signal import SIGINT, signal

from . import review


def cli():
    deck_list = review.get_deck_list()

    print('Decks:')
    for x in deck_list: print(' ', x)

    def completer(text, state):
        options = [x for x in deck_list if x.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    while True:
        deck_name = input()
        if deck_name in deck_list:
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
