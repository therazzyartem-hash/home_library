# Домашняя библиотека (PyQt6)

Учёт книг: вход по логину, таблица книг, поиск, фильтр по жанру, сортировка,
добавление / изменение / удаление, отметка «прочитана». Данные хранятся в `data/books.csv`,
при закрытии окна в `report.txt` дописывается сеанс работы.

## Запуск

```
pip install PyQt6
python main.py
```

Горячие клавиши: `Ctrl+F` — поиск, `Ctrl+N` — новая книга, `Enter`/двойной клик — изменить,
`Пробел` — прочитана/нет, `Delete` — удалить, `Esc` в поиске — очистить, ПКМ по строке — меню.

## Структура

| Файл | Содержимое |
|------|------------|
| `models.py` | `BaseModel` (ABC), `Book`, `Pair`, `PairMap`, `Library`, `Session` |
| `storage.py` | `BookStorage` (CSV), `SessionReport` (отчёт-таблица) |
| `widgets.py` | `Theme` и 13 переопределённых компонентов окна |
| `main_window.py` | `MainWindow` |
| `main.py` | `Application.run()` — точка входа |

## Где выполнены требования

| Требование | Реализация |
|---|---|
| Сущности описаны классами | все данные и логика — в классах; даже запуск — `Application.run()` |
| Наследование от абстрактного класса | `BaseModel(ABC)` с абстрактными `compare_key`, `__str__`, `__repr__`; от него наследуются `Book`, `Pair`, `PairMap`, `Library`, `Session`, `BookStorage`, `SessionReport` |
| Функциональность в методах объекта / `@staticmethod` | напр. `Book.require_text`, `Book.from_row`, `Library.sorted_by`, `Session.format_time`, `SessionReport.format_table`, `Theme.stylesheet` |
| `__eq__`, `__repr__`, `__str__` + ещё ≥3 спецметода | база: `__eq__ __lt__ __le__ __gt__ __ge__ __hash__`; `Book`: `__len__ __contains__ __iter__`; `PairMap`: `__getitem__ __setitem__ __delitem__ __contains__ __len__ __iter__`; `Library`: `__len__ __iter__ __contains__ __getitem__`; `Session`: `__bool__ __int__ __iter__`; `BookStorage`: `__bool__ __fspath__` |
| Классы сравнимы | `<, <=, >, >=, ==` по `compare_key()`, поэтому работает `sorted(library)` |
| Геттеры и сеттеры | все атрибуты — приватные `__поля` с `@property` и `@x.setter` (с валидацией в `Book`) |
| Без `dict` | своё отображение `PairMap` на списке `Pair`: цвета жанров (`Theme.GENRE_COLORS`), варианты сортировки (`SortComboBox.OPTIONS`) |
| ≥5 UI-компонентов | QLabel, QLineEdit, QComboBox, QCheckBox, QSpinBox, QPushButton, QTableWidget, QStatusBar, QMenu, QMessageBox, QDialog |
| ≥10 переопределённых компонентов окна | `HeaderLabel(sizeHint)`, `StatsLabel(setText)`, `SearchLineEdit(keyPressEvent, focusInEvent)`, `ActionButton(enterEvent, leaveEvent)`, `NoWheelComboBox(wheelEvent)`, `GenreComboBox`, `SortComboBox`, `YearSpinBox(wheelEvent)`, `ReadCheckBox(nextCheckState, setChecked)`, `BookTable(keyPressEvent, mouseDoubleClickEvent, contextMenuEvent)`, `AppStatusBar(showMessage)`, `LoginDialog(accept)`, `BookFormDialog(accept, keyPressEvent)`, `MainWindow(showEvent, keyPressEvent, closeEvent)` |
| ≥10 пользовательских объектов в коллекциях | 12 книг в `list` внутри `Library` (`BookStorage.SEED`) |
| Выравнивание | только layout-менеджеры (`QVBoxLayout`, `QHBoxLayout`, `QFormLayout`) + `setAlignment` |
| Отчёт при закрытии | `MainWindow.closeEvent` → `SessionReport.append` → `report.txt`, время `%d.%m.%Y %H:%M:%S` |

Пример `report.txt`:

```
+---------------------------------------------------+
| login |       time_in       |       time_out      |
|-------|---------------------|---------------------|
|artem  | 10.10.2026 08:18:31 | 10.10.2026 08:25:02 |
+---------------------------------------------------+
```
