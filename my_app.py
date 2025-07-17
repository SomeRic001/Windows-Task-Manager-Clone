import psutil
import PyQt5
import pyqtgraph
import sys
from PyQt5.QtWidgets import QApplication, QWidget

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Deez Nuts")
    window.resize(400,300)
    window.show()
    sys.exit(app.exec_())