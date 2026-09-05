style = """
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

#description {
    color: #858d9b;
    font-size: 13px;
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

QPushButton#mainButton {
    background: #e9edf5;
    color: #111318;
    border: 0;
    font-weight: 600;
}

QPushButton#mainButton:hover {
    background: #ffffff;
}

QLineEdit,
QPlainTextEdit,
QComboBox {
    background: #101318;
    border: 1px solid #2a3039;
    border-radius: 8px;
    padding: 9px 10px;
    color: #e8eaf0;
    selection-background-color: #414a59;
}

QLineEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus {
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

QTreeView::item:selected {
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
