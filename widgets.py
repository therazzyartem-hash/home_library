import re
from datetime import datetime
from typing import List, Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QSpinBox, QStatusBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from models import Book, PairMap


class Theme:
    GENRE_COLORS = PairMap([
        ("Роман", "#fff4e0"),
        ("Фантастика", "#e3f2fd"),
        ("Антиутопия", "#fde7e9"),
        ("Поэзия", "#f3e5f5"),
        ("IT", "#e8f5e9"),
        ("Повесть", "#fffde7"),
        ("Детектив", "#eceff1"),
    ])
    DEFAULT_COLOR = "#ffffff"

    @staticmethod
    def genre_color(genre: str) -> QColor:
        return QColor(Theme.GENRE_COLORS.get(genre, Theme.DEFAULT_COLOR))

    @staticmethod
    def stylesheet() -> str:
        return """
            QWidget { font-family: 'Segoe UI'; font-size: 10pt; color: #1f2933; }
            QMainWindow, QDialog { background: #f5f7fa; }
            QLabel#header { font-size: 16pt; font-weight: 600; color: #243b53; }
            QLabel#stats { color: #486581; }
            QLineEdit, QComboBox, QSpinBox {
                background: #ffffff; border: 1px solid #bcccdc; border-radius: 6px; padding: 5px 8px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #2f80ed; }
            QPushButton {
                background: #2f80ed; color: #ffffff; border: none; border-radius: 6px; padding: 7px 16px;
            }
            QPushButton:hover { background: #1c6ad6; }
            QPushButton:pressed { background: #1556b0; }
            QPushButton#danger { background: #e0464e; }
            QPushButton#danger:hover { background: #c5323a; }
            QTableWidget {
                background: #ffffff; border: 1px solid #d9e2ec; border-radius: 6px;
                gridline-color: #e4e7eb; selection-background-color: #2f80ed; selection-color: #ffffff;
            }
            QHeaderView::section {
                background: #e4e7eb; padding: 6px; border: none; font-weight: 600;
            }
            QStatusBar { color: #486581; }
        """


class HeaderLabel(QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("header")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), 48))


class StatsLabel(QLabel):
    PREFIX = "Статистика: "

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("stats")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def setText(self, text: str) -> None:
        super().setText(StatsLabel.PREFIX + text)


class SearchLineEdit(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setPlaceholderText("Поиск по названию, автору или жанру")
        self.setClearButtonEnabled(True)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)
        self.selectAll()


class ActionButton(QPushButton):
    def __init__(self, text: str, status_tip: str, danger: bool = False,
                 parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setStatusTip(status_tip)
        self.setToolTip(status_tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        if danger:
            self.setObjectName("danger")

    def enterEvent(self, event) -> None:
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        font = self.font()
        font.setBold(False)
        self.setFont(font)
        super().leaveEvent(event)


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class GenreComboBox(NoWheelComboBox):
    ALL = "Все жанры"

    def set_genres(self, genres: List[str]) -> None:
        current = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItem(GenreComboBox.ALL)
        self.addItems(genres)
        index = self.findText(current)
        self.setCurrentIndex(max(index, 0))
        self.blockSignals(False)

    @property
    def current_genre(self) -> Optional[str]:
        text = self.currentText()
        return None if text == GenreComboBox.ALL else text

    @current_genre.setter
    def current_genre(self, value: Optional[str]) -> None:
        self.setCurrentIndex(max(self.findText(value or GenreComboBox.ALL), 0))


class SortComboBox(NoWheelComboBox):
    OPTIONS = PairMap([
        ("По названию", "title"),
        ("По автору", "author"),
        ("По году", "year"),
        ("По жанру", "genre"),
        ("По страницам", "pages"),
        ("По ID", "book_id"),
    ])

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.addItems(SortComboBox.OPTIONS.names())

    @property
    def attribute(self) -> str:
        return SortComboBox.OPTIONS[self.currentText()]

    @attribute.setter
    def attribute(self, value: str) -> None:
        for label, attribute in SortComboBox.OPTIONS.pairs:
            if attribute == value:
                self.setCurrentText(label)


class YearSpinBox(QSpinBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setRange(Book.MIN_YEAR, datetime.now().year)
        self.setValue(datetime.now().year)
        self.setSuffix(" г.")

    def wheelEvent(self, event) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class ReadCheckBox(QCheckBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.refresh_text()

    def refresh_text(self) -> None:
        self.setText("Прочитана" if self.isChecked() else "Не прочитана")

    def nextCheckState(self) -> None:
        super().nextCheckState()
        self.refresh_text()

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self.refresh_text()


class BookTable(QTableWidget):
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    toggle_requested = pyqtSignal()

    HEADERS = ("ID", "Название", "Автор", "Год", "Жанр", "Страниц", "Прочитана")
    NUMERIC_COLUMNS = (0, 3, 5, 6)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(0, len(BookTable.HEADERS), parent)
        self.setHorizontalHeaderLabels(BookTable.HEADERS)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def show_books(self, books: List[Book]) -> None:
        selected = self.selected_book_id
        self.setRowCount(len(books))
        for row, book in enumerate(books):
            color = Theme.genre_color(book.genre)
            for column, value in enumerate(book):
                item = QTableWidgetItem(str(value))
                item.setBackground(color)
                item.setForeground(QColor("#1f2933"))
                if column in BookTable.NUMERIC_COLUMNS:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row, column, item)
            if book.book_id == selected:
                self.selectRow(row)

    @property
    def selected_book_id(self) -> Optional[int]:
        row = self.currentRow()
        if row < 0 or not self.selectionModel().hasSelection() or self.item(row, 0) is None:
            return None
        return int(self.item(row, 0).text())

    @selected_book_id.setter
    def selected_book_id(self, book_id: Optional[int]) -> None:
        for row in range(self.rowCount()):
            if int(self.item(row, 0).text()) == book_id:
                self.selectRow(row)
                return
        self.clearSelection()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.delete_requested.emit()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.edit_requested.emit()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_requested.emit()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        super().mouseDoubleClickEvent(event)
        if self.selected_book_id is not None:
            self.edit_requested.emit()

    def contextMenuEvent(self, event) -> None:
        if self.selected_book_id is None:
            return
        menu = QMenu(self)
        menu.addAction("Изменить", self.edit_requested.emit)
        menu.addAction("Прочитано / не прочитано", self.toggle_requested.emit)
        menu.addSeparator()
        menu.addAction("Удалить", self.delete_requested.emit)
        menu.exec(event.globalPos())


class AppStatusBar(QStatusBar):
    DEFAULT_TIMEOUT = 5000

    def showMessage(self, text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        super().showMessage(f"[{datetime.now():%H:%M:%S}] {text}", timeout)


class LoginDialog(QDialog):
    LOGIN_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё0-9_.-]{3,20}$")

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.login = ""
        self.setWindowTitle("Вход")
        self.setFixedWidth(360)

        self.__login_edit = QLineEdit()
        self.__login_edit.setPlaceholderText("логин")
        enter_button = ActionButton("Войти", "Начать работу с библиотекой")
        enter_button.setDefault(True)
        enter_button.clicked.connect(self.accept)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.addRow("Логин:", self.__login_edit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        layout.addWidget(HeaderLabel("Домашняя библиотека"))
        layout.addLayout(form)
        layout.addWidget(enter_button, alignment=Qt.AlignmentFlag.AlignRight)

    @property
    def login(self) -> str:
        return self.__login

    @login.setter
    def login(self, value: str) -> None:
        self.__login = value.strip()

    def accept(self) -> None:
        login = self.__login_edit.text().strip()
        if not LoginDialog.LOGIN_PATTERN.match(login):
            QMessageBox.warning(self, "Неверный логин",
                                "Логин должен быть от 3 до 20 символов (буквы, цифры, _ . -)")
            return
        self.login = login
        super().accept()


class BookFormDialog(QDialog):
    def __init__(self, genres: List[str], book: Optional[Book] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.source_book = book
        self.result_book = None
        self.setWindowTitle("Изменить книгу" if book else "Новая книга")
        self.setMinimumWidth(420)

        self.__title_edit = QLineEdit()
        self.__author_edit = QLineEdit()
        self.__year_spin = YearSpinBox()
        self.__genre_combo = NoWheelComboBox()
        self.__genre_combo.setEditable(True)
        self.__genre_combo.addItems(genres)
        self.__pages_spin = QSpinBox()
        self.__pages_spin.setRange(1, 10000)
        self.__pages_spin.setValue(300)
        self.__read_check = ReadCheckBox()

        if book:
            self.__title_edit.setText(book.title)
            self.__author_edit.setText(book.author)
            self.__year_spin.setValue(book.year)
            self.__genre_combo.setCurrentText(book.genre)
            self.__pages_spin.setValue(book.pages)
            self.__read_check.setChecked(book.is_read)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Название:", self.__title_edit)
        form.addRow("Автор:", self.__author_edit)
        form.addRow("Год издания:", self.__year_spin)
        form.addRow("Жанр:", self.__genre_combo)
        form.addRow("Страниц:", self.__pages_spin)
        form.addRow("", self.__read_check)

        save_button = ActionButton("Сохранить", "Сохранить книгу")
        save_button.setDefault(True)
        save_button.clicked.connect(self.accept)
        cancel_button = ActionButton("Отмена", "Закрыть без сохранения", danger=True)
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addLayout(buttons)

    @property
    def source_book(self) -> Optional[Book]:
        return self.__source_book

    @source_book.setter
    def source_book(self, value: Optional[Book]) -> None:
        self.__source_book = value

    @property
    def result_book(self) -> Optional[Book]:
        return self.__result_book

    @result_book.setter
    def result_book(self, value: Optional[Book]) -> None:
        self.__result_book = value

    def accept(self) -> None:
        try:
            book_id = self.source_book.book_id if self.source_book else None
            self.result_book = Book(self.__title_edit.text(), self.__author_edit.text(),
                                    self.__year_spin.value(), self.__genre_combo.currentText(),
                                    self.__pages_spin.value(), self.__read_check.isChecked(), book_id)
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка ввода", str(error))
            return
        super().accept()

    def keyPressEvent(self, event) -> None:
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.accept()
        else:
            super().keyPressEvent(event)
