import csv
from pathlib import Path
from typing import Iterator, List, Tuple

from models import BaseModel, Book, Library, Session


class BookStorage(BaseModel):
    DELIMITER = ";"
    SEED = (
        ("Мастер и Маргарита", "Михаил Булгаков", 1967, "Роман", 480, True),
        ("Преступление и наказание", "Фёдор Достоевский", 1866, "Роман", 672, True),
        ("1984", "Джордж Оруэлл", 1949, "Антиутопия", 328, True),
        ("Пикник на обочине", "Аркадий и Борис Стругацкие", 1972, "Фантастика", 224, False),
        ("Евгений Онегин", "Александр Пушкин", 1833, "Поэзия", 320, True),
        ("Сто лет одиночества", "Габриэль Гарсиа Маркес", 1967, "Роман", 416, False),
        ("Дюна", "Фрэнк Герберт", 1965, "Фантастика", 704, False),
        ("Мы", "Евгений Замятин", 1924, "Антиутопия", 256, True),
        ("Чистый код", "Роберт Мартин", 2008, "IT", 464, False),
        ("Грокаем алгоритмы", "Адитья Бхаргава", 2016, "IT", 288, True),
        ("Собачье сердце", "Михаил Булгаков", 1925, "Повесть", 160, True),
        ("Этюд в багровых тонах", "Артур Конан Дойл", 1887, "Детектив", 192, False),
    )

    def __init__(self, path: Path):
        self.path = path

    @property
    def path(self) -> Path:
        return self.__path

    @path.setter
    def path(self, value: Path) -> None:
        self.__path = Path(value)

    @staticmethod
    def seed_books() -> List[Book]:
        return [Book(*row) for row in BookStorage.SEED]

    def load(self, library_name: str) -> Library:
        if not self:
            return Library(library_name, BookStorage.seed_books())
        with open(self.path, encoding="utf-8", newline="") as file:
            rows = [row for row in csv.reader(file, delimiter=BookStorage.DELIMITER) if row]
        return Library(library_name, [Book.from_row(row) for row in rows])

    def save(self, library: Library) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file, delimiter=BookStorage.DELIMITER)
            for book in library:
                writer.writerow(book.to_row())

    def compare_key(self) -> tuple:
        return (str(self.path),)

    def __str__(self) -> str:
        return f"Хранилище книг: {self.path}"

    def __repr__(self) -> str:
        return f"BookStorage(path={str(self.path)!r})"

    def __bool__(self) -> bool:
        return self.path.is_file()

    def __fspath__(self) -> str:
        return str(self.path)


class SessionReport(BaseModel):
    HEADERS = ("login", "time_in", "time_out")

    def __init__(self, path: Path):
        self.path = path
        self.rows = SessionReport.parse(self.path.read_text(encoding="utf-8")) if self.path.is_file() else []

    @property
    def path(self) -> Path:
        return self.__path

    @path.setter
    def path(self, value: Path) -> None:
        self.__path = Path(value)

    @property
    def rows(self) -> List[Tuple[str, str, str]]:
        return list(self.__rows)

    @rows.setter
    def rows(self, value: List[Tuple[str, str, str]]) -> None:
        self.__rows = [tuple(row) for row in value]

    @staticmethod
    def parse(text: str) -> List[Tuple[str, str, str]]:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("|") or line.startswith("|-"):
                continue
            cells = tuple(cell.strip() for cell in line.strip("|").split("|"))
            if len(cells) == 3 and cells != SessionReport.HEADERS:
                rows.append(cells)
        return rows

    @staticmethod
    def format_table(rows: List[Tuple[str, str, str]]) -> str:
        widths = [max([len(header)] + [len(row[i]) for row in rows]) + 2
                  for i, header in enumerate(SessionReport.HEADERS)]
        inner = sum(widths) + len(widths) - 1
        border = "+" + "-" * inner + "+"
        header = "|" + "|".join(h.center(w) for h, w in zip(SessionReport.HEADERS, widths)) + "|"
        separator = "|" + "|".join("-" * w for w in widths) + "|"
        lines = [border, header, separator]
        for login, time_in, time_out in rows:
            lines.append("|" + login.ljust(widths[0]) + "|"
                         + time_in.center(widths[1]) + "|"
                         + time_out.center(widths[2]) + "|")
        lines.append(border)
        return "\n".join(lines) + "\n"

    def append(self, session: Session) -> None:
        self.__rows.append(tuple(session))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(SessionReport.format_table(self.__rows), encoding="utf-8")

    def compare_key(self) -> tuple:
        return str(self.path), len(self)

    def __str__(self) -> str:
        return SessionReport.format_table(self.__rows)

    def __repr__(self) -> str:
        return f"SessionReport(path={str(self.path)!r}, rows={len(self)})"

    def __len__(self) -> int:
        return len(self.__rows)

    def __iter__(self) -> Iterator[Tuple[str, str, str]]:
        return iter(list(self.__rows))

    def __contains__(self, login: str) -> bool:
        return any(row[0] == login for row in self.__rows)
