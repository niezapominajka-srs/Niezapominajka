#!/usr/bin/env python
from signal import SIGINT, signal
from sys import stdin

from . import review


def cli():
    deck_list = review.get_deck_list()
    print('Decks:')
    for x in deck_list: print(' ', x)
    while True:
        deck_name = stdin.readline().strip()
        if deck_name in deck_list:
            print('-------------\n-------------')
            cli_review(deck_name)
            break


def cli_review(deck_name):
    cards_for_review, db_con = review.get_cards_for_review(deck_name)
    while cards_for_review:
        card_pair = cards_for_review.pop()
        try:
            print(review.get_card_content(card_pair['question_path']))
            input()
            print(review.get_card_content(card_pair['answer_path']))
            print('-------------\n(g)ood  (b)ad')
        except FileNotFoundError:
            print('-------------\n-------------')
            continue
        while True:
            key = stdin.readline()
            if key == 'g\n':
                print('-------------\n-------------')
                review.card_reviewed(card_pair['question_path'].stem,
                                     card_pair['side'], db_con, 1)
                break
            if key == 'b\n':
                print('-------------\n-------------')
                review.card_reviewed(card_pair['question_path'].stem,
                                     card_pair['side'], db_con, 0)
                break
    db_con.close()
    print('Empty deck :)')


def sigint(_sig, _frame):
    print(end='\r')
    raise SystemExit


signal(SIGINT, sigint)
