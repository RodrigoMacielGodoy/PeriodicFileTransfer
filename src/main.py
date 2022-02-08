import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()

if __name__ == "__main__":
    main()