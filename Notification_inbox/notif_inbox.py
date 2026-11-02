
import sys

from PySide6.QtWidgets import QApplication
from ui.main_window import NotificationInbox


def main():
    app = QApplication(sys.argv)

    window = NotificationInbox()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
