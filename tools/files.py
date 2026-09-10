import hashlib
import shutil
from pathlib import Path

from send2trash import send2trash
from PySide6.QtCore import QDir, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from tools.task import Task


def size_text(size):
    names = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    value = float(size)

    for name in names:
        if value < 1024 or name == names[-1]:
            return f"{value:.1f} {name}" if name != "Б" else f"{int(value)} {name}"
        value /= 1024


def free(path):
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    index = 1

    while True:
        name = path.with_name(f"{stem} ({index}){suffix}")
        if not name.exists():
            return name
        index += 1


def all_files(path):
    if path.is_file():
        return [path]

    return [file for file in path.rglob("*") if file.is_file()]


def total_size(paths, stop=None):
    size = 0

    for path in paths:
        if stop and stop():
            return None
        if path.is_file():
            size += path.stat().st_size
        elif path.is_dir():
            for file in path.rglob("*"):
                if stop and stop():
                    return None
                if file.is_file():
                    size += file.stat().st_size

    return size


def copy_file(source, target, add, stop):
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")

    try:
        with source.open("rb") as src, part.open("wb") as dst:
            while True:
                if stop():
                    return False

                data = src.read(1024 * 1024)
                if not data:
                    break

                dst.write(data)
                add(len(data))

        shutil.copystat(source, part)
        part.replace(target)
        return True
    finally:
        if part.exists():
            part.unlink(missing_ok=True)


def copy_path(source, target, add, stop):
    if source.is_file():
        return copy_file(source, target, add, stop)

    target.mkdir(parents=True, exist_ok=True)

    for item in source.rglob("*"):
        if stop():
            return False

        part = target / item.relative_to(source)

        if item.is_dir():
            part.mkdir(parents=True, exist_ok=True)
        elif item.is_file() and not copy_file(item, part, add, stop):
            return False

    try:
        shutil.copystat(source, target)
    except OSError:
        pass

    return True


def remove(path):
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


class Tree(QTreeView):
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
        paths = [path for path in paths if path.exists()]

        if paths:
            self.dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class Files(QWidget):
    def __init__(self):
        super().__init__()

        self.folder = Path.home()
        self.model = QFileSystemModel(self)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.model.setRootPath(str(self.folder))
        self.model.setNameFilterDisables(False)

        self.path = QLineEdit(str(self.folder))
        self.search = QLineEdit()
        self.tree = Tree()
        self.status = QLabel()
        self.progress = QProgressBar()
        self.cancel = QPushButton("Отмена")
        self.task = None

        self.setup()
        self.open(self.folder)

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Менеджер файлов")
        title.setObjectName("heading")

        description = QLabel("Просмотр, поиск, копирование, перемещение и работа с файлами.")
        description.setObjectName("description")

        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        folder_button = QPushButton("Открыть папку")
        folder_button.clicked.connect(self.pick_folder)

        home_button = QPushButton("Домой")
        home_button.clicked.connect(lambda: self.open(Path.home()))

        self.path.returnPressed.connect(self.open_path)

        path_row.addWidget(self.path, 1)
        path_row.addWidget(home_button)
        path_row.addWidget(folder_button)

        self.search.setPlaceholderText("Поиск в текущей папке")
        self.search.textChanged.connect(self.filter)

        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.AscendingOrder)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.doubleClicked.connect(self.enter)
        self.tree.dropped.connect(self.drop)

        row = QHBoxLayout()
        row.setSpacing(8)

        folder = QPushButton("Новая папка")
        rename = QPushButton("Переименовать")
        copy = QPushButton("Копировать")
        move = QPushButton("Переместить")
        path = QPushButton("Копировать путь")
        size = QPushButton("Размер")
        duplicates = QPushButton("Дубликаты")
        delete = QPushButton("В корзину")

        folder.clicked.connect(self.new_folder)
        rename.clicked.connect(self.rename)
        copy.clicked.connect(self.copy)
        move.clicked.connect(self.move)
        path.clicked.connect(self.copy_path)
        size.clicked.connect(self.size)
        duplicates.clicked.connect(self.duplicates)
        delete.clicked.connect(self.delete)

        row.addWidget(folder)
        row.addWidget(rename)
        row.addWidget(copy)
        row.addWidget(move)
        row.addWidget(path)
        row.addStretch()
        row.addWidget(size)
        row.addWidget(duplicates)
        row.addWidget(delete)

        task_row = QHBoxLayout()
        task_row.setSpacing(8)

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
        layout.addSpacing(6)
        layout.addLayout(path_row)
        layout.addWidget(self.search)
        layout.addWidget(self.tree, 1)
        layout.addLayout(row)
        layout.addLayout(task_row)

    def selected(self):
        paths = []

        for index in self.tree.selectionModel().selectedRows(0):
            path = Path(self.model.filePath(index))
            if path not in paths:
                paths.append(path)

        return paths

    def one(self):
        paths = self.selected()
        return paths[0] if len(paths) == 1 else None

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку", str(self.folder))

        if folder:
            self.open(Path(folder))

    def open_path(self):
        folder = Path(self.path.text()).expanduser()

        if folder.is_dir():
            self.open(folder)
        else:
            QMessageBox.warning(self, "Папка не найдена", "Указанный путь не существует.")

    def open(self, folder):
        self.folder = Path(folder)
        self.path.setText(str(self.folder))
        self.tree.setRootIndex(self.model.index(str(self.folder)))
        self.search.clear()

    def enter(self, index):
        path = Path(self.model.filePath(index))

        if path.is_dir():
            self.open(path)

    def filter(self, text):
        text = text.strip()
        self.model.setNameFilters([f"*{text}*"] if text else ["*"])

    def new_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Имя папки:")

        if not ok or not name.strip():
            return

        try:
            (self.folder / name.strip()).mkdir()
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def rename(self):
        source = self.one()

        if not source:
            QMessageBox.information(self, "Переименование", "Выберите один файл или папку.")
            return

        name, ok = QInputDialog.getText(
            self,
            "Переименование",
            "Новое имя:",
            text=source.name,
        )

        if not ok or not name or name == source.name:
            return

        try:
            source.rename(source.with_name(name))
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def copy(self):
        paths = self.selected()

        if not paths:
            return

        folder = QFileDialog.getExistingDirectory(self, "Куда копировать", str(self.folder))

        if folder:
            self.start_copy(paths, Path(folder), False)

    def move(self):
        paths = self.selected()

        if not paths:
            return

        folder = QFileDialog.getExistingDirectory(self, "Куда переместить", str(self.folder))

        if folder:
            self.start_copy(paths, Path(folder), True)

    def drop(self, paths):
        self.start_copy(paths, self.folder, False)

    def start_copy(self, paths, folder, move):
        if self.task and self.task.isRunning():
            return

        def run(progress, info, stop):
            info("Подготовка...")
            total = total_size(paths, stop)
            if total is None:
                return False

            done = 0

            def add(size):
                nonlocal done
                done += size
                progress(100 if total == 0 else int(done * 100 / total))

            for source in paths:
                if stop():
                    return False

                if source.is_dir():
                    src = source.resolve()
                    dst = folder.resolve()
                    if src == dst or src in dst.parents:
                        raise ValueError(
                            "Нельзя копировать папку внутрь самой себя."
                        )

                target = free(folder / source.name)
                info(f"{'Перемещение' if move else 'Копирование'}: {source.name}")

                if not copy_path(source, target, add, stop):
                    if target.exists():
                        remove(target)
                    return False

                if move:
                    remove(source)

            progress(100)
            return True

        self.run_task(run, "Готово")

    def copy_path(self):
        paths = self.selected()

        if paths:
            QApplication.clipboard().setText("\n".join(str(path) for path in paths))
            self.status.setText("Путь скопирован")

    def size(self):
        paths = self.selected()

        if not paths:
            return

        def run(progress, info, stop):
            info("Подсчёт размера...")
            size = 0
            count = 0

            for path in paths:
                files = all_files(path)
                for file in files:
                    if stop():
                        return None
                    size += file.stat().st_size
                    count += 1

            return size, count

        def done(value):
            self.finish()
            if value:
                size, count = value
                self.status.setText(f"{size_text(size)}, файлов: {count}")

        self.start(run, done)

    def duplicates(self):
        if self.task and self.task.isRunning():
            return

        folder = self.folder

        def run(progress, info, stop):
            info("Поиск файлов...")
            sizes = {}

            for file in folder.rglob("*"):
                if stop():
                    return None
                if file.is_file():
                    sizes.setdefault(file.stat().st_size, []).append(file)

            files = [file for group in sizes.values() if len(group) > 1 for file in group]
            total = sum(file.stat().st_size for file in files)
            done = 0
            hashes = {}

            for file in files:
                if stop():
                    return None

                value = hashlib.sha256()
                with file.open("rb") as f:
                    while True:
                        data = f.read(1024 * 1024)
                        if not data:
                            break
                        value.update(data)
                        done += len(data)
                        progress(100 if total == 0 else int(done * 100 / total))

                hashes.setdefault((file.stat().st_size, value.hexdigest()), []).append(file)

            return [group for group in hashes.values() if len(group) > 1]

        def done(groups):
            self.finish()

            if groups is None:
                return

            if not groups:
                QMessageBox.information(self, "Дубликаты", "Дубликаты не найдены.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Дубликаты")
            dialog.resize(760, 520)
            layout = QVBoxLayout(dialog)
            text = QPlainTextEdit()
            text.setReadOnly(True)

            blocks = []
            for i, group in enumerate(groups, 1):
                blocks.append(f"Группа {i}\n" + "\n".join(str(path) for path in group))

            text.setPlainText("\n\n".join(blocks))
            layout.addWidget(text)
            dialog.exec()

        self.start(run, done)

    def delete(self):
        paths = self.selected()

        if not paths:
            return

        names = ", ".join(path.name for path in paths[:3])
        if len(paths) > 3:
            names += f" и ещё {len(paths) - 3}"

        answer = QMessageBox.question(
            self,
            "Корзина",
            f"Переместить в корзину: {names}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            for path in paths:
                send2trash(str(path))
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", str(error))

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

    def run_task(self, run, text):
        def done(value):
            self.finish()
            self.status.setText(text if value else "Операция отменена")

        self.start(run, done)

    def stop(self):
        if self.task and self.task.isRunning():
            self.task.requestInterruption()
            self.status.setText("Отмена...")

    def finish(self):
        self.progress.hide()
        self.cancel.hide()

    def fail(self, text):
        self.finish()
        QMessageBox.critical(self, "Ошибка", text)
