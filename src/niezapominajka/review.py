#!/usr/bin/env python
import sqlite3
from collections import defaultdict
from pathlib import Path

from .constants import STATE_HOME


def card_reviewed(name, side, con, score):
    cur = con.cursor()
    cur.execute(f"UPDATE cards set\
        {side}_level = {side}_level * 2 * ? + 1,\
        {side}_next_revision = CASE ?\
        WHEN 0 THEN date('now','+1 day')\
        ELSE date('now','+' ||cast(({side}_level+1) as text)|| ' day')\
        END\
        WHERE name = ?", (score, score, name))
    con.commit()


def get_card_content(card_path):
    try:
        return Path.read_text(card_path).strip()
    except FileNotFoundError:
        print(f'{card_path} does not exist, but it existed when the cards for \
review were being assembled. Moving to the next card')
        raise


def get_deck_list():
    return [x.stem for x in STATE_HOME.iterdir() if x.is_dir()]


def get_cards_for_review(deck_name):
    deck_dir = STATE_HOME / deck_name

    # each card must have front "<name>.f" and back "<name>.b"
    card_parts = defaultdict(set)
    for filepath in deck_dir.iterdir():
        if filepath.is_dir():
            print(f'Found subdirectory {filepath}. Ignored')
            continue

        if filepath.suffix not in ('.f', '.b'):
            if filepath.name != f'{deck_name}.db':
                print(f'Found file {filepath} without valid extension. Ignored')
            continue

        basename = filepath.stem
        ext = filepath.suffix[1:]
        card_parts[basename].add(ext)

    cards_validated = {
        basename for basename, exts in card_parts.items()
        if exts == {'f', 'b'}
    }

#    cards_without_pair = {
#        f'{basename}.{ext}'
#        for basename, exts in card_parts.items()
#        for ext in exts
#        if exts not in ({'f', 'b'}, {'f', 'b', 'i'})
#    }

    db_path = deck_dir / f'{deck_name}.db'
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS cards(name NOT NULL,\
front_level DEFAULT 1,\
back_level DEFAULT 1,\
front_next_revision DEFAULT CURRENT_DATE,\
back_next_revision DEFAULT CURRENT_DATE)')

    cards_db = {row[0] for row in cur.execute('SELECT name FROM cards').fetchall()}
    missing_cards = cards_validated - cards_db
    if missing_cards:
        cur.executemany('INSERT into cards (name) VALUES(?)', [(x,) for x in missing_cards])
        con.commit()

    data = cur.execute('SELECT name FROM cards where front_next_revision <= CURRENT_DATE').fetchall()
    front_for_review = {x[0] for x in data}.intersection(cards_validated)
    front_for_review = [{'question_path': deck_dir / f'{x}.f',
                         'answer_path': deck_dir / f'{x}.b',
                         'side': 'front'
                         }
                        for x in front_for_review]

    data = cur.execute('SELECT name FROM cards where back_next_revision <= CURRENT_DATE').fetchall()
    back_for_review = {x[0] for x in data}.intersection(cards_validated)
    back_for_review = [{'question_path': deck_dir / f'{x}.b',
                        'answer_path': deck_dir / f'{x}.f',
                        'side': 'back'
                        }
                       for x in back_for_review]

    return (front_for_review + back_for_review, con)
