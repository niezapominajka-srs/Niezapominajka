#!/usr/bin/env python
from pathlib import Path
from signal import SIGINT, signal
from sys import stdin

import review


def cli():
    deck_list = review.get_deck_list()
    print('Decks:', )
    for x in deck_list: print(' ', x)
    while True:
        deck_name = stdin.readline().strip()
        if deck_name in deck_list:
            print('-------------\n-------------')
            cli_review(deck_name)
            break


def cli_review(deck_name):
    cards_for_review = review.get_cards_for_review(deck_name)
    while cards_for_review:
        card_pair = cards_for_review.pop()
        print(Path.read_text(card_pair['question_path']).strip())
        input()
        print(Path.read_text(card_pair['answer_path']).strip())
        print('-------------\n(g)ood  (b)ad')
        while True:
            key = stdin.readline()
            if key == 'g\n':
                print('-------------\n-------------')
                review.card_reviewed(card_pair['info_path'], card_pair['side'], 1)
                break
            if key == 'b\n':
                print('-------------\n-------------')
                review.card_reviewed(card_pair['info_path'], card_pair['side'], 0)
                break
    print('Empty deck :)')


def sigint(_sig, _frame):
    print(end='\r')
    raise SystemExit


signal(SIGINT, sigint)
