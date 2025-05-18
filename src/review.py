#!/usr/bin/env python
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from constants import STATE_HOME


def card_reviewed(i_path, side, score):
    if Path.exists(i_path):
        with open(i_path, encoding='utf-8') as content:
            content = [x.strip() for x in content]

            index = {}
            level = 0
            for i, line in enumerate(content):
                if len(line.split(' = ')) == 2:
                    key, val = line.split(' = ', 1)
                if key == f'{side}_level':
                    if val.isnumeric():
                        index['level'] = i
                        level = int(val)
                elif key == f'{side}_next_revision':
                    index['next_revision'] = i

            if 'level' in index:
                if score == 0: level = 0
                else: level = level * 2 * score if level != 0 else 1
                content[index['level']] = f'{side}_level = {level}'
            else:
                level = score
                content.append(f'{side}_level = {level}')

            next_revision_date = date.today() + timedelta(days=level+1)
            if 'next_revision' in index:
                content[index['next_revision']] = f'{side}_next_revision = {next_revision_date}'
            else:
                content.append(f'{side}_next_revision = {next_revision_date}')

            Path.write_text(i_path, '\n'.join(content)+'\n')
    else:
        Path.write_text(i_path,
                        f'{side}_next_revision = {date.today() + timedelta(days=score+1)}\
\n{side}_level = {score}\n')


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

#    cards_without_pair = {
#        f'{basename}.{ext}'
#        for basename, exts in card_parts.items()
#        for ext in exts
#        if exts not in ({'f', 'b'}, {'f', 'b', 'i'})
#    }

    def get_review_dict(question_path, answer_path, i_path, side):
        return {
            'question_path': question_path,
            'answer_path': answer_path,
            'i_path': i_path,
            'side': side
        }

    cards_for_review = []
    for card in cards_validated:
        i_path = deck_dir / f'{card}.i'
        f_path = deck_dir / f'{card}.f'
        b_path = deck_dir / f'{card}.b'
        if Path.exists(i_path):
            with open(i_path, encoding='utf-8') as content:
                front_next_revision = None
                back_next_revision = None
                for line in content:
                    if len(line.split(' = ')) == 2:
                        key, val = line.strip().split(' = ', 1)
                    if key == 'front_next_revision':
                        try:
                            front_next_revision = datetime.strptime(val, '%Y-%m-%d').date()
                        except ValueError:
                            print(f'Wrong value for \'front_next_revision\': \'{val}\' in {i_path}. Ignored.')
                            continue
                    elif key == 'back_next_revision':
                        try:
                            back_next_revision = datetime.strptime(val, '%Y-%m-%d').date()
                        except ValueError:
                            print(f'Wrong value for \'back_next_revision\': \'{val}\' in {i_path}. Ignored.')
                            continue

                if front_next_revision:
                    if front_next_revision <= date.today():
                        cards_for_review.append(get_review_dict(f_path, b_path, i_path, 'front'))
                if back_next_revision:
                    if back_next_revision <= date.today():
                        cards_for_review.append(get_review_dict(b_path, f_path, i_path, 'back'))
        else:
            cards_for_review.append(get_review_dict(f_path, b_path, i_path, 'front'))
            cards_for_review.append(get_review_dict(b_path, f_path, i_path, 'back'))

    return cards_for_review
