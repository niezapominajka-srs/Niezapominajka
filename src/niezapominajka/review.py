#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

import sqlite3
from pathlib import Path
from datetime import date, timedelta

from .constants import DATA_HOME, NEW_CARDS_PER_DAY


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
side NOT NULL,
level DEFAULT 1,
next_revision DEFAULT CURRENT_DATE)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS stats_new_per_day(
date DEFAULT CURRENT_DATE,
number NOT NULL)''')

        db_cards = set(self.cur.execute('SELECT name, side FROM cards').fetchall())

        fs_cards = set(
            (path.name, side)
            for path in deck_dir.iterdir()
            if path.is_dir()
            and {'front', 'back'}.issubset(x.name for x in path.iterdir())
            for side in ('front', 'back')
        )

        new_cards = fs_cards - db_cards
        new_cards_already_added = self.cur.execute('SELECT number FROM stats_new_per_day WHERE date = CURRENT_DATE').fetchone()
        new_cards_for_today = []
        if not new_cards_already_added:
            new_cards_for_today = {new_cards.pop() for _ in range(
                min(len(new_cards), NEW_CARDS_PER_DAY)
            )}
        self.cur.execute(f'INSERT INTO stats_new_per_day (number) VALUES ({len(new_cards_for_today)})')
        self.con.commit()
        if new_cards_for_today:
            self.cur.executemany('INSERT INTO cards (name, side) VALUES(?, ?)', [x for x in new_cards_for_today])
            self.con.commit()

        self.cards_for_review = [
            {'name': name,
             'q_path': deck_dir / name / side,
             'a_path': deck_dir / name / ('back' if side == 'front' else 'front'),
             'side': side
             }
            for name, side in self.cur.execute('''
                SELECT name, side FROM cards where next_revision <= CURRENT_DATE
            ''').fetchall()
            if (name, side) in fs_cards
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
        name = self.current_card['name']
        side = self.current_card['side']
        curr_score, curr_revision_date = self.cur.execute('''
            SELECT level, next_revision FROM cards
            WHERE name = ? and side = ?
        ''', (name, side)).fetchone()
        new_score = curr_score * (score * 2) + 1
        new_date = date.today() + timedelta(days=new_score)
        self.cur.execute('''
            UPDATE cards SET
            level = ?,
            next_revision = ?
            WHERE name = ? and side = ?
        ''', (new_score, new_date, name, side))
        self.con.commit()

    def close_db(self):
        self.con.close()
