import base64
import json
from urllib.parse import quote, unquote

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Code(QWidget):
    def __init__(self):
        super().__init__()

        self.type = QComboBox()
        self.input = QPlainTextEdit()
        self.output = QPlainTextEdit()
        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Кодирование")
        title.setObjectName("heading")

        description = QLabel("Base64, HEX, URL и Unicode Escape.")
        description.setObjectName("description")

        row = QHBoxLayout()
        self.type.addItems(["Base64", "HEX", "URL", "Unicode"])

        encode = QPushButton("Кодировать")
        decode = QPushButton("Декодировать")
        swap = QPushButton("Поменять местами")
        clear = QPushButton("Очистить")
        copy = QPushButton("Копировать результат")

        encode.setObjectName("mainButton")
        encode.clicked.connect(lambda: self.run(False))
        decode.clicked.connect(lambda: self.run(True))
        swap.clicked.connect(self.swap)
        clear.clicked.connect(self.clear)
        copy.clicked.connect(self.copy)

        row.addWidget(self.type)
        row.addWidget(encode)
        row.addWidget(decode)
        row.addWidget(swap)
        row.addStretch()
        row.addWidget(clear)
        row.addWidget(copy)

        self.input.setPlaceholderText("Исходный текст")
        self.output.setPlaceholderText("Результат")
        self.output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(row)
        layout.addWidget(QLabel("Ввод"))
        layout.addWidget(self.input, 1)
        layout.addWidget(QLabel("Результат"))
        layout.addWidget(self.output, 1)

    def run(self, decode):
        text = self.input.toPlainText()
        type = self.type.currentText()

        try:
            if type == "Base64":
                if decode:
                    value = base64.b64decode(text.encode("ascii"), validate=True).decode("utf-8")
                else:
                    value = base64.b64encode(text.encode("utf-8")).decode("ascii")
            elif type == "HEX":
                if decode:
                    value = bytes.fromhex(text).decode("utf-8")
                else:
                    value = text.encode("utf-8").hex()
            elif type == "URL":
                value = unquote(text) if decode else quote(text, safe="")
            else:
                if decode:
                    value = json.loads(f'"{text}"')
                else:
                    value = json.dumps(text, ensure_ascii=True)[1:-1]

            self.output.setPlainText(value)
        except Exception as error:
            QMessageBox.warning(self, "Ошибка", str(error))

    def swap(self):
        text = self.output.toPlainText()
        self.output.clear()
        self.input.setPlainText(text)

    def clear(self):
        self.input.clear()
        self.output.clear()

    def copy(self):
        if self.output.toPlainText():
            QApplication.clipboard().setText(self.output.toPlainText())
