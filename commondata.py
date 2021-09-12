from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMessageBox, QApplication)
from PyQt5.QtGui import QStandardItemModel
import xlwt
import json
import os

settings: QtCore.QSettings
width_form = 1200
height_form = 800
texts = None
iconCreate = None
iconDelete = None
iconSave = None
iconLoadFile = None
iconFont = None
iconExcel = None


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


def export_to_excel_xls(root_model: QStandardItemModel, file_name='test'):
    try:
        QApplication.setOverrideCursor(Qt.BusyCursor)  # курсор ожидания
        book = xlwt.Workbook()
        sheet1 = book.add_sheet("Sheet1")
        row = sheet1.row(0)
        for i in range(root_model.columnCount()):
            if i == 2:
                continue
            row.write(i, root_model.horizontalHeaderItem(i).text())
        for arow in range(root_model.rowCount()):
            row = sheet1.row(1 + arow)
            for i in range(root_model.columnCount()):
                if i == 2:
                    continue
                ind = root_model.index(arow, i)
                value = root_model.data(ind)
                row.write(i, value)
        path = 'file_excel'
        try:
            os.mkdir(path)
        except:
            pass
        book.save(path + '/' + file_name+'.xls')
        QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
        make_question(
            None, 'Таблица экспортирована в файл ' + os.getcwd() + '/' + path + '/' + file_name+'.xls',
            only_ok=True)
    except Exception as err:
        make_question(None, f'{err}', 'Ошибка экспорта', only_ok=True)
        QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
