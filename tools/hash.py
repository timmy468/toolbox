import hashlib
import zlib
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tools.task import Task


class Hash(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        self.file = QLineEdit()
        self.type = QComboBox()
        self.result = QLineEdit()
        self.expected = QLineEdit()
        self.status = QLabel()
        self.progress = QProgressBar()
        self.cancel = QPushButton("Отмена")
        self.task = None

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Хэш")
        title.setObjectName("heading")

        description = QLabel("Хэши файлов и проверка контрольной суммы.")
        description.setObjectName("description")

        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.file.setPlaceholderText("Выберите файл или перетащите его сюда")
        self.file.setReadOnly(True)

        choose = QPushButton("Выбрать")
        choose.clicked.connect(self.pick)

        file_row.addWidget(self.file, 1)
        file_row.addWidget(choose)

        self.type.addItems(
            [
                "MD5 · устаревший",
                "SHA-1 · устаревший",
                "SHA-256",
                "SHA-512",
                "BLAKE2b",
                "BLAKE2s",
                "CRC32",
            ]
        )

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

        self.expected.setPlaceholderText("Вставьте ожидаемый хэш для проверки")
        self.expected.textChanged.connect(self.verify)

        task_row = QHBoxLayout()
        self.status.setObjectName("muted")
        self.progress.setRange(0, 100)
        self.progress.hide()
        self.cancel.hide()
        self.cancel.clicked.connect(self.stop)
        task_row.addWidget(self.status, 1)
        task_row.addWidget(self.progress, 1)
        task_row.addWidget(self.cancel)

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
        layout.addWidget(QLabel("Ожидаемый хэш"))
        layout.addWidget(self.expected)
        layout.addLayout(task_row)
        layout.addStretch()

    def pick(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл")

        if file:
            self.set_file(Path(file))

    def set_file(self, file):
        self.file.setText(str(file))
        self.result.clear()
        self.status.clear()

    def calculate(self):
        file = Path(self.file.text())

        if not file.is_file():
            QMessageBox.warning(self, "Файл не выбран", "Сначала выберите файл.")
            return

        type = self.type.currentText()
        self.status.setObjectName("muted")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

        def run(progress, info, stop):
            size = file.stat().st_size
            done = 0
            info("Расчёт...")

            if type == "CRC32":
                value = 0

                with file.open("rb") as f:
                    while True:
                        if stop():
                            return None
                        data = f.read(1024 * 1024)
                        if not data:
                            break
                        value = zlib.crc32(data, value)
                        done += len(data)
                        progress(100 if size == 0 else int(done * 100 / size))

                return f"{value & 0xffffffff:08x}"

            types = {
                "MD5 · устаревший": hashlib.md5,
                "SHA-1 · устаревший": hashlib.sha1,
                "SHA-256": hashlib.sha256,
                "SHA-512": hashlib.sha512,
                "BLAKE2b": hashlib.blake2b,
                "BLAKE2s": hashlib.blake2s,
            }

            value = types[type]()

            with file.open("rb") as f:
                while True:
                    if stop():
                        return None
                    data = f.read(1024 * 1024)
                    if not data:
                        break
                    value.update(data)
                    done += len(data)
                    progress(100 if size == 0 else int(done * 100 / size))

            return value.hexdigest()

        self.start(run)

    def start(self, run):
        if self.task and self.task.isRunning():
            return

        self.task = Task(run)
        self.task.progress.connect(self.progress.setValue)
        self.task.info.connect(self.status.setText)
        self.task.error.connect(self.fail)
        self.task.done.connect(self.done)
        self.progress.setValue(0)
        self.progress.show()
        self.cancel.show()
        self.task.start()

    def stop(self):
        if self.task and self.task.isRunning():
            self.task.requestInterruption()
            self.status.setText("Отмена...")

    def done(self, value):
        self.progress.hide()
        self.cancel.hide()

        if value is None:
            self.status.setText("Операция отменена")
            return

        self.result.setText(value)
        self.status.setText("Готово")
        self.verify()

    def fail(self, text):
        self.progress.hide()
        self.cancel.hide()
        QMessageBox.critical(self, "Ошибка", text)

    def verify(self):
        expected = self.expected.text().strip().replace(" ", "").lower()
        result = self.result.text().strip().lower()

        if not expected or not result:
            return

        if expected == result:
            self.status.setText("Совпадает")
            self.status.setObjectName("ok")
        else:
            self.status.setText("Не совпадает")
            self.status.setObjectName("bad")

        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def copy(self):
        if self.result.text():
            QApplication.clipboard().setText(self.result.text())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        files = [file for file in files if file.is_file()]

        if files:
            self.set_file(files[0])
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
