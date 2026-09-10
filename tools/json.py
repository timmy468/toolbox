import difflib
import json

from PySide6.QtCore import QRect, QRegularExpression, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPalette,
    QTextCharFormat,
    QTextFormat,
    QSyntaxHighlighter,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Area(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.area_size()

    def paintEvent(self, event):
        self.editor.paint_area(event)


class Editor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.area = Area(self)
        self.blockCountChanged.connect(self.update_width)
        self.updateRequest.connect(self.update_area)
        self.update_width()

    def area_size(self):
        return QSize(self.area_width(), 0)

    def area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_width(self):
        self.setViewportMargins(self.area_width(), 0, 0, 0)

    def update_area(self, rect, dy):
        if dy:
            self.area.scroll(0, dy)
        else:
            self.area.update(0, rect.y(), self.area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.area.setGeometry(QRect(rect.left(), rect.top(), self.area_width(), rect.height()))

    def paint_area(self, event):
        painter = QPainter(self.area)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Base).darker(105))

        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(self.palette().color(QPalette.PlaceholderText))
                painter.drawText(
                    0,
                    top,
                    self.area.width() - 7,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    str(number + 1),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            number += 1

    def mark(self, line=0):
        if not line:
            self.setExtraSelections([])
            return

        block = self.document().findBlockByNumber(line - 1)
        if not block.isValid():
            return

        selection = QTextEdit.ExtraSelection()
        selection.cursor = self.textCursor()
        selection.cursor.setPosition(block.position())
        selection.format.setBackground(QColor("#4a2929"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        self.setExtraSelections([selection])
        self.setTextCursor(selection.cursor)
        self.centerCursor()


class Highlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        string = QTextCharFormat()
        string.setForeground(QColor("#9bd49a"))

        number = QTextCharFormat()
        number.setForeground(QColor("#e6c07b"))

        value = QTextCharFormat()
        value.setForeground(QColor("#73b7ff"))

        self.rules = [
            (QRegularExpression(r'"(?:\\.|[^"\\])*"'), string),
            (QRegularExpression(r"-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b"), number),
            (QRegularExpression(r"\b(?:true|false|null)\b"), value),
        ]

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            match = pattern.globalMatch(text)
            while match.hasNext():
                value = match.next()
                self.setFormat(value.capturedStart(), value.capturedLength(), format)


bad = object()


class Json(QWidget):
    def __init__(self):
        super().__init__()

        self.text = Editor()
        self.error = QLabel()
        self.highlighter = Highlighter(self.text.document())
        self.setup()

    def setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(14)

        title = QLabel("JSON")
        title.setObjectName("heading")

        description = QLabel("Форматирование, проверка, сортировка и сравнение JSON.")
        description.setObjectName("description")

        self.text.setPlaceholderText('{"name":"Alex","age":16}')
        self.text.setLineWrapMode(QPlainTextEdit.NoWrap)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        open_button = QPushButton("Открыть")
        format_button = QPushButton("Форматировать")
        minify_button = QPushButton("Сжать")
        sort_button = QPushButton("Сортировать ключи")
        compare_button = QPushButton("Сравнить")
        copy_button = QPushButton("Копировать")
        save_button = QPushButton("Сохранить")

        format_button.setObjectName("mainButton")

        open_button.clicked.connect(self.open)
        format_button.clicked.connect(self.format)
        minify_button.clicked.connect(self.minify)
        sort_button.clicked.connect(self.sort)
        compare_button.clicked.connect(self.compare)
        copy_button.clicked.connect(self.copy)
        save_button.clicked.connect(self.save)

        buttons.addWidget(open_button)
        buttons.addWidget(format_button)
        buttons.addWidget(minify_button)
        buttons.addWidget(sort_button)
        buttons.addWidget(compare_button)
        buttons.addStretch()
        buttons.addWidget(copy_button)
        buttons.addWidget(save_button)

        self.error.setObjectName("muted")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(6)
        layout.addLayout(buttons)
        layout.addWidget(self.text, 1)
        layout.addWidget(self.error)

    def read(self, text=None, show=True):
        value = self.text.toPlainText() if text is None else text

        try:
            data = json.loads(value)
            if text is None:
                self.error.setText("JSON корректен")
                self.error.setObjectName("ok")
                self.error.style().unpolish(self.error)
                self.error.style().polish(self.error)
                self.text.mark()
            return data
        except json.JSONDecodeError as error:
            if show:
                self.error.setText(
                    f"Ошибка: строка {error.lineno}, столбец {error.colno} · {error.msg}"
                )
                self.error.setObjectName("bad")
                self.error.style().unpolish(self.error)
                self.error.style().polish(self.error)
                if text is None:
                    self.text.mark(error.lineno)
            return bad

    def format(self):
        data = self.read()

        if data is not bad:
            self.text.setPlainText(json.dumps(data, ensure_ascii=False, indent=4))

    def minify(self):
        data = self.read()

        if data is not bad:
            self.text.setPlainText(
                json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            )

    def sort(self):
        data = self.read()

        if data is not bad:
            self.text.setPlainText(
                json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)
            )

    def copy(self):
        if self.text.toPlainText():
            QApplication.clipboard().setText(self.text.toPlainText())

    def compare(self):
        left = self.read()

        if left is bad:
            return

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Сравнить с JSON",
            "",
            "JSON (*.json);;Все файлы (*)",
        )

        if not file:
            return

        try:
            with open(file, "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))
            return

        right = self.read(raw, False)

        if right is bad:
            QMessageBox.warning(self, "Ошибка", "Выбранный файл содержит некорректный JSON.")
            return

        a = json.dumps(left, ensure_ascii=False, indent=4, sort_keys=True).splitlines()
        b = json.dumps(right, ensure_ascii=False, indent=4, sort_keys=True).splitlines()
        diff = list(difflib.unified_diff(a, b, fromfile="Текущий", tofile=file, lineterm=""))

        if not diff:
            QMessageBox.information(self, "Сравнение", "JSON совпадают.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Сравнение JSON")
        dialog.resize(850, 600)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        text.setPlainText("\n".join(diff))
        layout.addWidget(text)
        dialog.exec()

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
            self.read()
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def save(self):
        if self.read() is bad:
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
