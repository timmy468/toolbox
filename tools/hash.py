import hashlib
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Hash(QWidget):
    def __init__(self):
        super().__init__()

        self.file = QLineEdit()
        self.type = QComboBox()
        self.result = QLineEdit()

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Хэш")
        title.setObjectName("heading")

        description = QLabel("MD5, SHA-1, SHA-256 и SHA-512 для любого файла.")
        description.setObjectName("description")

        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.file.setPlaceholderText("Выберите файл")
        self.file.setReadOnly(True)

        choose = QPushButton("Выбрать")
        choose.clicked.connect(self.pick)

        file_row.addWidget(self.file, 1)
        file_row.addWidget(choose)

        self.type.addItems(["MD5", "SHA-1", "SHA-256", "SHA-512"])

        calculate = QPushButton("Посчитать")
        calculate.setObjectName("mainButton")
        calculate.clicked.connect(self.calculate)

        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Результат появится здесь")

        copy = QPushButton("Копировать")
        copy.clicked.connect(self.copy)

        result_row = QHBoxLayout()
        result_row.setSpacing(8)
        result_row.addWidget(self.result, 1)
        result_row.addWidget(copy)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(12)
        layout.addLayout(file_row)
        layout.addWidget(QLabel("Алгоритм"))
        layout.addWidget(self.type)
        layout.addSpacing(8)
        layout.addWidget(calculate)
        layout.addSpacing(12)
        layout.addLayout(result_row)
        layout.addStretch()

    def pick(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл")

        if file:
            self.file.setText(file)
            self.result.clear()

    def calculate(self):
        file = Path(self.file.text())

        if not file.is_file():
            QMessageBox.warning(self, "Файл не выбран", "Сначала выберите файл.")
            return

        types = {
            "MD5": hashlib.md5,
            "SHA-1": hashlib.sha1,
            "SHA-256": hashlib.sha256,
            "SHA-512": hashlib.sha512,
        }

        value = types[self.type.currentText()]()

        try:
            with file.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    value.update(chunk)

            self.result.setText(value.hexdigest())
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def copy(self):
        if self.result.text():
            QApplication.clipboard().setText(self.result.text())
