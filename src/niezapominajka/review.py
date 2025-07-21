#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

import sqlite3
from pathlib import Path
from datetime import date, timedelta

from .constants import DATA_HOME


def get_deck_list(flags=[]):
    deck_names = [x.stem for x in DATA_HOME.iterdir() if x.is_dir()]
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
        deck_dir = DATA_HOME / deck_name

        self.con = sqlite3.connect(deck_dir / f'{deck_name}.db')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS cards(name NOT NULL,
front_level DEFAULT 1,
back_level DEFAULT 1,
front_next_revision DEFAULT CURRENT_DATE,
back_next_revision DEFAULT CURRENT_DATE)''')

        db_pairs = {x[0] for x in self.cur.execute('SELECT name FROM cards').fetchall()}

        fs_pairs = {
            path.name for path in deck_dir.iterdir()
            if path.is_dir()
            and {'front', 'back'}.issubset(x.name for x in path.iterdir())
        }

        missing_pairs = fs_pairs - db_pairs
        if missing_pairs:
            self.cur.executemany('INSERT into cards (name) VALUES(?)', [(x,) for x in missing_pairs])
            self.con.commit()

        self.cards_for_review = [
            {'name': name,
             'q_path': deck_dir / name / side,
             'a_path': deck_dir / name / ('back' if side == 'front' else 'front'),
             'side': side
             }
            for name, side in self.cur.execute('''
                SELECT name, 'front' as side FROM cards where front_next_revision <= CURRENT_DATE
                UNION ALL
                SELECT name, 'back' as side FROM cards where back_next_revision <= CURRENT_DATE
            ''').fetchall()
            if name in fs_pairs
        ]

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
            return {'question': question, 'answer': answer}
        else:
            self.con.close()
            return None

    def submit_score(self, score):
        side = self.current_card['side']
        curr_score, curr_revision_date = self.cur.execute(f'''
            SELECT {side}_level, {side}_next_revision FROM cards
            WHERE name = ?
        ''', (self.current_card['name'],)).fetchone()
        new_score = curr_score * (score * 2) + 1
        new_date = date.today() + timedelta(days=new_score)
        self.cur.execute(f'''
            UPDATE cards SET
            {side}_level = ?,
            {side}_next_revision = ?
            WHERE name = ?
        ''', (new_score, new_date, self.current_card['name']))
        self.con.commit()

    def close_db(self):
        self.con.close()
