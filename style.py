dark = """
QWidget {
    background: #0f1115;
    color: #e8eaf0;
    font-family: "Segoe UI";
    font-size: 14px;
}

#menu {
    background: #15181e;
    border-right: 1px solid #252a33;
}

#title {
    color: #ffffff;
    font-size: 25px;
    font-weight: 700;
}

#subtitle {
    color: #7f8795;
    font-size: 13px;
}

#menuButton {
    background: transparent;
    border: 0;
    border-radius: 9px;
    padding: 11px 13px;
    text-align: left;
    color: #aeb5c2;
}

#menuButton:hover {
    background: #1d2129;
    color: #ffffff;
}

#menuButton:checked {
    background: #262c36;
    color: #ffffff;
    font-weight: 600;
}

#heading {
    color: #ffffff;
    font-size: 25px;
    font-weight: 700;
}

#description,
#muted {
    color: #858d9b;
    font-size: 13px;
}

#ok {
    color: #7ddc9b;
    font-weight: 600;
}

#bad {
    color: #ff8d8d;
    font-weight: 600;
}

#preview {
    border: 1px solid #2a3039;
    border-radius: 8px;
}

QPushButton {
    background: #242a34;
    border: 1px solid #303744;
    border-radius: 8px;
    padding: 9px 14px;
    color: #f1f3f6;
}

QPushButton:hover {
    background: #2b323e;
}

QPushButton:pressed {
    background: #202630;
}

QPushButton:disabled {
    color: #69717e;
    background: #1a1e25;
}

QPushButton#mainButton {
    background: #e9edf5;
    color: #111318;
    border: 0;
    font-weight: 600;
}

QPushButton#mainButton:hover {
    background: #ffffff;
}

QPushButton#cardButton {
    text-align: left;
    padding: 16px;
    font-size: 14px;
}

QLineEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QListWidget,
QTabWidget::pane {
    background: #101318;
    border: 1px solid #2a3039;
    border-radius: 8px;
    padding: 9px 10px;
    color: #e8eaf0;
    selection-background-color: #414a59;
}

QLineEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QListWidget:focus {
    border: 1px solid #525b69;
}

QTreeView {
    background: #111419;
    border: 1px solid #252b34;
    border-radius: 9px;
    padding: 4px;
}

QTreeView::item {
    height: 28px;
}

QTreeView::item:selected,
QListWidget::item:selected {
    background: #303744;
    border-radius: 5px;
}

QHeaderView::section {
    background: #171b21;
    color: #969eaa;
    padding: 7px;
    border: 0;
    border-bottom: 1px solid #252a33;
}

QProgressBar {
    background: #171b21;
    border: 1px solid #2a3039;
    border-radius: 6px;
    text-align: center;
    min-height: 18px;
}

QProgressBar::chunk {
    background: #596575;
    border-radius: 5px;
}

QTabBar::tab {
    background: #171b21;
    border: 1px solid #2a3039;
    padding: 8px 13px;
    margin-right: 4px;
    border-radius: 7px;
}

QTabBar::tab:selected {
    background: #2a3039;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #252b34;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #e9edf5;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #303641;
    border-radius: 5px;
    min-height: 30px;
}

QMessageBox {
    background: #171a20;
}
"""

light = """
QWidget {
    background: #f4f6f9;
    color: #20242b;
    font-family: "Segoe UI";
    font-size: 14px;
}

#menu {
    background: #ffffff;
    border-right: 1px solid #dfe3e9;
}

#title,
#heading {
    color: #15181d;
    font-size: 25px;
    font-weight: 700;
}

#subtitle,
#description,
#muted {
    color: #747d89;
    font-size: 13px;
}

#menuButton {
    background: transparent;
    border: 0;
    border-radius: 9px;
    padding: 11px 13px;
    text-align: left;
    color: #505966;
}

#menuButton:hover,
#menuButton:checked {
    background: #e9edf2;
    color: #111318;
}

#menuButton:checked {
    font-weight: 600;
}

#ok {
    color: #168544;
    font-weight: 600;
}

#bad {
    color: #c73b3b;
    font-weight: 600;
}

#preview {
    border: 1px solid #d8dde5;
    border-radius: 8px;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #d5dae2;
    border-radius: 8px;
    padding: 9px 14px;
    color: #242a32;
}

QPushButton:hover {
    background: #f7f8fa;
}

QPushButton:disabled {
    color: #9ba2ad;
    background: #eef0f3;
}

QPushButton#mainButton {
    background: #222831;
    color: #ffffff;
    border: 0;
    font-weight: 600;
}

QPushButton#mainButton:hover {
    background: #11151a;
}

QPushButton#cardButton {
    text-align: left;
    padding: 16px;
    font-size: 14px;
}

QLineEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QListWidget,
QTreeView,
QTabWidget::pane {
    background: #ffffff;
    border: 1px solid #d8dde5;
    border-radius: 8px;
    padding: 9px 10px;
    color: #222831;
    selection-background-color: #cfd6e0;
}

QHeaderView::section {
    background: #f0f2f5;
    color: #626b76;
    padding: 7px;
    border: 0;
    border-bottom: 1px solid #d8dde5;
}

QTreeView::item {
    height: 28px;
}

QTreeView::item:selected,
QListWidget::item:selected {
    background: #dfe5ec;
    border-radius: 5px;
}

QProgressBar {
    background: #ffffff;
    border: 1px solid #d8dde5;
    border-radius: 6px;
    text-align: center;
    min-height: 18px;
}

QProgressBar::chunk {
    background: #7a8796;
    border-radius: 5px;
}

QTabBar::tab {
    background: #ffffff;
    border: 1px solid #d8dde5;
    padding: 8px 13px;
    margin-right: 4px;
    border-radius: 7px;
}

QTabBar::tab:selected {
    background: #e9edf2;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #d8dde5;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #222831;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
"""
