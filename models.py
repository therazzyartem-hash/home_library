"""Модели предметной области: абстрактная база, книга, пара/отображение, библиотека, сессия."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Iterator, List, Optional, Tuple

DATE_FORMAT = "%d.%m.%Y %H:%M:%S"


class BaseModel(ABC):
    """Абстрактный предок всех пользовательских классов.

    Задаёт сравнение (==, <, <=, >, >=) и хеширование через абстрактный
    ключ compare_key(). Каждый наследник обязан определить compare_key(),
    __str__() и __repr__().
    """

    @abstractmethod
    def compare_key(self) -> tuple:
        """Кортеж, по которому объекты сравниваются и хешируются."""

    @abstractmethod
    def __str__(self) -> str:
        """Человекочитаемое представление."""

    @abstractmethod
    def __repr__(self) -> str:
        """Отладочное представление."""

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.compare_key() == other.compare_key()

    def __lt__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.compare_key() < other.compare_key()

    def __le__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.compare_key() <= other.compare_key()

    def __gt__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.compare_key() > other.compare_key()

    def __ge__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.compare_key() >= other.compare_key()

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.compare_key()))


class Book(BaseModel):
    """Книга домашней библиотеки."""

    MIN_YEAR = 1000
    _next_id = 1

    def __init__(self, title: str, author: str, year: int, genre: str,
                 pages: int, is_read: bool = False, book_id: Optional[int] = None):
        if book_id is None:
            book_id = Book._next_id
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.pages = pages
        self.is_read = is_read

    # --- геттеры / сеттеры -------------------------------------------------
    @property
    def book_id(self) -> int:
        return self.__book_id

    @book_id.setter
    def book_id(self, value: int) -> None:
        value = int(value)
        if value < 1:
            raise ValueError("ID книги должен быть положительным")
        self.__book_id = value
        Book._next_id = max(Book._next_id, value + 1)

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = Book.require_text(value, "Название")

    @property
    def author(self) -> str:
        return self.__author

    @author.setter
    def author(self, value: str) -> None:
        self.__author = Book.require_text(value, "Автор")

    @property
    def year(self) -> int:
        return self.__year

    @year.setter
    def year(self, value: int) -> None:
        value = int(value)
        current = datetime.now().year
        if not Book.MIN_YEAR <= value <= current:
            raise ValueError(f"Год должен быть в диапазоне {Book.MIN_YEAR}–{current}")
        self.__year = value

    @property
    def genre(self) -> str:
        return self.__genre

    @genre.setter
    def genre(self, value: str) -> None:
        self.__genre = Book.require_text(value, "Жанр")

    @property
    def pages(self) -> int:
        return self.__pages

    @pages.setter
    def pages(self, value: int) -> None:
        value = int(value)
        if value <= 0:
            raise ValueError("Количество страниц должно быть больше нуля")
        self.__pages = value

    @property
    def is_read(self) -> bool:
        return self.__is_read

    @is_read.setter
    def is_read(self, value: bool) -> None:
        self.__is_read = bool(value)

    # --- методы ------------------------------------------------------------
    @staticmethod
    def require_text(value: str, field: str) -> str:
        value = str(value).strip()
        if not value:
            raise ValueError(f"Поле «{field}» не может быть пустым")
        return value

    @staticmethod
    def from_row(row: List[str]) -> "Book":
        book_id, title, author, year, genre, pages, is_read = row
        return Book(title, author, int(year), genre, int(pages), is_read == "1", int(book_id))

    def to_row(self) -> Tuple[str, ...]:
        return (str(self.book_id), self.title, self.author, str(self.year),
                self.genre, str(self.pages), "1" if self.is_read else "0")

    def toggle_read(self) -> None:
        self.is_read = not self.is_read

    def compare_key(self) -> tuple:
        # Одинаковыми считаются книги с совпадающими названием, автором и годом
        return self.title.lower(), self.author.lower(), self.year

    # --- специальные методы ------------------------------------------------
    def __str__(self) -> str:
        return f"«{self.title}» — {self.author} ({self.year})"

    def __repr__(self) -> str:
        return (f"Book(book_id={self.book_id}, title={self.title!r}, author={self.author!r}, "
                f"year={self.year}, genre={self.genre!r}, pages={self.pages}, is_read={self.is_read})")

    def __len__(self) -> int:
        """Длина книги — количество страниц."""
        return self.pages

    def __contains__(self, text: str) -> bool:
        """Поиск подстроки в названии, авторе и жанре: `"булгаков" in book`."""
        text = str(text).lower()
        return text in self.title.lower() or text in self.author.lower() or text in self.genre.lower()

    def __iter__(self) -> Iterator:
        """Значения ячеек строки таблицы."""
        yield self.book_id
        yield self.title
        yield self.author
        yield self.year
        yield self.genre
        yield self.pages
        yield "✔" if self.is_read else "—"


class Pair(BaseModel):
    """Пара «имя → значение», элемент PairMap."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value) -> None:
        self.__name = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value) -> None:
        self.__value = value

    def compare_key(self) -> tuple:
        return str(self.name), str(self.value)

    def __str__(self) -> str:
        return f"{self.name} → {self.value}"

    def __repr__(self) -> str:
        return f"Pair({self.name!r}, {self.value!r})"

    def __iter__(self) -> Iterator:
        """Позволяет распаковывать пару: name, value = pair."""
        yield self.name
        yield self.value

    def __len__(self) -> int:
        return 2

    def __bool__(self) -> bool:
        return self.value is not None


class PairMap(BaseModel):
    """Собственное отображение на списке пар — замена встроенного dict."""

    def __init__(self, pairs: Optional[List[Tuple]] = None):
        self.pairs = [Pair(name, value) for name, value in (pairs or [])]

    @property
    def pairs(self) -> List[Pair]:
        return list(self.__pairs)

    @pairs.setter
    def pairs(self, value: List[Pair]) -> None:
        self.__pairs = list(value)

    def find(self, name) -> Optional[Pair]:
        for pair in self.__pairs:
            if pair.name == name:
                return pair
        return None

    def get(self, name, default=None):
        pair = self.find(name)
        return default if pair is None else pair.value

    def put(self, name, value) -> None:
        pair = self.find(name)
        if pair is None:
            self.__pairs.append(Pair(name, value))
        else:
            pair.value = value

    def remove(self, name) -> None:
        pair = self.find(name)
        if pair is None:
            raise KeyError(name)
        self.__pairs.remove(pair)

    def names(self) -> List:
        return [pair.name for pair in self.__pairs]

    def values(self) -> List:
        return [pair.value for pair in self.__pairs]

    def compare_key(self) -> tuple:
        return tuple(pair.compare_key() for pair in self.__pairs)

    def __str__(self) -> str:
        return "{" + ", ".join(str(pair) for pair in self.__pairs) + "}"

    def __repr__(self) -> str:
        return f"PairMap({[tuple(pair) for pair in self.__pairs]!r})"

    def __getitem__(self, name):
        pair = self.find(name)
        if pair is None:
            raise KeyError(name)
        return pair.value

    def __setitem__(self, name, value) -> None:
        self.put(name, value)

    def __delitem__(self, name) -> None:
        self.remove(name)

    def __contains__(self, name) -> bool:
        return self.find(name) is not None

    def __len__(self) -> int:
        return len(self.__pairs)

    def __iter__(self) -> Iterator:
        return iter(self.names())


class Library(BaseModel):
    """Коллекция книг с поиском, фильтрацией, сортировкой и статистикой."""

    def __init__(self, name: str, books: Optional[List[Book]] = None):
        self.name = name
        self.books = []
        for book in books or []:
            self.add(book)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = Book.require_text(value, "Название библиотеки")

    @property
    def books(self) -> List[Book]:
        return list(self.__books)

    @books.setter
    def books(self, value: List[Book]) -> None:
        self.__books = list(value)

    # --- изменение ---------------------------------------------------------
    def add(self, book: Book) -> None:
        if book in self.__books:
            raise ValueError(f"Книга {book} уже есть в библиотеке")
        self.__books.append(book)

    def update(self, book: Book) -> None:
        """Заменяет книгу с тем же ID на новую версию."""
        old = self.find_by_id(book.book_id)
        if old is None:
            raise ValueError("Книга не найдена")
        if any(other == book for other in self.__books if other is not old):
            raise ValueError(f"Книга {book} уже есть в библиотеке")
        self.__books[self.__books.index(old)] = book

    def remove(self, book_id: int) -> Book:
        book = self.find_by_id(book_id)
        if book is None:
            raise ValueError("Книга не найдена")
        self.__books.remove(book)
        return book

    # --- выборки -----------------------------------------------------------
    def find_by_id(self, book_id: int) -> Optional[Book]:
        for book in self.__books:
            if book.book_id == book_id:
                return book
        return None

    def search(self, text: str = "", genre: Optional[str] = None) -> List[Book]:
        return [book for book in self.__books
                if text in book and (genre is None or book.genre == genre)]

    def genres(self) -> List[str]:
        return sorted({book.genre for book in self.__books})

    def total_pages(self) -> int:
        return sum(len(book) for book in self.__books)

    def read_count(self) -> int:
        return sum(1 for book in self.__books if book.is_read)

    @staticmethod
    def sort_key(attribute: str) -> Callable[[Book], object]:
        def key(book: Book):
            value = getattr(book, attribute)
            return value.lower() if isinstance(value, str) else value
        return key

    @staticmethod
    def sorted_by(books: List[Book], attribute: str, reverse: bool = False) -> List[Book]:
        return sorted(books, key=Library.sort_key(attribute), reverse=reverse)

    def compare_key(self) -> tuple:
        return self.name, len(self)

    # --- специальные методы ------------------------------------------------
    def __str__(self) -> str:
        return f"Библиотека «{self.name}»: {len(self)} книг"

    def __repr__(self) -> str:
        return f"Library(name={self.name!r}, books={self.__books!r})"

    def __len__(self) -> int:
        return len(self.__books)

    def __iter__(self) -> Iterator[Book]:
        return iter(list(self.__books))

    def __contains__(self, book: Book) -> bool:
        return book in self.__books

    def __getitem__(self, index: int) -> Book:
        return self.__books[index]


class Session(BaseModel):
    """Сеанс работы пользователя: логин, время входа и выхода."""

    def __init__(self, login: str, time_in: Optional[datetime] = None,
                 time_out: Optional[datetime] = None):
        self.login = login
        self.time_in = time_in or datetime.now()
        self.time_out = time_out

    @property
    def login(self) -> str:
        return self.__login

    @login.setter
    def login(self, value: str) -> None:
        self.__login = Book.require_text(value, "Логин")

    @property
    def time_in(self) -> datetime:
        return self.__time_in

    @time_in.setter
    def time_in(self, value: datetime) -> None:
        self.__time_in = value

    @property
    def time_out(self) -> Optional[datetime]:
        return self.__time_out

    @time_out.setter
    def time_out(self, value: Optional[datetime]) -> None:
        self.__time_out = value

    def finish(self) -> None:
        self.time_out = datetime.now()

    @staticmethod
    def format_time(value: Optional[datetime]) -> str:
        return value.strftime(DATE_FORMAT) if value else ""

    def compare_key(self) -> tuple:
        return self.time_in, self.login

    def __str__(self) -> str:
        return f"{self.login}: {Session.format_time(self.time_in)} — {Session.format_time(self.time_out)}"

    def __repr__(self) -> str:
        return f"Session(login={self.login!r}, time_in={self.time_in!r}, time_out={self.time_out!r})"

    def __bool__(self) -> bool:
        """Истина, если сеанс завершён."""
        return self.time_out is not None

    def __int__(self) -> int:
        """Длительность сеанса в секундах."""
        end = self.time_out or datetime.now()
        return int((end - self.time_in).total_seconds())

    def __iter__(self) -> Iterator[str]:
        """Ячейки строки отчёта: login, time_in, time_out."""
        yield self.login
        yield Session.format_time(self.time_in)
        yield Session.format_time(self.time_out)
