import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog, QFontDialog, QCheckBox, QApplication, QSpinBox, \
    QDoubleSpinBox, QMessageBox
import os
from matplotlib import pyplot as plt
import pandas as pan

import commondata


class TModeler(QWidget):
    formaparent = None
    select_directory = ''
    select_file = ''
    select_file_excel = ''
    exist = False
    fig = None
    cid = None
    xf = 50
    yf = 100
    dxf = 600
    dyf = 500
    fig_e = None
    cid_e = None
    xf_e = 50
    yf_e = 100
    dxf_e = 600
    dyf_e = 500

    def __init__(self):
        super(QWidget, self).__init__()
# контейнер для кнопок
        layoutbutton = QtWidgets.QHBoxLayout()
        self.font_button = QtWidgets.QPushButton(commondata.iconFont, 'Сменить шрифт')
        self.font_button.clicked.connect(self.font_click)
        layoutbutton.addWidget(self.font_button)
        self.load_button = QtWidgets.QPushButton(commondata.iconLoadFile, 'Загрузить')
        self.load_button.clicked.connect(self.load_click)
        layoutbutton.addWidget(self.load_button)
        self.calc_button = QtWidgets.QPushButton('Рассчитать')
        self.calc_button.clicked.connect(self.show_data)
        self.calc_button.setEnabled(False)
        layoutbutton.addWidget(self.calc_button)
        self.with_detail = QCheckBox('с подробностями')
        layoutbutton.addWidget(self.with_detail)
        self.with_detail.stateChanged.connect(self.detail_changed)
        layoutbutton.addWidget(QLabel(''), 2)
        self.excel_button = QtWidgets.QPushButton(commondata.iconExcel, '=> Excel')
        self.excel_button.clicked.connect(self.excel_click)
        layoutbutton.addWidget(self.excel_button)
        self.close_button = QtWidgets.QPushButton('Закончить')
        self.close_button.clicked.connect(self.close_click)
        layoutbutton.addWidget(self.close_button)
# Параметры
        panel_param = QtWidgets.QVBoxLayout()
        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Общее кол-во избирателей='))
        self.count = QSpinBox()
        self.count.setMaximum(1000000000)
        self.count.setMinimum(1)
        self.count.valueChanged.connect(self.changed)
        param.addWidget(self.count)
        param.addWidget(QLabel(''), 10)
        diagramma = QtWidgets.QPushButton('Избиратели')
        diagramma.clicked.connect(self.show_image_e)
        param.addWidget(diagramma)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Количество мандатов='))
        self.count_mandat = QSpinBox()
        self.count_mandat.setMaximum(10000)
        self.count_mandat.setMinimum(1)
        self.count_mandat.valueChanged.connect(self.changed)
        param.addWidget(self.count_mandat)
        param.addWidget(QLabel(''), 10)
        self.diagramma_button = QtWidgets.QPushButton('Мандаты')
        self.diagramma_button.clicked.connect(self.show_image)
        param.addWidget(self.diagramma_button)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Электоральный барьер (%)='))
        self.count_barier = QDoubleSpinBox()
        self.count_barier.setMaximum(100)
        self.count_barier.setMinimum(0)
        self.count_barier.valueChanged.connect(self.changed)
        param.addWidget(self.count_barier)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        self.kvota = QLabel('Квота Хэйра')
        param.addWidget(self.kvota)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        self.kvota_drup = QLabel('Квота Друпа')
        param.addWidget(self.kvota_drup)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)

# контейнер для дерева
        panel_table = QtWidgets.QVBoxLayout()
        self.root_model = QStandardItemModel()
        self.root_model.itemChanged.connect(self.on_change)
        self.table = QtWidgets.QTreeView()
        self.table.setRootIsDecorated(True)
        self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(False)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        self.table.header().setDefaultSectionSize(150)
        self.table.selectionModel().selectionChanged.connect(self.row_change)
        panel_table.addWidget(self.table)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком

# панель добавления, удаления строк
        panel_control = QtWidgets.QHBoxLayout()
        self.add_row = QtWidgets.QPushButton(commondata.iconCreate, 'Добавить партию в список')
        self.add_row.clicked.connect(self.add_row_click)
        panel_control.addWidget(self.add_row, 2)
        self.delete_row = QtWidgets.QPushButton(commondata.iconDelete, 'Удалить партию из списка')
        self.delete_row.clicked.connect(self.delete_row_click)
        self.delete_row.setEnabled(False)
        panel_control.addWidget(self.delete_row, 2)
        self.save_file = QtWidgets.QPushButton(commondata.iconSave, 'Сохранить (JSON)')
        self.save_file.clicked.connect(self.save_file_click)
        self.save_file.setEnabled(False)
        panel_control.addWidget(self.save_file)

# StatusBar
        statusbar = QtWidgets.QHBoxLayout()
        self.row_count = QLabel('')
        statusbar.addWidget(self.row_count)
        self.barier_count = QLabel('')
        statusbar.addWidget(self.barier_count)
        statusbar.addWidget(QLabel(''), 10)
        self.file_json = QLabel('')
        statusbar.addWidget(self.file_json)

# все соберем вместе
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutbutton)
        layout.addLayout(panel_param)
        layout.addLayout(panel_table, 10)
        layout.addLayout(panel_control)

        layout.addLayout(statusbar)
# финальный аккорд
        self.setLayout(layout)

        if commondata.settings.contains("data_directory"):
            self.select_directory = commondata.settings.value("data_directory", None)
        if commondata.settings.contains("data_file"):
            self.select_file = commondata.settings.value("data_file", None)
        if self.select_file == '':
            self.select_file = 'parties.json'
        if commondata.settings.contains("file_excel"):
            self.select_file_excel = commondata.settings.value("file_excel", '')
        if commondata.settings.contains('_xf'):
            self.xf = int(commondata.settings.value('_xf'))
        if commondata.settings.contains('_yf'):
            self.yf = int(commondata.settings.value('_yf'))
        if commondata.settings.contains('_dxf'):
            self.dxf = int(commondata.settings.value('_dxf'))
        if commondata.settings.contains('_dyf'):
            self.dyf = int(commondata.settings.value('_dyf'))
        if commondata.settings.contains('_xf_e'):
            self.xf_e = int(commondata.settings.value('_xf_e'))
        if commondata.settings.contains('_yf_e'):
            self.yf_e = int(commondata.settings.value('_yf_e'))
        if commondata.settings.contains('_dxf_e'):
            self.dxf_e = int(commondata.settings.value('_dxf_e'))
        if commondata.settings.contains('_dyf_e'):
            self.dyf_e = int(commondata.settings.value('_dyf_e'))

        if commondata.load_texts(self.select_file):
            self.file_json.setText(self.select_file)
        try:
            self.count.setValue(commondata.texts[0]["Общее кол-во избирателей"])
            self.count_mandat.setValue(commondata.texts[0]["Количество мандатов"])
            self.count_barier.setValue(commondata.texts[0]["Электоральный барьер"])
        except:
            pass
        self.show_data()

# изменить шрифт
    def font_click(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.setFont(font)

# загрузить файл с данными
    def load_click(self):
        dialog = QFileDialog(caption="Выбор файла с данными в JSON", filter="json (*.json)")
        if self.select_directory:
            dialog.setDirectory(self.select_directory)
        if self.select_file:
            dialog.FileName = self.select_file
        filename, filtr = dialog.getOpenFileName()
        if filename:
            self.select_file = filename
            self.select_directory = os.path.dirname(filename)
            self.file_json.setText(self.select_file)
            commondata.settings.setValue("data_directory", self.select_directory)
            commondata.settings.setValue("data_file", self.select_file)
            commondata.settings.sync()
            commondata.load_texts(filename)
            self.count.setValue(commondata.texts[0]["Общее кол-во избирателей"])
            self.count_mandat.setValue(commondata.texts[0]["Количество мандатов"])
            self.count_barier.setValue(commondata.texts[0]["Электоральный барьер"])
            self.save_file.setEnabled(False)
            self.show_data()

    def calc_summa_barier(self):
        """
        расчет суммы процентов голосов за партии, превысившие электоральный барьер
        """
        values = commondata.texts[1]
        summa = 0
        for key in values.keys():
            val = values[key]
            if val is not None and val >= self.count_barier.value():
                summa = summa + val
        return summa

    def kvota_haira(self, summa):
        """
        расчет квоты Хэйра
        :param summa: суммарное количество процентов голосов партий, превысивших электоральный барьер
        :return:
        """
        return summa / 100 * self.count.value() / self.count_mandat.value()

    def kvota_drupa(self, summa):
        """
        расчет квоты Друпа
        :param summa: суммарное количество процентов голосов партий, превысивших электоральный барьер
        :return:
        """
        return summa / 100 * self.count.value() / (self.count_mandat.value() + 1) + 1

    def show_last_row(self, index_column, is_float=False):
        val = 0
        for j in range(self.root_model.rowCount() - 1):
            ind = self.root_model.index(j, index_column)
            st = self.root_model.data(ind)
            if st is not None and st != '':
                val += float(st)
        ind = self.root_model.index(self.root_model.rowCount() - 1, index_column)
        if is_float:
            self.root_model.setData(ind, "%.3f" % val)
        else:
            self.root_model.setData(ind, str(int(val)))
        self.root_model.setData(ind, QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)

    def set_align(self, arow):
        for index_column in range(self.root_model.columnCount() -1):
            if index_column != 1 and index_column != 2:
                ind = self.root_model.index(arow, index_column)
                self.root_model.setData(ind, QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)

    def init_table(self):
        self.root_model.setRowCount(0)  # сбросить таблицу
        self.root_model.setColumnCount(0)  # сбросить все колонки
        # колонки
        stname = []
        stname.append('№№')  # 0
        stname.append('Партия')  # 1
        stname.append('Партия начальная')  # 2
        stname.append('%\n избир.')  # 3
        stname.append('Кол-во\n избирателей')  # 4

        stname.append('Кол-во\n по Хэйру')  # 5
        stname.append('Мандатов\n по Хэйру')  # 6
        stname.append('Дробная\n часть \nпо Хэйру')  # 7
        stname.append('Добавка \nпо \nХэйру')  # 8

        stname.append('Кол-во\n по Друпу')  # 9
        stname.append('Мандатов\n по Друпу')  # 10
        stname.append('Дробная\n часть \nпо Друпу')  # 11
        stname.append('Добавка \nпо \nДрупу')  # 12

        stname.append('Мандатов\n по Сент-Лагю')  # 13
        stname.append("Мандатов\n по Д'Ондту")  # 13
        stname.append("Мандатов\n по Империали")  # 14
        stname.append(' ')
        self.root_model.setHorizontalHeaderLabels(stname)
        self.table.setColumnHidden(2, True)
        self.table.setColumnHidden(5, not self.with_detail.isChecked())
        self.table.setColumnHidden(7, not self.with_detail.isChecked())
        self.table.setColumnHidden(8, not self.with_detail.isChecked())
        self.table.setColumnHidden(11, not self.with_detail.isChecked())
        self.table.setColumnHidden(9, not self.with_detail.isChecked())
        self.table.setColumnHidden(12, not self.with_detail.isChecked())

    def sort_indexes(self, dif):
        indexes = []
        while len(dif) > 0:
            index = -1
            # ищем максимум
            val_max = 0
            for key in dif.keys():
                val = dif[key]
                if val > val_max:
                    val_max = val
                    index = int(key)
            if index == -1:
                break
            indexes.append(index)  # номер строки
            dif.pop(str(index))
        return indexes

    def show_data(self, show_image=True):
        self.exist = False
        try:
            self.init_table()
            mandats_sl = self.method_sent_lagu(2, 1)
            mandats_on = self.method_sent_lagu(1, 1)
            mandats_im = self.method_sent_lagu(1, 2)
            values = commondata.texts[1]
            summa = self.calc_summa_barier()
            # рассчитать квоту Хэйра
            kvota_haira = self.kvota_haira(summa)
            kvota_drupa = self.kvota_drupa(summa)
            self.kvota_drup.setText('Квота Друпа = %.6f' % kvota_drupa)
            # заполняем таблицу
            dif = dict()
            dif_d = dict()
            val_d = 0
            n = 1
            count_mandat = 0
            count_barier = 0
            for key in values.keys():
                val = values[key]  # процент избирателей
                row = [QStandardItem(str(n)), QStandardItem(key), QStandardItem(key)]
                if val is not None and val >= self.count_barier.value():
                    row.append(QStandardItem(str(val)))  # процент избирателей
                    row.append(QStandardItem(str(int(val * self.count.value() / 100))))  # кол-во избирателей
                    val1 = val / 100 * self.count.value() / kvota_haira
                    row.append(QStandardItem("%.3f" % val1))  # дробное количество мандатов
                    row.append(QStandardItem(str(int(val1))))  # итоговый мандат
                    row.append(QStandardItem("%.3f" % (val1 - int(val1))))  # дробная часть мандатов
                    row.append(QStandardItem(''))  # будущая добавка по Хэйру
                    count_mandat = count_mandat + int(val1)
                    count_barier += 1
                    dif[str(n)] = val1 - int(val1)  # разности с номерами строк по ключам
                    val1 = val / 100 * self.count.value() / kvota_drupa
                    row.append(QStandardItem("%.3f" % val1))  # дробное количество мандатов по Друпу
                    row.append(QStandardItem(str(int(val1))))  # итоговый мандат
                    row.append(QStandardItem("%.3f" % (val1 - int(val1))))  # дробная часть мандатов
                    val_d += int(val1)  # целое количество мандатов по Друпу
                    dif_d[str(n)] = val1 - int(val1)  # разности с номерами строк по ключам
                else:
                    if val is not None:
                        row.append(QStandardItem(str(val)))
                    else:
                        row.append(QStandardItem(''))
                    row.append(QStandardItem(''))
                    row.append(QStandardItem(''))
                    row.append(QStandardItem(''))
                    row.append(QStandardItem(''))  # добавка
                    row.append(QStandardItem(''))  # итоговый мандат
                row.append(QStandardItem(''))  # для Сент-Лагю
                row.append(QStandardItem(''))  # невидимая колонка
                # только чтение
                commondata.row_only_read(row, [1, 3])  # 1 и 3 колонка корректируются
                self.root_model.appendRow(row)
                self.set_align(self.root_model.rowCount() - 1)
                n += 1
            # суммарная строка
            row = [QStandardItem('==='), QStandardItem('суммарно'), QStandardItem(''),
                   QStandardItem(str(summa)), QStandardItem(str(summa * self.count.value() / 100)),
                   QStandardItem(str(count_mandat))]
            commondata.row_only_read(row, [])  # в суммарной строке ничего не корректируется
            self.root_model.appendRow(row)
            self.set_align(self.root_model.rowCount() - 1)
            # ширина колонок по содержимому
            for j in range(0, self.root_model.columnCount()):
                self.table.resizeColumnToContents(j)
            self.kvota.setText(
                'Квота Хэйра = %.6f' % + kvota_haira +
                '; сумма % избирателей для квоты=' + str(summa) +
                '; кол-во избирателей для квоты=' + str(summa * self.count.value() / 100))
            # сортируем словарь
            indexes = self.sort_indexes(dif)
            # сформируем добавки
            for j in range(min(len(indexes), self.count_mandat.value()-count_mandat)):
                ind7 = self.root_model.index(indexes[j] - 1, 7)  # дробная часть мандатов
                ind6 = self.root_model.index(indexes[j] - 1, 6)  # мандаты по Хэйру
                ind5 = self.root_model.index(indexes[j] - 1, 5)  # количество смандатов с дробной частью
                ind8 = self.root_model.index(indexes[j] - 1, 8)  # добавки
                self.root_model.setData(ind8, '1')
                val = float(self.root_model.data(ind5)) - float(self.root_model.data(ind7)) + 1
                self.root_model.setData(ind6, str(int(val)))
            # закончим таблицу последней строкой
            self.show_last_row(5, True)
            self.show_last_row(8, False)
            self.show_last_row(7, True)
            self.show_last_row(6, False)

            # сортируем словарь
            indexes = self.sort_indexes(dif_d)
            # сформируем добавки
            while val_d < self.count_mandat.value():
                for j in range(min(len(indexes), self.count_mandat.value())):
                    if val_d >= self.count_mandat.value():
                        break
                    ind7 = self.root_model.index(indexes[j] - 1, 11)  # дробная часть мандатов
                    ind6 = self.root_model.index(indexes[j] - 1, 10)  # мандаты по Друпу
                    ind5 = self.root_model.index(indexes[j] - 1, 9)  # количество смандатов с дробной частью
                    ind8 = self.root_model.index(indexes[j] - 1, 12)  # добавки
                    if self.root_model.data(ind8) is not None and self.root_model.data(ind8) != '':
                        v = int(self.root_model.data(ind8))
                    else:
                        v = 0
                    v += 1
                    self.root_model.setData(ind8, str(v))
                    val = float(self.root_model.data(ind5)) - float(self.root_model.data(ind7)) + v
                    self.root_model.setData(ind6, str(int(val)))
                    val_d += 1
            for arow in range(self.root_model.rowCount() - 1):
                val = mandats_sl[arow]
                if val != 0:
                    ind13 = self.root_model.index(arow, 13)
                    self.root_model.setData(ind13, str(int(val)))
                val = mandats_on[arow]
                if val != 0:
                    ind14 = self.root_model.index(arow, 14)
                    self.root_model.setData(ind14, str(int(val)))
                val = mandats_im[arow]
                if val != 0:
                    ind15 = self.root_model.index(arow, 15)
                    self.root_model.setData(ind15, str(int(val)))

            # закончим таблицу последней строкой
            self.show_last_row(11, True)
            self.show_last_row(10, False)
            self.show_last_row(9, True)
            self.show_last_row(12, False)
            self.show_last_row(13, False)
            self.show_last_row(14, False)
            self.show_last_row(15, False)

            self.row_count.setText('всего партий=' + str(len(values)) + ';')
            self.barier_count.setText('прошедших барьер=' + str(count_barier) + ';')
            self.calc_button.setEnabled(False)
        except Exception as err:
            commondata.make_question(
                None, f'{err}', 'Ошибка при выводе таблицы', only_ok=True)
        self.exist = True
        if show_image and self.fig is not None:
            self.show_image()

    def on_change(self, item):
        if not self.exist:
            return
        values = commondata.texts[1]
        self.save_file.setEnabled(True)
        for j in range(self.root_model.rowCount()):
            if item == self.root_model.item(j, 3):
                ind_name = self.root_model.index(j, 1)
                ind_val = self.root_model.index(j, 3)
                if self.root_model.data(ind_val) == '':
                    values[self.root_model.data(ind_name)] = None
                else:
                    try:
                        val = float(self.root_model.data(ind_val))
                        values[self.root_model.data(ind_name)] = val
                    except Exception as err:
                        commondata.make_question(
                            None, f'{err}', 'Ошибка ввода числа с десятичными знаками',
                            self.root_model.data(ind_val), only_ok=True)
                self.show_data()
                break
            if item == self.root_model.item(j, 1):
                ind_name = self.root_model.index(j, 2)
                ind_val = self.root_model.index(j, 1)
                old_key = self.root_model.data(ind_name)
                new_key = self.root_model.data(ind_val)
                values[new_key] = values.pop(old_key)
                self.show_data()
                break

    def changed(self):
        if self.exist:
            self.calc_button.setEnabled(True)
            self.save_file.setEnabled(True)
            commondata.texts[0]["Общее кол-во избирателей"] = self.count.value()
            commondata.texts[0]["Количество мандатов"] = self.count_mandat.value()
            commondata.texts[0]["Электоральный барьер"] = self.count_barier.value()

    def close_click(self):
        self.close_fig()
        self.close_fig_e()
        commondata.settings.setValue('_xf', self.xf)
        commondata.settings.setValue('_yf', self.yf)
        commondata.settings.setValue('_dxf', self.dxf)
        commondata.settings.setValue('_dyf', self.dyf)

        commondata.settings.setValue('_xf_e', self.xf_e)
        commondata.settings.setValue('_yf_e', self.yf_e)
        commondata.settings.setValue('_dxf_e', self.dxf_e)
        commondata.settings.setValue('_dyf_e', self.dyf_e)
        commondata.settings.sync()
        self.formaparent.close()
        QApplication.quit()

    def add_row_click(self):
        values = commondata.texts[1]
        st = 'Партия ' + str(self.root_model.rowCount())
        values[st] = None
        self.show_data()

    def delete_row_click(self):
        row = self.table.selectionModel().selectedRows()[0].row()
        ind_val = self.root_model.index(row, 1)
        key = self.root_model.data(ind_val)
        commondata.texts[1].pop(key)
        self.show_data()

    def row_change(self, new, old):
        if self.exist:
            row = self.table.selectionModel().selectedRows()[0].row()
            self.delete_row.setEnabled(row != self.root_model.rowCount() - 1)

    def detail_changed(self):
        self.show_data(False)

    def excel_click(self):
        path = commondata.export_to_excel_xls(self.root_model, self.select_file_excel)
        if path:
            self.select_file_excel = path
            commondata.settings.setValue("file_excel", path)
            commondata.settings.sync()

    def save_file_click(self):
        path = commondata.get_filename_for_write(self.select_file)
        if path:
            path = os.path.splitext(path)[0] + '.json'
            self.select_file = path
            self.select_directory = os.path.dirname(path)
            commondata.settings.setValue("data_directory", self.select_directory)
            commondata.settings.setValue("data_file", self.select_file)
            commondata.settings.sync()
            try:
                f = open(path, 'wt', encoding='utf-8')  # только запись и текстовый файл
                with f:
                    txt = json.dumps(commondata.texts, indent=4, ensure_ascii=False)
                    f.write(txt)
                    self.save_file.setEnabled(False)
            except Exception as err:
                commondata.make_question(None, path + f'\n {err}', 'Ошибка записи в файл', txt, only_ok=True)

    def fig_draw(self, event):
        self.fig.tight_layout()

    def fig_draw_e(self, event):
        self.fig_e.tight_layout()

    def figure_close(self, event):
        if self.exist:
            self.exist = False
            self.fig = self.close_fig()
            self.exist = True

    def figure_close_e(self, event):
        if self.exist:
            self.exist = False
            self.fig_e = self.close_fig_e()
            self.exist = True

    def close_fig(self):
        try:
            if self.fig != None:
                mngr = plt.get_current_fig_manager()
                geom = mngr.window.geometry()
                self.xf, self.yf, self.dxf, self.dyf = geom.getRect()  # расположение фигуры
                self.fig.canvas.mpl_disconnect(self.cid)
                plt.close(self.fig)  # все закрывается
                self.fig = None
        except:
            pass
        return self.fig

    def close_fig_e(self):
        try:
            if self.fig_e != None:
                mngr = plt.get_current_fig_manager()
                geom = mngr.window.geometry()
                self.xf_e, self.yf_e, self.dxf_e, self.dyf_e = geom.getRect()  # расположение фигуры
                self.fig_e.canvas.mpl_disconnect(self.cid_e)
                plt.close(self.fig_e)  # все закрывается
                self.fig_e = None
        except:
            pass
        return self.fig_e

    def show_image_e(self):
        try:
            if self.fig_e != None:
                self.close_fig_e()
            self.fig_e = plt.figure(
                    frameon=True, num='Избиратели (из файла ' + self.select_file + ')', clear=True)
            self.cid_e = self.fig_e.canvas.mpl_connect('close_event', self.figure_close_e)
            self.fig_e.canvas.mpl_connect('resize_event', self.fig_draw_e)
            try:
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.xf_e, self.yf_e, self.dxf_e, self.dyf_e)
            except:
                pass

            x = []
            y1 = []
            for j in range(self.root_model.rowCount() - 1):
                ind1 = self.root_model.index(j, 1)  # название партий
                ind3 = self.root_model.index(j, 3)  # процент избирателей
                x.append(self.root_model.data(ind1))
                y1.append(float(self.root_model.data(ind3)))
            # отсортируем по возрастанию
            for i in range(len(x)):
                minimum = i
                for j in range(i +1, len(x)):
                    if y1[j] < y1[minimum]:
                        minimum = j
                x[minimum], x[i] = x[i], x[minimum]
                y1[minimum], y1[i] = y1[i], y1[minimum]

            ax = plt.subplot(1, 1, 1)
            ax.set_title('Проценты избирателей')
            ax.set_ylabel('------------ Партии ------------')
            ax.set_xlabel('% избирателей')
            ax.set_xlim(xmin=0, xmax=100)
            for i, v in enumerate(y1):
                if v != 0:
                    ax.text(v + 1, i - 0.1, str(v), color='red')
            ax.barh(x, y1, height = 0.75, color='r', alpha=0.5)
            plt.show()
        except Exception as e:
            QMessageBox.information(None, 'Ошибки', f"{e}", buttons=QtWidgets.QMessageBox.Close)

    def show_image(self):
        try:
            if self.fig != None:
                self.close_fig()
            self.fig = plt.figure(
                    frameon=True, num='Информация из файла ' + self.select_file, clear=True)
            self.cid = self.fig.canvas.mpl_connect('close_event', self.figure_close)
            self.fig.canvas.mpl_connect('resize_event', self.fig_draw)
            try:
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.xf, self.yf, self.dxf, self.dyf)
            except:
                pass

            x = []
            y = []
            y_d = []
            y_cl = []
            y_o = []
            y_i = []
            for j in range(self.root_model.rowCount() - 1):
                ind1 = self.root_model.index(j, 1)  # название партий
                ind6 = self.root_model.index(j, 6)  # мандаты по Хэйру
                ind10 = self.root_model.index(j, 10)  # мандаты по Друпу
                ind13 = self.root_model.index(j, 13)  # мандаты по Сент-Лагю
                ind14 = self.root_model.index(j, 14)  # мандаты по Д'Онндту
                ind15 = self.root_model.index(j, 15)  # мандаты по Империали
                x.append(self.root_model.data(ind1))
                val = self.root_model.data(ind6)
                if val is None or val == '':
                    val = 0
                else:
                    val = int(val)
                y.append(val)
                val = self.root_model.data(ind10)
                if val is None or val == '':
                    val = 0
                else:
                    val = int(val)
                y_d.append(val)
                val = self.root_model.data(ind13)
                if val is None or val == '':
                    val = 0
                else:
                    val = int(val)
                y_cl.append(val)
                val = self.root_model.data(ind14)
                if val is None or val == '':
                    val = 0
                else:
                    val = int(val)
                y_o.append(val)
                val = self.root_model.data(ind15)
                if val is None or val == '':
                    val = 0
                else:
                    val = int(val)
                y_i.append(val)
            # отсортируем по возрастанию
            for i in range(len(x)):
                minimum = i
                for j in range(i +1, len(x)):
                    if y[j] < y[minimum]:
                        minimum = j
                y[minimum], y[i] = y[i], y[minimum]
                y_d[minimum], y_d[i] = y_d[i], y_d[minimum]
                y_o[minimum], y_o[i] = y_o[i], y_o[minimum]
                y_i[minimum], y_i[i] = y_i[i], y_i[minimum]
                y_cl[minimum], y_cl[i] = y_cl[i], y_cl[minimum]
                x[minimum], x[i] = x[i], x[minimum]

            ax = plt.subplot(1, 1, 1)
            # ax.set_title('Полученные мандаты')
            # ax.set_ylabel('------------ Партии ------------')
            # ax.set_xlabel('Количество полученных мандатов')
            # ax.set_xlim(xmin=0, xmax=self.count_mandat.value())
            # for i, v in enumerate(y):
            #     if v != 0:
            #         ax.text(v + 1, i - 0.2, str(v), color='blue')
            # for i, v in enumerate(y_d):
            #     if v != 0:
            #         ax.text(v + 1, i - 0.2, str(v), color='green')
            # ax.barh(x, y, height = 0.75, label='по Хэйру', color='blue')
            # ax.barh(x, y_d, height = 0.75, label='по Друпу', color='green')
            # ax.legend(loc='best', frameon=False)

            data = {'по Хэйру': y, 'По Друпу': y_d, 'По Сент-Лагю': y_cl, "По Д'Ондту": y_o, "По Империали": y_i}
            dx = pan.DataFrame(data, columns=['по Хэйру', 'По Друпу', 'По Сент-Лагю', "По Д'Ондту", "По Империали"],
                               index=x)
            dx.plot(kind='barh', title='Полученные мандаты', xlim=(0, self.count_mandat.value()),
                    ax=ax)
            ax.set_ylabel('------------ Партии ------------')
            ax.set_xlabel('Количество полученных мандатов')
            # for i, v in enumerate(y):
            #     if v != 0:
            #         ax.text(v + 1, i - 0.2, str(v), color='blue')
            # for i, v in enumerate(y_d):
            #     if v != 0:
            #         ax.text(v + 1, i - 0.2, str(v), color='green')
            # ax.barh(x, y, height = 0.75, label='по Хэйру', color='blue')
            # ax.barh(x, y_d, height = 0.75, label='по Друпу', color='green')
            # ax.grid(True)
            # ax.legend(loc='best', frameon=False)

            plt.show()
            # plt.tight_layout()
        except Exception as e:
            QMessageBox.information(None, 'Ошибки', f"{e}", buttons=QtWidgets.QMessageBox.Close)

    def method_sent_lagu(self, k, d):
        """
        метод Сент-Лагю
        :return:
        """
        values = commondata.texts[1]
        summa = self.calc_summa_barier()  # сумма процентов партий, одолевших электоральный барьер
        voters = []  # избиратели
        mandats = []
        for key in values.keys():
            val = values[key]  # процент избирателей
            if val is not None and val >= self.count_barier.value():
                voters.append(val * self.count.value() / 100)
            else:
                voters.append(0)  # не прошедших барьер не считаем
            mandats.append(0)

        count_mandats = 0
        while count_mandats < self.count_mandat.value():
            dif = dict()
            for i in range(len(voters)):
                if voters[i] == 0:
                    continue  # пропускаем
                dif[str(i + 1)] = voters[i] / (k * mandats[i] + d)
            # сортируем словарь
            indexes = self.sort_indexes(dif)
            mandats[indexes[0] - 1] = mandats[indexes[0] - 1] + 1
            count_mandats += 1

        return mandats

