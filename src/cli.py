#!/usr/bin/env python
from collections import defaultdict
from pathlib import Path
from sys import stdin
from review import review, cards_for_review

def cli():
    for card_path in cards_for_review:
        card_path_no_suffix = card_path.parent / card_path.stem
        card_pair = defaultdict()
        card_pair['question_path'] = card_path
        card_pair['info_path'] = Path(f'{card_path_no_suffix}.i')
        if card_path.suffix == '.f':
            card_pair['side'] = 'front'
            card_pair['answer_path'] = Path(f'{card_path_no_suffix}.b')
        elif card_path.suffix == '.b':
            card_pair['side'] = 'back'
            card_pair['answer_path'] = Path(f'{card_path_no_suffix}.f')

        print(Path.read_text(card_pair['question_path']).strip())
        input()
        print(Path.read_text(card_pair['answer_path']).strip())
        print('-------------\n(g)ood  (b)ad')
        while(True):
            key = stdin.readline()
            if key == "g\n":
                print('-------------\n-------------')
                review.card_reviewed(card_pair, 1)
                break
            if key == "b\n":
                print('-------------\n-------------')
                review.card_reviewed(card_pair, 0)
                break
