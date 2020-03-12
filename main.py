import View.MainWindow
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = View.MainWindow.MainWindow()
    sys.exit(app.exec_())