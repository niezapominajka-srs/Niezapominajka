#!/usr/bin/env python
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from constants import STATE_HOME


def card_reviewed(card_pair, score):
    with open(card_pair['info_path'], encoding='utf-8') as content:
        content = list(content)
        level = None
        for line in content:
            try: key, val = line.strip().split(' = ')
            except ValueError: continue
            if key == f'{card_pair["side"]}_level':
                if val.isnumeric():
                    level = int(val)

        if level is not None:
            if score == 0: level = 0
            else: level = level * 2 * score if level != 0 else 1
        else:
            if not content[len(content)-1].endswith('\n'):
                newline_added = f'{content.pop()}\n'
                content.append(newline_added)
            level = score
            text = f'{card_pair["side"]}_level = {level}'
            content.append(text)

        next_revision_date = date.today() + timedelta(days=level+1)
        for i, line in enumerate(content):
            try: key, val = line.split(' = ')
            except ValueError: continue
            if key == f'{card_pair["side"]}_level':
                content[i] = f'{card_pair["side"]}_level = {level}\n'
            if key == f'{card_pair["side"]}_next_revision':
                content[i] = f'{card_pair["side"]}_next_revision = {next_revision_date}\n'
        Path.write_text(card_pair['info_path'], ''.join(content))


def get_cards_for_review(deck_name):
    deck_dir = STATE_HOME / deck_name

    # each card must have front "<name>.f" and back "<name>.b"
    card_parts = defaultdict(set)
    for filepath in deck_dir.iterdir():
        if filepath.is_dir():
            print(f'Found subdirectory {filepath}. Ignored')
            continue

        if filepath.suffix not in ('.f', '.b', '.i'):
            print(f'Found file {filepath} without valid extension. Ignored')
            continue

        basename = filepath.stem
        ext = filepath.suffix[1:]
        card_parts[basename].add(ext)

    cards_validated = {
        basename for basename, exts in card_parts.items()
        if exts in ({'f', 'b'}, {'f', 'b', 'i'})
    }

    cards_without_pair = {
        f'{basename}.{ext}'
        for basename, exts in card_parts.items()
        for ext in exts
        if exts != {'f', 'b'}
    }

    cards_for_review = set()
    for card in cards_validated:
        card_pair_path = defaultdict()
        card_pair_path['i'] = Path.joinpath(deck_dir, f'{card}.i')
        card_pair_path['f'] = Path.joinpath(deck_dir, f'{card}.f')
        card_pair_path['b'] = Path.joinpath(deck_dir, f'{card}.b')
        if Path.exists(card_pair_path['i']):
            with open(card_pair_path['i'], encoding='utf-8') as content:
                front_next_revision = None
                back_next_revision = None
                for line in content:
                    try:
                        key, val = line.split(' = ')
                    except ValueError:
                        if line.strip() != '':
                            print(f'Wrong syntax: \'{line.strip()}\'')
                        continue
                    if key == 'front_next_revision':
                        try:
                            front_next_revision = datetime.strptime(val.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            print(f'Wrong value for \'front_next_revision\': \'{val.strip()}\' in {card_pair_path["i"]}. Ignored.')
                            continue
                    if key == 'back_next_revision':
                        try:
                            back_next_revision = datetime.strptime(val.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            print(f'Wrong value for \'back_next_revision\': \'{val.strip()}\' in {card_pair_path["i"]}. Ignored')
                            continue
                if front_next_revision:
                    if front_next_revision <= date.today():
                        cards_for_review.add(card_pair_path['f'])
                else:
                    with open(card_pair_path['i'], 'ab+') as f:
                        text = f'front_next_revision = {date.today()}'
                        if f.tell() > 0:
                            f.seek(-1, 2)
                            if f.read(1) != b'\n':
                                f.write(b'\n')
                        f.write(text.encode('utf-8'))
                        cards_for_review.add(card_pair_path['f'])

                if back_next_revision:
                    if back_next_revision <= date.today():
                        cards_for_review.add(card_pair_path['b'])
                else:
                    with open(card_pair_path['i'], 'ab+') as f:
                        text = f'back_next_revision = {date.today()}'
                        if f.tell() > 0:
                            f.seek(-1, 2)
                            if f.read(1) != b'\n':
                                f.write(b'\n')
                        f.write(text.encode('utf-8'))
                        cards_for_review.add(card_pair_path['b'])
        else:
            Path.touch(card_pair_path['i'])
            with open(card_pair_path['i'], 'a', encoding='utf-8') as f:
                f.write(f'front_next_revision = {date.today()}')
                f.write(f'\nback_next_revision = {date.today()}\n')
                cards_for_review.add(card_pair_path['f'])
                cards_for_review.add(card_pair_path['b'])

    return cards_for_review
