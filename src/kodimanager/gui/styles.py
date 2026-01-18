DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1f1f1f;
    color: #ffffff;
    font-family: 'Roboto', 'Segoe UI', sans-serif;
    font-size: 16px;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #1f1f1f;
}

QTabBar::tab {
    background-color: #2b2b2b;
    color: #aaaaaa;
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #60a5fa; /* Blue accent */
    color: #ffffff;
    font-weight: bold;
}

QPushButton {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 16px;
}

QPushButton:hover {
    background-color: #2563eb;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton#ActionBtn {
    background-color: #374151; /* Darker grey for secondary actions */
}

QPushButton#ActionBtn:hover {
    background-color: #4b5563;
}

QFrame#Card {
    background-color: #2b2b2b;
    border-radius: 12px;
    border: 1px solid #3d3d3d;
}

QFrame#Card:hover {
    border: 1px solid #60a5fa;
    background-color: #333333;
}

QFrame#Card QLabel {
    background-color: transparent;
}

QLabel#CardTitle {
    font-size: 22px;
    font-weight: bold;
    color: #f3f4f6;
    background-color: transparent;
}

QLabel#CardSubtitle {
    color: #9ca3af;
    font-size: 14px;
    background-color: transparent;
}

QPushButton#MenuBtn {
    background-color: #4b5563;
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
    border-radius: 6px;
    border: none;
    padding: 0px;
    margin: 0px;
}

QPushButton#MenuBtn:hover {
    background-color: #60a5fa;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #1f1f1f;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #4b5563;
    min-height: 20px;
    border-radius: 5px;
}

QMenu {
    background-color: #2b2b2b;
    border: 1px solid #3d3d3d;
    color: #ffffff;
    padding: 5px;
}

QMenu::item {
    padding: 8px 25px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3b82f6; /* Highlight color */
    color: white;
}

QRadioButton {
    color: #ffffff;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 8px;
    border: 2px solid #60a5fa;
    background: transparent;
}

QRadioButton::indicator:checked {
    background: #60a5fa;
    border: 2px solid #60a5fa;
}

QRadioButton::indicator:unchecked:hover {
    border: 2px solid #ffffff;
}
"""
