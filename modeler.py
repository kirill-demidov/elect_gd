from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog, QFontDialog, QInputDialog,QCheckBox, QApplication,\
    QSpinBox
import os

import commondata


class TModeler(QWidget):
    formaparent = None
    select_directory = ''
    select_file = ''
    def __init__(self, parent):
        super(QWidget, self).__init__()
# контейнер для кнопок
        layoutbutton = QtWidgets.QHBoxLayout()
        self.font_button = QtWidgets.QPushButton('Сменить шрифт')
        self.font_button.clicked.connect(self.font_click)
        layoutbutton.addWidget(self.font_button)
        self.load_button = QtWidgets.QPushButton('Загрузить')
        self.load_button.clicked.connect(self.load_click)
        layoutbutton.addWidget(self.load_button)
        self.calc_button = QtWidgets.QPushButton('Рассчитать')
        self.calc_button.clicked.connect(self.show_parameters)
        layoutbutton.addWidget(self.calc_button)
        self.with_detail = QCheckBox('с подробностями')
        # layoutbutton.addWidget(self.with_detail)
        layoutbutton.addWidget(QLabel(''), 2)
        self.close_button = QtWidgets.QPushButton('Закончить')
        self.close_button.clicked.connect(QApplication.quit)
        layoutbutton.addWidget(self.close_button)
# Параметры
        panel_param = QtWidgets.QVBoxLayout()
        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Общее кол-во избирателей='))
        self.count = QSpinBox()
        self.count.setMaximum(100000000)
        self.count.setMinimum(1)
        param.addWidget(self.count)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Количество мандатов='))
        self.count_mandat = QSpinBox()
        self.count_mandat.setMaximum(1000)
        self.count_mandat.setMinimum(1)
        param.addWidget(self.count_mandat)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Электоральный барьер (%)='))
        self.count_min = QSpinBox()
        self.count_min.setMaximum(100)
        self.count_min.setMinimum(1)
        param.addWidget(self.count_min)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        self.kvota = QLabel('Квота Хэйра')
        param.addWidget(self.kvota)
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
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        self.table.header().setDefaultSectionSize(150)
        panel_table.addWidget(self.table)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком
# StatusBar
        statusbar = QtWidgets.QHBoxLayout()
        self.row_count = QLabel('')
        statusbar.addWidget(self.row_count)

# все соберем вместе
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutbutton)
        layout.addLayout(panel_param)
        layout.addLayout(panel_table, 10)

        layout.addLayout(statusbar)
# финальный аккорд
        self.setLayout(layout)

        if commondata.settings.contains("data_directory"):
            self.select_directory = commondata.settings.value("data_directory", None)
        if commondata.settings.contains("data_file"):
            self.select_file = commondata.settings.value("data_file", None)
        if self.select_file == '':
            self.select_file = 'parties.json'
        commondata.load_texts(self.select_file)
        try:
            self.count.setValue(commondata.texts[0]["Общее кол-во избирателей"])
            self.count_mandat.setValue(commondata.texts[0]["Количество мандатов"])
            self.count_min.setValue(commondata.texts[0]["Электоральный барьер"])
        except:
            pass
        self.show_parameters()


# изменить шрифт
    def font_click(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.setFont(font)

# загрузить файл с данными
    def load_click(self):
        dialog = QFileDialog(caption="Выбор файла с данными в CSV", filter="csv (*.csv)")
        if self.select_directory:
            dialog.setDirectory(self.select_directory)
        if self.select_file:
            dialog.FileName = self.select_file
        filename, filtr = dialog.getOpenFileName()
        if filename:
            self.select_file = filename
            self.select_directory = os.path.dirname(filename)
            commondata.settings.setValue("data_directory", self.select_directory)
            commondata.settings.setValue("data_file", self.select_file)
            commondata.settings.sync()
            commondata.load_texts(filename)
            self.count.setValue(commondata.texts[0]["Общее кол-во избирателей"])
            self.count_mandat.setValue(commondata.texts[0]["Количество мандатов"])
            self.count_min.setValue(commondata.texts[0]["Электоральный барьер"])
            self.show_parameters()

    def show_parameters(self):
            try:
                self.root_model.setRowCount(0)  # сбросить таблицу
                self.root_model.setColumnCount(0)  # сбросить все колонки
                # колонки
                stname = []
                stname.append('№№')
                stname.append('Партия')
                stname.append('% избир.')
                stname.append('Кол-во избир.')
                stname.append('Кол-во мандатов')
                stname.append('Дробная часть')
                stname.append('Добавка')
                stname.append('Итог мандатов')
                self.root_model.setHorizontalHeaderLabels(stname)
                values = commondata.texts[1]
                summa = 0
                summa_count = 0
                # рассчитать квоту Хэйра
                for key in values.keys():
                    val = values[key]
                    if val >= self.count_min.value():
                        summa = summa + val
                        summa_count = summa_count + val * self.count.value() / 100
                kvota = summa * self.count.value() /100 / self.count_mandat.value()

                # заполняем таблицу
                dif = dict()
                n = 1
                count_mandat = 0
                for key in values.keys():
                    val = values[key]  # процент избирателей
                    row = [QStandardItem(str(n)), QStandardItem(key), QStandardItem(str(val))]
                    if val >= self.count_min.value():
                        row.append(QStandardItem(str(int(val * self.count.value() / 100))))
                        val1 = val * self.count.value() / 100 / kvota
                        row.append(QStandardItem("%.3f" % val1))
                        count_mandat = count_mandat + int(val1)
                        row.append(QStandardItem("%.3f" % (val1 - int(val1))))
                        dif[str(n)] = val1 - int(val1) # разности с номерами строк по ключам
                        row.append(QStandardItem(''))  # добавка
                        row.append(QStandardItem(str(int(val1))))  # итоговый мандат
                    else:
                        row.append(QStandardItem(''))
                        row.append(QStandardItem(''))
                        row.append(QStandardItem(''))
                        row.append(QStandardItem(''))  # добавка
                        row.append(QStandardItem(''))  # итоговый мандат
                    # только чтение
                    commondata.row_only_read(row, [2])
                    self.root_model.appendRow(row)
                    n += 1
                # суммарная строка
                row = [QStandardItem('==='), QStandardItem('суммарно'),
                       QStandardItem(str(summa)), QStandardItem(str(summa_count)),
                       QStandardItem(str(count_mandat))]
                self.root_model.appendRow(row)
                # ширина колонок по содержимому
                for j in range(0, self.root_model.columnCount()):
                    self.table.resizeColumnToContents(j)
                self.kvota.setText(
                    'Квота Хэйра = %.6f' % + kvota +
                    '; сумма % избирателей для квоты=' + str(summa) +
                    '; кол-во избирателей для квоты=' + str(summa * self.count.value() /100))
                # сортируем словарь
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
                    indexes.append(index) # номер строки
                    dif.pop(str(index))
                # сформируем добавки
                for j in range(min(len(indexes), self.count_mandat.value()-count_mandat)):
                    ind7 = self.root_model.index(indexes[j] - 1, 7)
                    ind6 = self.root_model.index(indexes[j] - 1, 6)
                    ind5 = self.root_model.index(indexes[j] - 1, 5)
                    ind4 = self.root_model.index(indexes[j] - 1, 4)
                    self.root_model.setData(ind6, '1')
                    val = float(self.root_model.data(ind4)) - float(self.root_model.data(ind5)) + 1
                    self.root_model.setData(ind7, str(int(val)))
                # закончим таблицу
                val5 = 0
                val6 = 0
                val7 = 0
                for j in range(self.root_model.rowCount() - 1):
                    ind7 = self.root_model.index(j, 7)
                    ind6 = self.root_model.index(j, 6)
                    ind5 = self.root_model.index(j, 5)
                    st = self.root_model.data(ind5)
                    if st != '':
                        val5 += float(st)
                    st = self.root_model.data(ind6)
                    if st != '':
                        val6 += float(st)
                    st = self.root_model.data(ind7)
                    if st != '':
                        val7 += float(st)
                ind7 = self.root_model.index(self.root_model.rowCount() - 1, 7)
                ind6 = self.root_model.index(self.root_model.rowCount() - 1, 6)
                ind5 = self.root_model.index(self.root_model.rowCount() - 1, 5)
                self.root_model.setData(ind7, str(int(val7)))
                self.root_model.setData(ind6, str(int(val6)))
                self.root_model.setData(ind5, "%.3f" % val5)

            except:
                pass

    def on_change(self, item):
        for j in range(self.root_model.rowCount()):
            if item == self.root_model.item(j, 2):
                ind_name = self.root_model.index(j, 1)
                ind_val = self.root_model.index(j, 2)
                commondata.texts[1][self.root_model.data(ind_name)] = float(self.root_model.data(ind_val))
                self.show_parameters()
                break
