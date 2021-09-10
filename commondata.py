from PyQt5 import QtCore
import json

settings: QtCore.QSettings = None
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
    except:
        pass

def row_only_read(row, mas_change):
    for jj in range(0, len(row)):
        ind = row.__getitem__(jj)
        if not (jj in mas_change):  # колонка только для чтения
            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
