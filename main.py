from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import tform
import commondata

# Press the green button in the gutter to run the script.
app = QtWidgets.QApplication(sys.argv)
commondata.settings = QtCore.QSettings("Демидов", "Расчет мандатов")

if __name__ == '__main__':
    win = tform.Form()
    win.setWindowTitle('Расчет мандатов')
    win.show()

    sys.exit(app.exec())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
