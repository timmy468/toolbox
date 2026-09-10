import random
import re
import secrets
import string
import uuid

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Text(QWidget):
    def __init__(self):
        super().__init__()

        self.text = QPlainTextEdit()
        self.count = QLabel()
        self.pattern = QLineEdit()
        self.regex_text = QPlainTextEdit()
        self.matches = QPlainTextEdit()
        self.ignore = QCheckBox("Без учёта регистра")
        self.uuid = QLineEdit()
        self.password = QLineEdit()
        self.length = QSpinBox()
        self.lower = QCheckBox("a-z")
        self.upper = QCheckBox("A-Z")
        self.digits = QCheckBox("0-9")
        self.symbols = QCheckBox("Символы")

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Текст")
        title.setObjectName("heading")

        description = QLabel("Работа с текстом, Regex, UUID и паролями.")
        description.setObjectName("description")

        tabs = QTabWidget()
        tabs.addTab(self.text_tab(), "Текст")
        tabs.addTab(self.regex_tab(), "Regex")
        tabs.addTab(self.gen_tab(), "Генераторы")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(tabs, 1)

    def text_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        row = QHBoxLayout()
        upper = QPushButton("ВЕРХНИЙ")
        lower = QPushButton("нижний")
        title = QPushButton("Каждое Слово")
        unique = QPushButton("Убрать повторы строк")
        clear = QPushButton("Очистить")

        upper.clicked.connect(lambda: self.change("upper"))
        lower.clicked.connect(lambda: self.change("lower"))
        title.clicked.connect(lambda: self.change("title"))
        unique.clicked.connect(lambda: self.change("unique"))
        clear.clicked.connect(self.text.clear)

        row.addWidget(upper)
        row.addWidget(lower)
        row.addWidget(title)
        row.addWidget(unique)
        row.addStretch()
        row.addWidget(clear)

        self.text.setPlaceholderText("Введите текст")
        self.text.textChanged.connect(self.update_count)
        self.count.setObjectName("muted")
        self.update_count()

        layout.addLayout(row)
        layout.addWidget(self.text, 1)
        layout.addWidget(self.count)
        return page

    def regex_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        row = QHBoxLayout()
        self.pattern.setPlaceholderText(r"Например: \b\w+@\w+\.\w+\b")
        run = QPushButton("Найти")
        run.setObjectName("mainButton")
        run.clicked.connect(self.regex)
        row.addWidget(self.pattern, 1)
        row.addWidget(self.ignore)
        row.addWidget(run)

        self.regex_text.setPlaceholderText("Текст для поиска")
        self.matches.setPlaceholderText("Совпадения")
        self.matches.setReadOnly(True)

        layout.addLayout(row)
        layout.addWidget(self.regex_text, 1)
        layout.addWidget(self.matches, 1)
        return page

    def gen_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        uuid_row = QHBoxLayout()
        self.uuid.setReadOnly(True)
        self.uuid.setPlaceholderText("UUID")
        uuid_button = QPushButton("Создать UUID")
        uuid_copy = QPushButton("Копировать")
        uuid_button.clicked.connect(self.make_uuid)
        uuid_copy.clicked.connect(lambda: self.copy(self.uuid))
        uuid_row.addWidget(self.uuid, 1)
        uuid_row.addWidget(uuid_button)
        uuid_row.addWidget(uuid_copy)

        pass_row = QHBoxLayout()
        self.password.setReadOnly(True)
        self.password.setPlaceholderText("Пароль")
        pass_button = QPushButton("Создать пароль")
        pass_button.setObjectName("mainButton")
        pass_copy = QPushButton("Копировать")
        pass_button.clicked.connect(self.make_password)
        pass_copy.clicked.connect(lambda: self.copy(self.password))
        pass_row.addWidget(self.password, 1)
        pass_row.addWidget(pass_button)
        pass_row.addWidget(pass_copy)

        options = QHBoxLayout()
        self.length.setRange(4, 128)
        self.length.setValue(20)
        self.lower.setChecked(True)
        self.upper.setChecked(True)
        self.digits.setChecked(True)
        self.symbols.setChecked(True)

        options.addWidget(QLabel("Длина"))
        options.addWidget(self.length)
        options.addSpacing(12)
        options.addWidget(self.lower)
        options.addWidget(self.upper)
        options.addWidget(self.digits)
        options.addWidget(self.symbols)
        options.addStretch()

        layout.addWidget(QLabel("UUID"))
        layout.addLayout(uuid_row)
        layout.addSpacing(12)
        layout.addWidget(QLabel("Пароль"))
        layout.addLayout(options)
        layout.addLayout(pass_row)
        layout.addStretch()
        return page

    def change(self, type):
        text = self.text.toPlainText()

        if type == "upper":
            value = text.upper()
        elif type == "lower":
            value = text.lower()
        elif type == "title":
            value = text.title()
        else:
            lines = text.splitlines()
            value = "\n".join(dict.fromkeys(lines))

        self.text.setPlainText(value)

    def update_count(self):
        text = self.text.toPlainText()
        chars = len(text)
        words = len(re.findall(r"\S+", text))
        lines = 0 if not text else text.count("\n") + 1
        self.count.setText(f"Символов: {chars} · слов: {words} · строк: {lines}")

    def regex(self):
        pattern = self.pattern.text()

        if not pattern:
            self.matches.clear()
            return

        flags = re.IGNORECASE if self.ignore.isChecked() else 0

        try:
            value = re.compile(pattern, flags)
            items = []

            for i, match in enumerate(value.finditer(self.regex_text.toPlainText()), 1):
                groups = " | ".join(group or "" for group in match.groups())
                text = match.group(0)
                line = f"{i}. {match.start()}-{match.end()}: {text}"
                if groups:
                    line += f" | {groups}"
                items.append(line)

            self.matches.setPlainText("\n".join(items) if items else "Совпадений нет")
        except re.error as error:
            QMessageBox.warning(self, "Regex", str(error))

    def make_uuid(self):
        self.uuid.setText(str(uuid.uuid4()))

    def make_password(self):
        groups = []

        if self.lower.isChecked():
            groups.append(string.ascii_lowercase)
        if self.upper.isChecked():
            groups.append(string.ascii_uppercase)
        if self.digits.isChecked():
            groups.append(string.digits)
        if self.symbols.isChecked():
            groups.append("!@#$%^&*()-_=+[]{}:,.?")

        if not groups:
            QMessageBox.warning(self, "Пароль", "Выберите хотя бы один набор символов.")
            return

        length = self.length.value()
        if length < len(groups):
            QMessageBox.warning(self, "Пароль", "Увеличьте длину пароля.")
            return

        chars = [secrets.choice(group) for group in groups]
        pool = "".join(groups)
        chars.extend(secrets.choice(pool) for _ in range(length - len(chars)))
        random.SystemRandom().shuffle(chars)
        self.password.setText("".join(chars))

    def copy(self, edit):
        if edit.text():
            QApplication.clipboard().setText(edit.text())
