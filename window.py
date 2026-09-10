from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from style import dark, light
from tools.archive import Archive
from tools.code import Code
from tools.files import Files
from tools.hash import Hash
from tools.home import Home
from tools.images import Images
from tools.json import Json
from tools.text import Text


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Toolbox")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.settings = QSettings("Toolbox", "Toolbox")
        self.stack = QStackedWidget()
        self.buttons = []
        self.items = []
        self.theme = QComboBox()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.menu())
        layout.addWidget(self.stack, 1)

        home = Home()
        home.opened.connect(self.open)

        self.stack.addWidget(home)
        self.stack.addWidget(Files())
        self.stack.addWidget(Images())
        self.stack.addWidget(Json())
        self.stack.addWidget(Hash())
        self.stack.addWidget(Code())
        self.stack.addWidget(Text())
        self.stack.addWidget(Archive())

        self.set_theme(self.settings.value("theme", "Тёмная"))
        self.open(int(self.settings.value("tool", 0)))

    def menu(self):
        panel = QFrame()
        panel.setObjectName("menu")
        panel.setFixedWidth(240)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(8)

        title = QLabel("Toolbox")
        title.setObjectName("title")

        subtitle = QLabel("Небольшие инструменты")
        subtitle.setObjectName("subtitle")

        search = QLineEdit()
        search.setPlaceholderText("Найти инструмент")
        search.textChanged.connect(self.filter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(14)
        layout.addWidget(search)
        layout.addSpacing(8)

        icons = [
            QStyle.StandardPixmap.SP_ComputerIcon,
            QStyle.StandardPixmap.SP_DirIcon,
            QStyle.StandardPixmap.SP_FileDialogDetailedView,
            QStyle.StandardPixmap.SP_FileIcon,
            QStyle.StandardPixmap.SP_DialogApplyButton,
            QStyle.StandardPixmap.SP_CommandLink,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            QStyle.StandardPixmap.SP_DriveHDIcon,
        ]

        names = [
            "Главная",
            "Файлы",
            "Изображения",
            "JSON",
            "Хэш",
            "Кодирование",
            "Текст",
            "Архивы",
        ]

        for index, name in enumerate(names):
            button = QPushButton(name)
            button.setObjectName("menuButton")
            button.setIcon(self.style().standardIcon(icons[index]))
            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.open(i))
            self.buttons.append(button)
            self.items.append(name.lower())
            layout.addWidget(button)

        layout.addStretch()

        self.theme.addItems(["Тёмная", "Светлая"])
        self.theme.currentTextChanged.connect(self.set_theme)
        layout.addWidget(self.theme)

        return panel

    def filter(self, text):
        text = text.strip().lower()

        for name, button in zip(self.items, self.buttons):
            button.setVisible(not text or text in name)

    def open(self, index):
        if index < 0 or index >= self.stack.count():
            index = 0

        self.stack.setCurrentIndex(index)
        self.settings.setValue("tool", index)

        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)

    def set_theme(self, name):
        if self.theme.currentText() != name:
            self.theme.blockSignals(True)
            self.theme.setCurrentText(name)
            self.theme.blockSignals(False)

        self.setStyleSheet(light if name == "Светлая" else dark)
        self.settings.setValue("theme", name)
