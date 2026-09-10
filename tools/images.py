from pathlib import Path

from PIL import Image, ImageOps
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tools.task import Task


def size_text(size):
    names = ["Б", "КБ", "МБ", "ГБ"]
    value = float(size)

    for name in names:
        if value < 1024 or name == names[-1]:
            return f"{value:.1f} {name}" if name != "Б" else f"{int(value)} {name}"
        value /= 1024


def free(path):
    if not path.exists():
        return path

    index = 1
    while True:
        value = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not value.exists():
            return value
        index += 1


class List(QListWidget):
    dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        paths = [path for path in paths if path.is_file()]

        if paths:
            self.dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class Images(QWidget):
    def __init__(self):
        super().__init__()

        self.files = []
        self.list = List()
        self.preview = QLabel("Предпросмотр")
        self.info = QLabel()
        self.format = QComboBox()
        self.resize_box = QCheckBox("Изменить размер")
        self.mode = QComboBox()
        self.width = QSpinBox()
        self.height = QSpinBox()
        self.width_label = QLabel("Ширина")
        self.height_label = QLabel("Высота")
        self.percent = QSpinBox()
        self.keep = QCheckBox("Сохранять пропорции")
        self.quality = QSlider(Qt.Horizontal)
        self.quality_text = QLabel()
        self.rotate = QComboBox()
        self.meta = QCheckBox("Удалить EXIF")
        self.status = QLabel()
        self.progress = QProgressBar()
        self.cancel = QPushButton("Отмена")
        self.task = None

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Изображения")
        title.setObjectName("heading")

        description = QLabel("Конвертация, изменение размера и пакетная обработка изображений.")
        description.setObjectName("description")

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        add = QPushButton("Добавить")
        clear = QPushButton("Очистить")
        add.clicked.connect(self.pick)
        clear.clicked.connect(self.clear)
        buttons.addWidget(add)
        buttons.addWidget(clear)
        buttons.addStretch()

        body = QHBoxLayout()
        body.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(10)
        self.list.setMinimumWidth(280)
        self.list.currentRowChanged.connect(self.show_preview)
        self.list.dropped.connect(self.add)
        left.addWidget(self.list, 1)

        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(320, 220)
        self.preview.setObjectName("preview")
        left.addWidget(self.preview, 1)
        self.info.setObjectName("muted")
        left.addWidget(self.info)

        options = QGridLayout()
        options.setHorizontalSpacing(10)
        options.setVerticalSpacing(10)

        self.format.addItems(["PNG", "JPG", "WEBP"])
        self.mode.addItems(["Пиксели", "Проценты"])
        self.mode.currentTextChanged.connect(self.change_mode)

        for box in (self.width, self.height):
            box.setRange(1, 20000)
        self.width.setValue(1920)
        self.height.setValue(1080)

        self.percent.setRange(1, 500)
        self.percent.setValue(100)
        self.percent.setSuffix(" %")
        self.percent.hide()

        self.keep.setChecked(True)

        self.quality.setRange(1, 100)
        self.quality.setValue(92)
        self.quality.valueChanged.connect(self.change_quality)
        self.change_quality(92)

        self.rotate.addItems(["0°", "90°", "180°", "270°"])
        self.meta.setChecked(True)

        options.addWidget(QLabel("Формат"), 0, 0)
        options.addWidget(self.format, 0, 1, 1, 2)
        options.addWidget(self.resize_box, 1, 0, 1, 3)
        options.addWidget(QLabel("Режим"), 2, 0)
        options.addWidget(self.mode, 2, 1, 1, 2)
        options.addWidget(self.width_label, 3, 0)
        options.addWidget(self.width, 3, 1)
        options.addWidget(self.height_label, 4, 0)
        options.addWidget(self.height, 4, 1)
        options.addWidget(self.percent, 3, 1, 2, 2)
        options.addWidget(self.keep, 5, 0, 1, 3)
        options.addWidget(QLabel("Качество"), 6, 0)
        options.addWidget(self.quality, 6, 1)
        options.addWidget(self.quality_text, 6, 2)
        options.addWidget(QLabel("Поворот"), 7, 0)
        options.addWidget(self.rotate, 7, 1, 1, 2)
        options.addWidget(self.meta, 8, 0, 1, 3)

        convert = QPushButton("Обработать")
        convert.setObjectName("mainButton")
        convert.clicked.connect(self.convert)
        options.addWidget(convert, 9, 0, 1, 3)
        options.setRowStretch(10, 1)

        body.addLayout(left, 3)
        body.addLayout(options, 2)

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
        layout.addLayout(buttons)
        layout.addLayout(body, 1)
        layout.addLayout(task_row)

    def pick(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите изображения",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff)",
        )

        self.add([Path(file) for file in files])

    def add(self, files):
        types = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

        for file in files:
            if file.suffix.lower() in types and file not in self.files:
                self.files.append(file)
                self.list.addItem(file.name)

        if self.files and self.list.currentRow() < 0:
            self.list.setCurrentRow(0)

        self.update_size()

    def clear(self):
        self.files.clear()
        self.list.clear()
        self.preview.setPixmap(QPixmap())
        self.preview.setText("Предпросмотр")
        self.info.clear()
        self.status.clear()

    def show_preview(self, index):
        if index < 0 or index >= len(self.files):
            return

        file = self.files[index]
        pixmap = QPixmap(str(file))

        if not pixmap.isNull():
            size = self.preview.size() - QSize(16, 16)
            pixmap = pixmap.scaled(
                size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.preview.setPixmap(pixmap)

        try:
            with Image.open(file) as image:
                format = image.format or file.suffix[1:].upper()
                size = size_text(file.stat().st_size)
                self.info.setText(f"{image.width} × {image.height} · {size} · {format}")
        except Exception:
            self.info.setText(size_text(file.stat().st_size))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.show_preview(self.list.currentRow())

    def update_size(self):
        if self.files:
            size = sum(file.stat().st_size for file in self.files if file.exists())
            self.status.setText(f"Файлов: {len(self.files)} · исходный размер: {size_text(size)}")

    def change_mode(self, mode):
        percent = mode == "Проценты"
        self.width.setVisible(not percent)
        self.height.setVisible(not percent)
        self.width_label.setVisible(not percent)
        self.height_label.setVisible(not percent)
        self.keep.setVisible(not percent)
        self.percent.setVisible(percent)

    def change_quality(self, value):
        self.quality_text.setText(str(value))

    def convert(self):
        if not self.files:
            QMessageBox.warning(self, "Файлы не выбраны", "Добавьте хотя бы одно изображение.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Папка для сохранения")

        if not folder:
            return

        files = self.files.copy()
        folder = Path(folder)
        format = self.format.currentText()
        resize = self.resize_box.isChecked()
        mode = self.mode.currentText()
        width = self.width.value()
        height = self.height.value()
        percent = self.percent.value()
        keep = self.keep.isChecked()
        quality = self.quality.value()
        angle = int(self.rotate.currentText().replace("°", ""))
        meta = self.meta.isChecked()
        extension = {"PNG": ".png", "JPG": ".jpg", "WEBP": ".webp"}[format]

        def run(progress, info, stop):
            total = len(files)
            saved = []

            for i, source in enumerate(files, 1):
                if stop():
                    return None

                info(f"Обработка: {source.name}")
                target = free(folder / f"{source.stem}{extension}")

                with Image.open(source) as image:
                    image.load()
                    image = ImageOps.exif_transpose(image)
                    exif_data = image.getexif()
                    exif = exif_data.tobytes() if exif_data else None

                    if resize:
                        if mode == "Проценты":
                            w = max(1, round(image.width * percent / 100))
                            h = max(1, round(image.height * percent / 100))
                            image = image.resize((w, h), Image.Resampling.LANCZOS)
                        elif keep:
                            image.thumbnail((width, height), Image.Resampling.LANCZOS)
                        else:
                            image = image.resize((width, height), Image.Resampling.LANCZOS)

                    if angle:
                        image = image.rotate(angle, expand=True)

                    if format == "JPG" and image.mode not in ("RGB", "L"):
                        image = image.convert("RGB")

                    params = {}
                    if format in ("JPG", "WEBP"):
                        params["quality"] = quality
                    if format == "PNG":
                        params["optimize"] = True
                    if not meta and exif and format in ("JPG", "WEBP"):
                        params["exif"] = exif

                    image.save(target, format=format, **params)

                saved.append(target)
                progress(int(i * 100 / total))

            return saved

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

    def done(self, files):
        self.progress.hide()
        self.cancel.hide()

        if files is None:
            self.status.setText("Операция отменена")
            return

        size = sum(file.stat().st_size for file in files)
        self.status.setText(f"Готово: {len(files)} · результат: {size_text(size)}")

    def fail(self, text):
        self.progress.hide()
        self.cancel.hide()
        QMessageBox.critical(self, "Ошибка", text)
