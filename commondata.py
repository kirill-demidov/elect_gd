from PyQt5 import QtCore
from PyQt5.QtWidgets import (QMessageBox)
import json

settings: QtCore.QSettings
width_form = 1200
height_form = 800
texts = None


def load_texts(filename):
    global texts
    try:
        f = open(filename, 'rt', encoding='utf-8')  # только чтение и текстовый файл
        with f:
            texts = f.read()
            texts = json.loads(texts.replace('\n', ' '))
    except Exception as err:
        make_question(None, filename + f'\n {err}', 'Ошибка чтения файла', texts, only_ok=True)


def row_only_read(row, mas_change):
    for jj in range(0, len(row)):
        ind = row.__getitem__(jj)
        if not (jj in mas_change):  # колонка только для чтения
            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


def make_question(self, txt, informative_text=None, detailed_text=None, only_ok=False):
    message_box = QMessageBox(self)
    message_box.setText(txt)
    message_box.setIcon(4)
    if informative_text:
        message_box.setWindowTitle(informative_text)
    if detailed_text:
        message_box.setDetailedText(detailed_text)
    if only_ok:
        message_box.setStandardButtons(QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.Yes)
    else:
        message_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.No)
    result = message_box.exec()
    return result == QMessageBox.Yes
