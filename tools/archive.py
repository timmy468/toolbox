import zipfile
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tools.task import Task


def safe(folder, name):
    root = folder.resolve()
    path = (folder / name).resolve()
    return path == root or root in path.parents


def copy(src, dst, add, stop):
    while True:
        if stop():
            return False

        data = src.read(1024 * 1024)
        if not data:
            return True

        dst.write(data)
        add(len(data))


class Archive(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        self.file = QLineEdit()
        self.list = QListWidget()
        self.status = QLabel()
        self.progress = QProgressBar()
        self.cancel = QPushButton("Отмена")
        self.task = None

        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Архивы")
        title.setObjectName("heading")

        description = QLabel("Создание, просмотр и распаковка ZIP архивов.")
        description.setObjectName("description")

        create_row = QHBoxLayout()
        files = QPushButton("Архивировать файлы")
        folder = QPushButton("Архивировать папку")
        files.clicked.connect(self.create_files)
        folder.clicked.connect(self.create_folder)
        create_row.addWidget(files)
        create_row.addWidget(folder)
        create_row.addStretch()

        file_row = QHBoxLayout()
        self.file.setReadOnly(True)
        self.file.setPlaceholderText("Выберите ZIP или перетащите его сюда")
        choose = QPushButton("Открыть ZIP")
        extract = QPushButton("Распаковать")
        extract.setObjectName("mainButton")
        choose.clicked.connect(self.pick)
        extract.clicked.connect(self.extract)
        file_row.addWidget(self.file, 1)
        file_row.addWidget(choose)
        file_row.addWidget(extract)

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
        layout.addLayout(create_row)
        layout.addLayout(file_row)
        layout.addWidget(self.list, 1)
        layout.addLayout(task_row)

    def create_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы")

        if not files:
            return

        target, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить ZIP",
            "archive.zip",
            "ZIP (*.zip)",
        )

        if target:
            self.create([Path(file) for file in files], Path(target), None)

    def create_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if not folder:
            return

        source = Path(folder)
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить ZIP",
            str(source.parent / f"{source.name}.zip"),
            "ZIP (*.zip)",
        )

        if target:
            self.create([source], Path(target), source.parent)

    def create(self, items, target, root):
        if target.suffix.lower() != ".zip":
            target = target.with_suffix(".zip")

        def run(progress, info, stop):
            files = []
            skip = {target.resolve(), target.with_name(target.name + ".part").resolve()}

            for item in items:
                if item.is_file():
                    files.append((item, item.name))
                elif item.is_dir():
                    base = root or item.parent
                    for file in item.rglob("*"):
                        if file.is_file() and file.resolve() not in skip:
                            files.append((file, str(file.relative_to(base))))

            total = sum(file.stat().st_size for file, name in files)
            done = 0
            part = target.with_name(target.name + ".part")

            def add(size):
                nonlocal done
                done += size
                progress(100 if total == 0 else int(done * 100 / total))

            try:
                with zipfile.ZipFile(part, "w", zipfile.ZIP_DEFLATED) as archive:
                    for file, name in files:
                        if stop():
                            return None

                        info(f"Добавление: {file.name}")
                        with file.open("rb") as src, archive.open(name, "w") as dst:
                            if not copy(src, dst, add, stop):
                                return None

                part.replace(target)
                return target
            finally:
                if part.exists():
                    part.unlink(missing_ok=True)

        self.start(run, self.created)

    def pick(self):
        file, _ = QFileDialog.getOpenFileName(self, "Открыть ZIP", "", "ZIP (*.zip)")

        if file:
            self.open(Path(file))

    def open(self, file):
        try:
            self.list.clear()
            with zipfile.ZipFile(file, "r") as archive:
                for item in archive.infolist():
                    size = item.file_size
                    self.list.addItem(f"{item.filename}    {size} Б")

            self.file.setText(str(file))
            self.status.setText(f"Файлов: {self.list.count()}")
        except (OSError, zipfile.BadZipFile) as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def extract(self):
        file = Path(self.file.text())

        if not file.is_file():
            QMessageBox.warning(self, "Архив", "Сначала выберите ZIP архив.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Куда распаковать")

        if not folder:
            return

        folder = Path(folder)

        def run(progress, info, stop):
            with zipfile.ZipFile(file, "r") as archive:
                items = archive.infolist()
                total = sum(item.file_size for item in items if not item.is_dir())
                done = 0

                def add(size):
                    nonlocal done
                    done += size
                    progress(100 if total == 0 else int(done * 100 / total))

                for item in items:
                    if stop():
                        return None
                    if not safe(folder, item.filename):
                        raise ValueError(f"Небезопасный путь: {item.filename}")

                    target = folder / item.filename
                    info(f"Распаковка: {item.filename}")

                    if item.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                        continue

                    target.parent.mkdir(parents=True, exist_ok=True)
                    part = target.with_name(target.name + ".part")

                    try:
                        with archive.open(item, "r") as src, part.open("wb") as dst:
                            if not copy(src, dst, add, stop):
                                return None
                        part.replace(target)
                    finally:
                        if part.exists():
                            part.unlink(missing_ok=True)

            return folder

        self.start(run, self.extracted)

    def start(self, run, done):
        if self.task and self.task.isRunning():
            return

        self.task = Task(run)
        self.task.progress.connect(self.progress.setValue)
        self.task.info.connect(self.status.setText)
        self.task.error.connect(self.fail)
        self.task.done.connect(done)
        self.progress.setValue(0)
        self.progress.show()
        self.cancel.show()
        self.task.start()

    def stop(self):
        if self.task and self.task.isRunning():
            self.task.requestInterruption()
            self.status.setText("Отмена...")

    def created(self, file):
        self.finish()
        if file is None:
            self.status.setText("Операция отменена")
            return
        self.status.setText("Архив создан")
        self.open(file)

    def extracted(self, folder):
        self.finish()
        self.status.setText("Готово" if folder else "Операция отменена")

    def finish(self):
        self.progress.hide()
        self.cancel.hide()

    def fail(self, text):
        self.finish()
        QMessageBox.critical(self, "Ошибка", text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        files = [file for file in files if file.is_file() and file.suffix.lower() == ".zip"]

        if files:
            self.open(files[0])
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
