import json

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Json(QWidget):
    def __init__(self):
        super().__init__()

        self.text = QPlainTextEdit()
        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("JSON")
        title.setObjectName("heading")

        description = QLabel("Форматирование и проверка JSON.")
        description.setObjectName("description")

        self.text.setPlaceholderText('{"name":"Alex","age":16}')
        self.text.setLineWrapMode(QPlainTextEdit.NoWrap)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        open_button = QPushButton("Открыть")
        format_button = QPushButton("Форматировать")
        minify_button = QPushButton("Сжать")
        save_button = QPushButton("Сохранить")

        format_button.setObjectName("mainButton")

        open_button.clicked.connect(self.open)
        format_button.clicked.connect(self.format)
        minify_button.clicked.connect(self.minify)
        save_button.clicked.connect(self.save)

        buttons.addWidget(open_button)
        buttons.addWidget(format_button)
        buttons.addWidget(minify_button)
        buttons.addStretch()
        buttons.addWidget(save_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(6)
        layout.addLayout(buttons)
        layout.addWidget(self.text, 1)

    def read(self):
        try:
            return json.loads(self.text.toPlainText())
        except json.JSONDecodeError as error:
            QMessageBox.warning(
                self,
                "Некорректный JSON",
                f"Строка {error.lineno}, столбец {error.colno}\n{error.msg}",
            )
            return None

    def format(self):
        data = self.read()

        if data is None:
            return

        self.text.setPlainText(json.dumps(data, ensure_ascii=False, indent=4))

    def minify(self):
        data = self.read()

        if data is None:
            return

        self.text.setPlainText(
            json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        )

    def open(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть JSON",
            "",
            "JSON (*.json);;Все файлы (*)",
        )

        if not file:
            return

        try:
            with open(file, "r", encoding="utf-8") as f:
                self.text.setPlainText(f.read())
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def save(self):
        if self.read() is None:
            return

        file, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить JSON",
            "data.json",
            "JSON (*.json)",
        )

        if not file:
            return

        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(self.text.toPlainText())
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))
