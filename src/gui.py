#!/usr/bin/env python
from pathlib import Path
from signal import SIGINT, signal, SIG_DFL
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QListWidget,
    QLabel,
    QPushButton
)

import review


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Niezapominajka')
        self.setCentralWidget(HomeScreen())
        self.show()


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.deck_list = QListWidget(self)
        self.deck_list.addItems(x for x in review.get_deck_list())
        layout.addWidget(self.deck_list)

        self.deck_list.clicked.connect(self.review_gui)

    def review_gui(self):
        deck_name = self.deck_list.currentItem().text()
        self.parent().setCentralWidget(DeckReview(deck_name))


class DeckReview(QWidget):
    def __init__(self, deck_name):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)

        self.card_widget = QLabel()
        layout.addWidget(self.card_widget)

        self.good = QPushButton('(g)ood')
        layout.addWidget(self.good)

        self.bad = QPushButton('(b)ad')
        layout.addWidget(self.bad)

        self.good.clicked.connect(lambda: self.answered(1))
        self.bad.clicked.connect(lambda: self.answered(0))

        self.answer_text = None
        self.question_text = None
        self.cards_for_review = review.get_cards_for_review(deck_name)
        if not self.cards_for_review:
            self.card_widget.setText('Empty deck :)')
            self.good.hide()
            self.bad.hide()
        else:
            self.card_pair = None
            self.is_question = None

            self.deal_a_card()

    def deal_a_card(self):
        self.card_pair = self.cards_for_review.pop()

        self.question_text = Path.read_text(self.card_pair['question_path']).strip()
        self.answer_text = Path.read_text(self.card_pair['answer_path']).strip()

        self.card_widget.setText(self.question_text)
        self.is_question = True

    def mouseReleaseEvent(self, _event):
        if self.answer_text is not None:
            if self.is_question:
                self.card_widget.setText(self.answer_text)
                self.is_question = False
            else:
                self.card_widget.setText(self.question_text)
                self.is_question = True

    def answered(self, score):
        review.card_reviewed(self.card_pair['info_path'], self.card_pair['side'], score)
        if not self.cards_for_review:
            self.card_widget.setText('Empty deck :)')
            self.good.hide()
            self.bad.hide()
            self.answer_text = None
            self.question_text = None
        else: self.deal_a_card()


def gui():
    app = QApplication([])
    _window = MainWindow()
    app.exec()


signal(SIGINT, SIG_DFL)
