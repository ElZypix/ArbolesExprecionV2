import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt


class CompiladorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Cargar la interfaz que tienes en la carpeta Gui
        uic.loadUi("Gui/interfaz.ui", self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())