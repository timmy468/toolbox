from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from style import style
from tools.files import Files
from tools.hash import Hash
from tools.images import Images
from tools.json import Json


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Toolbox")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.stack = QStackedWidget()
        self.buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.menu())
        layout.addWidget(self.stack, 1)

        self.stack.addWidget(Files())
        self.stack.addWidget(Images())
        self.stack.addWidget(Json())
        self.stack.addWidget(Hash())

        self.setStyleSheet(style)
        self.open(0)

    def menu(self):
        panel = QFrame()
        panel.setObjectName("menu")
        panel.setFixedWidth(230)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(8)

        title = QLabel("Toolbox")
        title.setObjectName("title")

        subtitle = QLabel("Небольшие инструменты")
        subtitle.setObjectName("subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(22)

        items = [
            ("Файлы", 0),
            ("Изображения", 1),
            ("JSON", 2),
            ("Хэш", 3),
        ]

        for text, index in items:
            button = QPushButton(text)
            button.setObjectName("menuButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.open(i))
            self.buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()

        return panel

    def open(self, index):
        self.stack.setCurrentIndex(index)

        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)
