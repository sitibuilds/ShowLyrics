import sys, os
from ui import (
    QApplication,
    MainWindow,
    ApplicationAttributes,
)

class CONSTANTS:
    __slots__ = ()
    SCRIPT_PATH = os.path.realpath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow(None)
    window.show()

    sys.exit(app.exec())
