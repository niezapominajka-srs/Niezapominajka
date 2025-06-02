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

_review_session = None


class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()

        home = QPushButton()
        icon = resources.files('niezapominajka').joinpath('res', 'home.svg')
        home.setIcon(QIcon(str(icon)))
        home.clicked.connect(lambda: self.go_home(self.parent()))
        self.addWidget(home)

    def go_home(self, parent):
        if _review_session:
            _review_session.close_db()

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
        global _review_session
        _review_session = review.ReviewSession(deck_name)

        self.deal_a_card()

    def deal_a_card(self):
        self.good.hide()
        self.bad.hide()
        while True:
            try:
                cards_content = _review_session.get_next_card()
                if cards_content:
                    self.question_text = cards_content[0]
                    self.answer_text = cards_content[1]
                    self.card_widget.setText(self.question_text)
                    self.is_question = True
                    break
                else:
                    self.card_widget.setText('Empty deck :)')
                    self.answer_text = None
                    self.question_text = None
                    break
            except FileNotFoundError:
                # todo: popup?
                continue

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
        _review_session.submit_score(score)
        self.deal_a_card()


def gui():
    app = QApplication([])
    _window = MainWindow()
    app.exec()


signal(SIGINT, SIG_DFL)
