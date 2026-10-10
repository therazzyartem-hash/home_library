"""Точка входа: окно входа, затем главное окно библиотеки."""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QDialog

from main_window import MainWindow
from models import Session
from storage import BookStorage, SessionReport
from widgets import LoginDialog, Theme


class Application:
    """Запуск приложения и пути к файлам данных."""

    BASE_DIR = Path(__file__).resolve().parent
    BOOKS_FILE = BASE_DIR / "data" / "books.csv"
    REPORT_FILE = BASE_DIR / "report.txt"
    LIBRARY_NAME = "Домашняя библиотека"

    @staticmethod
    def run() -> int:
        app = QApplication(sys.argv)
        app.setStyleSheet(Theme.stylesheet())

        login = LoginDialog()
        if login.exec() != QDialog.DialogCode.Accepted:
            return 0

        storage = BookStorage(Application.BOOKS_FILE)
        window = MainWindow(Session(login.login), storage.load(Application.LIBRARY_NAME),
                            storage, SessionReport(Application.REPORT_FILE))
        window.show()
        return app.exec()


if __name__ == "__main__":
    sys.exit(Application.run())
