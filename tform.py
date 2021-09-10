from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QApplication, QFontDialog, QInputDialog
import commondata
import modeler

class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setFont(QtGui.QFont('Arial', 11))
# запомненные настройки
        if commondata.settings.contains("CalcMandat"):
            self.setGeometry(commondata.settings.value("CalcMandat"))
        else:
            self.resize(commondata.width_form, commondata.height_form)
        if commondata.settings.contains("CalcMandatFont"):
            self.setFont(commondata.settings.value("CalcMandatFont"))
# основная форма
        self.widget = QWidget()
        self.modeler = modeler.TModeler(self.widget)
        self.modeler.formaparent = self
        self.setCentralWidget(self.modeler)
        self.show()

    # закрыть программу
    def closeEvent(self, evt):
        commondata.settings.setValue("CalcMandat", self.geometry())
        commondata.settings.setValue("CalcMandatFont", self.font())
        commondata.settings.sync()
