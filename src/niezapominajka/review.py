#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

import sqlite3
from collections import defaultdict
from pathlib import Path

from .constants import STATE_HOME


def get_deck_list(flags=[]):
    deck_names = [x.stem for x in STATE_HOME.iterdir() if x.is_dir()]
    deck_list = []
    if 'q' in flags: return deck_names
    else:
        for name in deck_names:
            session = ReviewSession(name)
            deck_list.append({
                'name': name,
                'num': len(session.cards_for_review),
            })
        return deck_list


class ReviewSession:
    def __init__(self, deck_name):
        deck_dir = STATE_HOME / deck_name

        # card pair validation
        # each pair must have both front and back
        card_parts = defaultdict(set)
        for filepath in deck_dir.iterdir():
            if filepath.is_dir():
                print(f'Found subdirectory {filepath}. Ignored')
                continue

            if filepath.suffix in ('.f', '.b'):
                card_parts[filepath.stem].add(filepath.suffix)
            else:
                if filepath.name != f'{deck_name}.db':
                    print(f'Found file {filepath} without valid extension. Ignored')
                continue

        cards_validated = {
            basename for basename, exts in card_parts.items()
            if exts == {'.f', '.b'}
        }

        #
        self.con = sqlite3.connect(deck_dir / f'{deck_name}.db')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS cards(name NOT NULL,
front_level DEFAULT 1,
back_level DEFAULT 1,
front_next_revision DEFAULT CURRENT_DATE,
back_next_revision DEFAULT CURRENT_DATE)''')

        # adding missing cards from the current session to the database
        # filesystem is the single source of truth for card existence
        cards_from_db = {row[0] for row in self.cur.execute('SELECT name FROM cards').fetchall()}
        missing_cards = cards_validated - cards_from_db

        if missing_cards:
            self.cur.executemany('INSERT into cards (name) VALUES(?)', [(x,) for x in missing_cards])
            self.con.commit()

        #
        data = self.cur.execute('SELECT name FROM cards where front_next_revision <= CURRENT_DATE').fetchall()
        front_for_review = {x[0] for x in data}.intersection(cards_validated)
        front_for_review = [{'q_path': deck_dir / f'{x}.f',
                             'a_path': deck_dir / f'{x}.b',
                             'side': 'front'
                             }
                            for x in front_for_review]

        data = self.cur.execute('SELECT name FROM cards where back_next_revision <= CURRENT_DATE').fetchall()
        back_for_review = {x[0] for x in data}.intersection(cards_validated)
        back_for_review = [{'q_path': deck_dir / f'{x}.b',
                            'a_path': deck_dir / f'{x}.f',
                            'side': 'back'
                            }
                           for x in back_for_review]

        self.cards_for_review = front_for_review + back_for_review

        #
        self.current_card = None

    def get_next_card(self):
        def get_card_content(card_path):
            try:
                return Path.read_text(card_path).strip()
            except FileNotFoundError:
                print(f'''{card_path} does not exist, but it existed when the cards for
        review were being assembled. Moving to the next card''')
                raise

        if self.cards_for_review:
            self.current_card = self.cards_for_review.pop()
            question = get_card_content(self.current_card['q_path'])
            answer = get_card_content(self.current_card['a_path'])
            return (question, answer)
        else:
            self.con.close()
            return None

    def submit_score(self, score):
        side = self.current_card['side']
        self.cur.execute(f'''UPDATE cards set
            {side}_level = {side}_level * 2 * ? + 1,
            {side}_next_revision = CASE ?
            WHEN 0 THEN date('now','+1 day')
            ELSE date('now','+' ||cast(({side}_level+1) as text)|| ' day')
            END
            WHERE name = ?''', (score, score, self.current_card['q_path'].stem))
        self.con.commit()

    def close_db(self):
        self.con.close()
