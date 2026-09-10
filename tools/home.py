from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Home(QWidget):
    opened = Signal(int)

    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Toolbox")
        title.setObjectName("heading")

        description = QLabel("Набор небольших инструментов для файлов и данных.")
        description.setObjectName("description")

        grid = QGridLayout()
        grid.setSpacing(12)

        items = [
            ("Файлы", "Копирование, поиск, размер и дубликаты", 1),
            ("Изображения", "Конвертация, размер и пакетная обработка", 2),
            ("JSON", "Форматирование, проверка и сравнение", 3),
            ("Хэш", "Хэши файлов и проверка суммы", 4),
            ("Кодирование", "Base64, HEX, URL и Unicode", 5),
            ("Текст", "Текст, Regex, UUID и пароли", 6),
            ("Архивы", "Создание и распаковка ZIP", 7),
        ]

        for i, item in enumerate(items):
            name, text, index = item
            button = QPushButton(f"{name}\n{text}")
            button.setObjectName("cardButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(92)
            button.clicked.connect(lambda checked=False, x=index: self.opened.emit(x))
            grid.addWidget(button, i // 2, i % 2)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(12)
        layout.addLayout(grid)
        layout.addStretch()
