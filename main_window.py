"""Главное окно приложения."""
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from models import Book, Library, Session
from storage import BookStorage, SessionReport
from widgets import (
    ActionButton, AppStatusBar, BookFormDialog, BookTable, GenreComboBox, HeaderLabel,
    SearchLineEdit, SortComboBox, StatsLabel,
)


class MainWindow(QMainWindow):
    """Окно со списком книг, фильтрами и действиями над книгами."""

    def __init__(self, session: Session, library: Library, storage: BookStorage,
                 report: SessionReport):
        super().__init__()
        self.session = session
        self.library = library
        self.storage = storage
        self.report = report

        self.setWindowTitle(f"Домашняя библиотека — {session.login}")
        self.resize(1000, 620)
        self.setMinimumSize(780, 480)

        self.__search = SearchLineEdit()
        self.__genre = GenreComboBox()
        self.__sort = SortComboBox()
        self.__descending = QCheckBox("По убыванию")
        self.__table = BookTable()
        self.__stats = StatsLabel()
        self.setStatusBar(AppStatusBar())

        self.__build_layout()
        self.__connect_signals()
        self.refresh()

    # --- геттеры / сеттеры -------------------------------------------------
    @property
    def session(self) -> Session:
        return self.__session

    @session.setter
    def session(self, value: Session) -> None:
        self.__session = value

    @property
    def library(self) -> Library:
        return self.__library

    @library.setter
    def library(self, value: Library) -> None:
        self.__library = value

    @property
    def storage(self) -> BookStorage:
        return self.__storage

    @storage.setter
    def storage(self, value: BookStorage) -> None:
        self.__storage = value

    @property
    def report(self) -> SessionReport:
        return self.__report

    @report.setter
    def report(self, value: SessionReport) -> None:
        self.__report = value

    # --- построение интерфейса ---------------------------------------------
    def __build_layout(self) -> None:
        filters = QHBoxLayout()
        filters.setSpacing(10)
        filters.addWidget(self.__search, stretch=1)
        filters.addWidget(self.__genre)
        filters.addWidget(self.__sort)
        filters.addWidget(self.__descending)

        self.__add_button = ActionButton("Добавить", "Добавить новую книгу (Ctrl+N)")
        self.__edit_button = ActionButton("Изменить", "Изменить выбранную книгу (Enter)")
        self.__toggle_button = ActionButton("Прочитана / нет", "Переключить отметку о прочтении (Пробел)")
        self.__delete_button = ActionButton("Удалить", "Удалить выбранную книгу (Delete)", danger=True)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.__stats, stretch=1)
        actions.addWidget(self.__add_button)
        actions.addWidget(self.__edit_button)
        actions.addWidget(self.__toggle_button)
        actions.addWidget(self.__delete_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)
        layout.addWidget(HeaderLabel(f"📚 {self.library.name}"))
        layout.addLayout(filters)
        layout.addWidget(self.__table, stretch=1)
        layout.addLayout(actions)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def __connect_signals(self) -> None:
        self.__search.textChanged.connect(self.refresh)
        self.__genre.currentIndexChanged.connect(self.refresh)
        self.__sort.currentIndexChanged.connect(self.refresh)
        self.__descending.toggled.connect(self.refresh)
        self.__add_button.clicked.connect(self.add_book)
        self.__edit_button.clicked.connect(self.edit_book)
        self.__toggle_button.clicked.connect(self.toggle_read)
        self.__delete_button.clicked.connect(self.delete_book)
        self.__table.edit_requested.connect(self.edit_book)
        self.__table.delete_requested.connect(self.delete_book)
        self.__table.toggle_requested.connect(self.toggle_read)

    # --- логика ------------------------------------------------------------
    def visible_books(self) -> List[Book]:
        books = self.library.search(self.__search.text().strip(), self.__genre.current_genre)
        return Library.sorted_by(books, self.__sort.attribute, self.__descending.isChecked())

    def refresh(self) -> None:
        self.__genre.set_genres(self.library.genres())
        books = self.visible_books()
        self.__table.show_books(books)
        self.__stats.setText(
            f"показано {len(books)} из {len(self.library)} · прочитано {self.library.read_count()} · "
            f"всего страниц {self.library.total_pages()}")

    def selected_book(self) -> Optional[Book]:
        book_id = self.__table.selected_book_id
        if book_id is None:
            self.statusBar().showMessage("Сначала выберите книгу в таблице")
            return None
        return self.library.find_by_id(book_id)

    def save(self) -> None:
        self.storage.save(self.library)

    def add_book(self) -> None:
        dialog = BookFormDialog(self.library.genres(), parent=self)
        if dialog.exec() != BookFormDialog.DialogCode.Accepted:
            return
        try:
            self.library.add(dialog.result_book)
        except ValueError as error:
            QMessageBox.warning(self, "Дубликат", str(error))
            return
        self.save()
        self.refresh()
        self.__table.selected_book_id = dialog.result_book.book_id
        self.statusBar().showMessage(f"Добавлена книга {dialog.result_book}")

    def edit_book(self) -> None:
        book = self.selected_book()
        if book is None:
            return
        dialog = BookFormDialog(self.library.genres(), book, parent=self)
        if dialog.exec() != BookFormDialog.DialogCode.Accepted:
            return
        try:
            self.library.update(dialog.result_book)
        except ValueError as error:
            QMessageBox.warning(self, "Дубликат", str(error))
            return
        self.save()
        self.refresh()
        self.statusBar().showMessage(f"Изменена книга {dialog.result_book}")

    def toggle_read(self) -> None:
        book = self.selected_book()
        if book is None:
            return
        book.toggle_read()
        self.save()
        self.refresh()
        state = "прочитана" if book.is_read else "не прочитана"
        self.statusBar().showMessage(f"{book}: {state}")

    def delete_book(self) -> None:
        book = self.selected_book()
        if book is None:
            return
        answer = QMessageBox.question(self, "Удаление", f"Удалить книгу {book}?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.library.remove(book.book_id)
        self.save()
        self.refresh()
        self.statusBar().showMessage(f"Удалена книга {book}")

    # --- переопределённые события окна -------------------------------------
    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.statusBar().showMessage(f"Добро пожаловать, {self.session.login}! {self.library}")

    def keyPressEvent(self, event) -> None:
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        if ctrl and event.key() == Qt.Key.Key_F:
            self.__search.setFocus()
        elif ctrl and event.key() == Qt.Key.Key_N:
            self.add_book()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """При закрытии сохраняем книги и дописываем сеанс в отчёт."""
        self.session.finish()
        self.save()
        self.report.append(self.session)
        super().closeEvent(event)
