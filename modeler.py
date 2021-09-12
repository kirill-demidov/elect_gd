from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog, QFontDialog, QCheckBox, QApplication, QSpinBox, \
    QDoubleSpinBox
import os

import commondata


class TModeler(QWidget):
    formaparent = None
    select_directory = ''
    select_file = ''
    exist = False

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
        self.count.setMaximum(100000000)
        self.count.setMinimum(1)
        self.count.valueChanged.connect(self.changed)
        param.addWidget(self.count)
        param.addWidget(QLabel(''), 10)
        panel_param.addLayout(param)
        panel_param.addLayout(param)

        param = QtWidgets.QHBoxLayout()
        param.addWidget(QLabel('Количество мандатов='))
        self.count_mandat = QSpinBox()
        self.count_mandat.setMaximum(1000)
        self.count_mandat.setMinimum(1)
        self.count_mandat.valueChanged.connect(self.changed)
        param.addWidget(self.count_mandat)
        param.addWidget(QLabel(''), 10)
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
        self.save_file = QtWidgets.QPushButton(commondata.iconSave, 'Сохранить')
        self.save_file.setEnabled(False)
        panel_control.addWidget(self.save_file)

# StatusBar
        statusbar = QtWidgets.QHBoxLayout()
        self.row_count = QLabel('')
        statusbar.addWidget(self.row_count)
        self.barier_count = QLabel('')
        statusbar.addWidget(self.barier_count)
        statusbar.addWidget(QLabel(''), 10)

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
        commondata.load_texts(self.select_file)
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

    def show_last_row(self, index_column, is_float=False):
        val = 0
        for j in range(self.root_model.rowCount() - 1):
            ind = self.root_model.index(j, index_column)
            st = self.root_model.data(ind)
            if st != '':
                val += float(st)
        ind = self.root_model.index(self.root_model.rowCount() - 1, index_column)
        if is_float:
            self.root_model.setData(ind, "%.3f" % val)
        else:
            self.root_model.setData(ind, str(int(val)))
        self.root_model.setData(ind, QtCore.Qt.AlignRight, QtCore.Qt.TextAlignmentRole)

    def set_align(self, arow):
        for index_column in range(10):
            if index_column != 1 and index_column != 2 and index_column != 9:
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
        stname.append('Кол-во\n мандатов')  # 5
        stname.append('Мандатов\n по Хэйру')  # 6
        stname.append('Дробная\n часть')  # 7
        stname.append('Добавка')  # 8
        stname.append(' ')
        self.root_model.setHorizontalHeaderLabels(stname)
        self.table.setColumnHidden(2, True)
        self.table.setColumnHidden(7, not self.with_detail.isChecked())
        self.table.setColumnHidden(8, not self.with_detail.isChecked())

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

    def show_data(self):
        self.exist = False
        try:
            self.init_table()
            values = commondata.texts[1]
            summa = self.calc_summa_barier()
            # рассчитать квоту Хэйра
            kvota_haira = self.kvota_haira(summa)
            # заполняем таблицу
            dif = dict()
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
            self.row_count.setText('всего партий=' + str(len(values)) + ';')
            self.barier_count.setText('прошедших барьер=' + str(count_barier) + ';')
            self.calc_button.setEnabled(False)
        except Exception as err:
            commondata.make_question(
                None, f'{err}', 'Ошибка при выводе таблицы', only_ok=True)
        self.exist = True

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

    def close_click(self):
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
        self.show_data()

    def excel_click(self):
        commondata.export_to_excel_xls(self.root_model, 'Выборы')
