from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QApplication, QFontDialog, QInputDialog, QStyle
import commondata
import modeler

class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setFont(QtGui.QFont('Arial', 11))
        commondata.iconCreate = QIcon()
        commondata.iconCreate.addFile('Добавить.bmp')
        commondata.iconDelete = QIcon()
        commondata.iconDelete.addFile('удалить.bmp')
        commondata.iconSave = QIcon()
        commondata.iconSave = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        commondata.iconLoadFile = QIcon()
        commondata.iconLoadFile = self.style().standardIcon(QStyle.SP_FileLinkIcon)
        commondata.iconFont = QIcon()
        commondata.iconFont.addFile('font.bmp')
        commondata.iconExcel = QIcon()
        commondata.iconExcel.addFile('EXCEL.bmp')

# запомненные настройки
        if commondata.settings.contains("CalcMandat"):
            self.setGeometry(commondata.settings.value("CalcMandat"))
        else:
            self.resize(commondata.width_form, commondata.height_form)
        if commondata.settings.contains("CalcMandatFont"):
            self.setFont(commondata.settings.value("CalcMandatFont"))
# основная форма
        self.widget = QWidget()
        self.modeler = modeler.TModeler()
        self.modeler.formaparent = self
        self.setCentralWidget(self.modeler)
        self.show()

    # закрыть программу
    def closeEvent(self, evt):
        commondata.settings.setValue("CalcMandat", self.geometry())
        commondata.settings.setValue("CalcMandatFont", self.font())
        commondata.settings.sync()
