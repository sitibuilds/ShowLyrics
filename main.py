import sys, os
from ui import QApplication, MainWindow, ApplicationAttributes


class CONSTANTS:
    __slots__ = ()
    SCRIPT_PATH = os.path.realpath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow(None)

    window.setMinimumSize(100, 100)
    stylesheet = ""
    with open(os.path.join(CONSTANTS.SCRIPT_DIR, "styles", "global.qss"), "r") as f:
        stylesheet = f.read()

    app.setStyleSheet(stylesheet)

    window.show()
    sys.exit(app.exec())
