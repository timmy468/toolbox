import shutil
from pathlib import Path

from PySide6.QtCore import QDir, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class Files(QWidget):
    def __init__(self):
        super().__init__()

        self.folder = Path.home()
        self.model = QFileSystemModel(self)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.model.setRootPath(str(self.folder))

        self.path = QLineEdit(str(self.folder))
        self.tree = QTreeView()

        self.setup()
        self.open(self.folder)

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("Менеджер файлов")
        title.setObjectName("heading")

        description = QLabel("Просмотр, копирование, перемещение и удаление файлов.")
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

        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.AscendingOrder)
        self.tree.doubleClicked.connect(self.enter)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        rename = QPushButton("Переименовать")
        copy = QPushButton("Копировать")
        move = QPushButton("Переместить")
        delete = QPushButton("Удалить")

        rename.clicked.connect(self.rename)
        copy.clicked.connect(self.copy)
        move.clicked.connect(self.move)
        delete.clicked.connect(self.delete)

        buttons.addWidget(rename)
        buttons.addWidget(copy)
        buttons.addWidget(move)
        buttons.addStretch()
        buttons.addWidget(delete)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(6)
        layout.addLayout(path_row)
        layout.addWidget(self.tree, 1)
        layout.addLayout(buttons)

    def selected(self):
        index = self.tree.currentIndex()

        if not index.isValid():
            return None

        return Path(self.model.filePath(index))

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

    def enter(self, index):
        path = Path(self.model.filePath(index))

        if path.is_dir():
            self.open(path)

    def rename(self):
        source = self.selected()

        if not source:
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
        source = self.selected()

        if not source:
            return

        folder = QFileDialog.getExistingDirectory(self, "Куда копировать", str(self.folder))

        if not folder:
            return

        target = Path(folder) / source.name

        try:
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def move(self):
        source = self.selected()

        if not source:
            return

        folder = QFileDialog.getExistingDirectory(self, "Куда переместить", str(self.folder))

        if not folder:
            return

        try:
            shutil.move(str(source), str(Path(folder) / source.name))
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def delete(self):
        source = self.selected()

        if not source:
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить «{source.name}»?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            if source.is_dir():
                shutil.rmtree(source)
            else:
                source.unlink()
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))
