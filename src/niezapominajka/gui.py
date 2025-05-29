#!/usr/bin/env python
from signal import SIGINT, signal, SIG_DFL
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QToolBar,
    QGridLayout,
    QListWidget,
    QLabel,
    QPushButton
)
from PyQt6.QtGui import QIcon
from importlib import resources

from . import review


class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()

        home = QPushButton()
        icon = resources.files('niezapominajka').joinpath('res', 'home.svg')
        home.setIcon(QIcon(str(icon)))
        home.clicked.connect(lambda: self.go_home(self.parent()))
        self.addWidget(home)

    def go_home(self, parent):
        if isinstance(parent.centralWidget, DeckReview):
            parent.centralWidget.close_db()

        parent.setCentralWidget(HomeScreen())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Niezapominajka')
        self.setCentralWidget(HomeScreen())
        self.addToolBar(Toolbar())
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
        self.cards_for_review, self.db_con = review.get_cards_for_review(deck_name)
        if not self.cards_for_review:
            self.card_widget.setText('Empty deck :)')
            self.good.hide()
            self.bad.hide()
            self.db_con.close()
        else:
            self.card_pair = None
            self.is_question = None

            self.deal_a_card()

    def deal_a_card(self):
        self.good.hide()
        self.bad.hide()
        if not self.cards_for_review:
            self.card_widget.setText('Empty deck :)')
            self.answer_text = None
            self.question_text = None
            self.db_con.close()
        else:
            self.card_pair = self.cards_for_review.pop()

            try:
                self.question_text = review.get_card_content(self.card_pair['question_path'])
                self.answer_text = review.get_card_content(self.card_pair['answer_path'])
                self.card_widget.setText(self.question_text)
                self.is_question = True
            except FileNotFoundError:
                # todo: popup?
                self.deal_a_card()

    def mouseReleaseEvent(self, _event):
        if self.answer_text is not None:
            if self.is_question:
                self.card_widget.setText(self.answer_text)
                self.is_question = False
            else:
                self.card_widget.setText(self.question_text)
                self.is_question = True
            self.good.show()
            self.bad.show()

    def answered(self, score):
        review.card_reviewed(self.card_pair['question_path'].stem,
                             self.card_pair['side'], self.db_con, score)
        self.deal_a_card()

    def close_db(self):
        self.db_con.close()


def gui():
    app = QApplication([])
    _window = MainWindow()
    app.exec()


signal(SIGINT, SIG_DFL)
