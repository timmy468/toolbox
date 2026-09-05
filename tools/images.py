from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import (
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


class Images(QWidget):
    def __init__(self):
        super().__init__()

        self.file = QLineEdit()
        self.format = QComboBox()

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Конвертер изображений")
        title.setObjectName("heading")

        description = QLabel("Конвертация PNG, JPG и WebP.")
        description.setObjectName("description")

        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.file.setPlaceholderText("Выберите изображение")
        self.file.setReadOnly(True)

        choose = QPushButton("Выбрать")
        choose.clicked.connect(self.pick)

        file_row.addWidget(self.file, 1)
        file_row.addWidget(choose)

        self.format.addItems(["PNG", "JPG", "WEBP"])

        convert = QPushButton("Конвертировать")
        convert.setObjectName("mainButton")
        convert.clicked.connect(self.convert)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(12)
        layout.addLayout(file_row)
        layout.addWidget(QLabel("Формат"))
        layout.addWidget(self.format)
        layout.addSpacing(8)
        layout.addWidget(convert)
        layout.addStretch()

    def pick(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )

        if file:
            self.file.setText(file)

    def convert(self):
        source = Path(self.file.text())

        if not source.is_file():
            QMessageBox.warning(self, "Файл не выбран", "Сначала выберите изображение.")
            return

        format = self.format.currentText()
        extension = {
            "PNG": ".png",
            "JPG": ".jpg",
            "WEBP": ".webp",
        }[format]

        target, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изображение",
            str(source.with_suffix(extension)),
            f"{format} (*{extension})",
        )

        if not target:
            return

        try:
            with Image.open(source) as image:
                if format == "JPG" and image.mode in ("RGBA", "LA", "P"):
                    image = image.convert("RGB")

                image.save(target, format=format, quality=95)

            QMessageBox.information(self, "Готово", "Изображение сохранено.")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", str(error))
