COLORS = {
    "background": "#0f172a", # Slate 900
    "surface": "#1e293b",     # Slate 800
    "surface_hover": "#334155", # Slate 700
    "primary": "#3b82f6",     # Blue 500
    "primary_hover": "#2563eb", # Blue 600
    "text": "#f1f5f9",        # Slate 100
    "text_muted": "#94a3b8",  # Slate 400
    "accent": "#06b6d4",      # Cyan 500
    "success": "#10b981",     # Emerald 500
    "danger": "#ef4444",      # Red 500
    "border": "#334155",      # Slate 700
}

GLASS_THEME = f"""
/* Global Reset */
QMainWindow, QDialog, QMessageBox {{
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}}

QMessageBox QPushButton {{
    background-color: {COLORS['surface_hover']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text']};
    min-width: 60px;
}}

QMessageBox QPushButton:hover {{
    background-color: {COLORS['primary']};
    color: white;
    border: 1px solid {COLORS['primary']};
}}

QLabel {{
    color: {COLORS['text']};
}}

/* Clean Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {COLORS['background']};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['surface_hover']};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_muted']};
}}

/* Cards - Modern Glass-like Surface */
QFrame#Card {{
    background-color: {COLORS['surface']}; 
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QFrame#Card:hover {{
    background-color: {COLORS['surface_hover']};
    border: 1px solid {COLORS['primary']};
}}

/* Typography */
QLabel#CardTitle {{
    color: {COLORS['text']};
    font-size: 16px;
    font-weight: 700;
}}
QLabel#CardSubtitle {{
    color: {COLORS['text_muted']};
    font-size: 13px;
}}

/* Buttons - Flat & Hero */
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    border: none;
}}
QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}
QPushButton:pressed {{
    background-color: #1d4ed8;
}}

/* Secondary / Ghost Buttons */
QPushButton#ActionBtn {{
    background-color: transparent;
    border: 1px solid {COLORS['border']};
    color: {COLORS['text']};
}}
QPushButton#ActionBtn:hover {{
    background-color: {COLORS['surface_hover']};
    border-color: {COLORS['text_muted']};
}}

/* Menu Button (Icon Only) */
QPushButton#MenuBtn {{
    background-color: transparent;
    color: {COLORS['text_muted']};
    font-size: 18px;
    font-weight: 900;
    border-radius: 4px;
    padding: 4px;
}}
QPushButton#MenuBtn:hover {{
    background-color: {COLORS['surface_hover']};
    color: {COLORS['text']};
}}

/* Ko-fi Support Button */
QPushButton#KofiBtn {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5E5B, stop:1 #FF8FA3);
    color: white;
    font-weight: bold;
    font-size: 14px;
    border-radius: 18px; /* Full Capsule */
    padding: 8px 24px;
    border: 1px solid #FF5E5B;
}
QPushButton#KofiBtn:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF413D, stop:1 #FF7A8F);
    border: 1px solid #FF413D;
}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['surface']};
    border-radius: 8px;
}}
QTabBar::tab {{
    background-color: {COLORS['background']};
    color: {COLORS['text_muted']};
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary']};
    font-weight: bold;
}}

/* Context Menu */
QMenu {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 4px;
    color: {COLORS['text']};
}}
QMenu::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background: {COLORS['border']};
    margin: 4px 0;
}}

/* Input Fields */
QLineEdit {{
    background-color: {COLORS['background']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text']};
}}
QLineEdit:focus {{
    border: 1px solid {COLORS['primary']};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    opacity: 230; 
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS['surface']};
    border-radius: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 4px;
}}
"""
