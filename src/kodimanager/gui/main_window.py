import os
import sys
import webbrowser
import math
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QScrollArea, QPushButton, QLabel, QFrame,
                            QTabWidget, QMessageBox, QMenu, QApplication, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QPixmap

from ..core.manager import InstanceManager
from ..core.models import KodiInstance
from ..utils import admin
from .dialogs import InstallDialog, ShortcutDialog
from .styles import DARK_THEME

class InstanceCard(QFrame):
    launch_clicked = pyqtSignal(str) # instance_id
    manage_clicked = pyqtSignal(str, object) # instance_id, position (QPoint)

    def __init__(self, instance: KodiInstance):
        super().__init__()
        self.instance = instance
        self.setObjectName("Card")
        self.setFixedSize(280, 180)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header: Name + Menu
        header_layout = QHBoxLayout()
        name_label = QLabel(self.instance.name)
        name_label.setObjectName("CardTitle")
        name_label.setWordWrap(True)
        
        btn_menu = QPushButton("...")
        btn_menu.setFixedSize(45, 35)
        btn_menu.setContentsMargins(0, 0, 0, 0)
        btn_menu.setObjectName("MenuBtn")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self.on_menu_click)
        
        header_layout.addWidget(name_label, 1) # Expand name
        header_layout.addWidget(btn_menu)
        layout.addLayout(header_layout)
        
        # Details
        ver_label = QLabel(f"Versión: {self.instance.version}")
        ver_label.setObjectName("CardSubtitle")
        layout.addWidget(ver_label)
        
        path_label = QLabel(self.instance.path)
        path_label.setObjectName("CardSubtitle")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("font-size: 12px; color: #6b7280;") # Extra styling
        layout.addWidget(path_label)
        
        layout.addStretch()
        
        # Launch Button
        btn_launch = QPushButton("INICIAR")
        btn_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_launch.setFixedHeight(35)
        btn_launch.clicked.connect(lambda: self.launch_clicked.emit(self.instance.id))
        layout.addWidget(btn_launch)

    def on_menu_click(self):
        self.manage_clicked.emit(self.instance.id, self.mapToGlobal(self.rect().topRight()))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KODI Manager")
        self.resize(1000, 700)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.manager = InstanceManager()
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab 1: Manager
        self.tab_manager = QWidget()
        self.setup_manager_tab()
        self.tabs.addTab(self.tab_manager, "Mis Instalaciones")
        
        # Tab 2: About
        self.tab_about = QWidget()
        self.setup_about_tab()
        self.tabs.addTab(self.tab_about, "Acerca de")

    def setup_manager_tab(self):
        layout = QVBoxLayout(self.tab_manager)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header / Toolbar
        toolbar = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #60a5fa;")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        self.btn_detect = QPushButton("Detectar")
        self.btn_detect.setIcon(QIcon.fromTheme("system-search")) # System icon fallback
        self.btn_detect.setObjectName("ActionBtn")
        self.btn_detect.clicked.connect(self.detect_instances)
        
        self.btn_add = QPushButton("Nueva Instalación")
        self.btn_add.clicked.connect(self.show_install_dialog)
        
        self.btn_refresh = QPushButton("Refrescar")
        self.btn_refresh.setObjectName("ActionBtn")
        self.btn_refresh.clicked.connect(self.refresh_list)
        
        # Admin Restart Button
        self.btn_admin = QPushButton("Reiniciar (Admin)")
        self.btn_admin.setObjectName("ActionBtn")
        self.btn_admin.setStyleSheet("background-color: #f59e0b; color: white;") # Orange for attention
        self.btn_admin.clicked.connect(lambda: admin.restart_as_admin())
        
        toolbar.addWidget(self.btn_detect)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_add)
        
        if not admin.is_admin():
            toolbar.addWidget(self.btn_admin)
        else:
            # Show small indicator or just hide
            lbl_admin = QLabel("Modo Admin")
            lbl_admin.setStyleSheet("color: #10b981; font-weight: bold; border: 1px solid #10b981; padding: 4px; border-radius: 4px;")
            toolbar.addWidget(lbl_admin)
            
        layout.addLayout(toolbar)
        
        # Scroll Area for Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

    def setup_about_tab(self):
        layout = QVBoxLayout(self.tab_about)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("KODI Manager")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Versión 2.0 (PyQt6 Edition)")
        subtitle.setStyleSheet("color: gray;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        author = QLabel("Latinokodi 2026")
        author.setStyleSheet("color: #60a5fa; font-weight: bold;")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = os.path.join(os.path.dirname(__file__), "LKU-LOGO-Small.png")
        if os.path.exists(logo_path):
            logo_lbl = QLabel()
            pixmap = QPixmap(logo_path)
            # Scale if too big (e.g. max 300 width)
            pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_lbl)
        
        layout.addSpacing(20)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(author)
        
        layout.addSpacing(20)
        
        invite_msg = QLabel("Únete a nuestro canal de Twitch para obtener soporte y tutoriales en vivo.")
        invite_msg.setStyleSheet("color: #60a5fa; font-size: 16px;")
        invite_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        invite_msg.setWordWrap(True)
        layout.addWidget(invite_msg)

        layout.addSpacing(10)
        
        # Schedule
        self.lbl_schedule = QLabel("📅 Horario de Directos:\nLunes a Viernes: 9:00 PM (Hora Colombia)\nFines de Semana: Anunciado en Discord")
        self.lbl_schedule.setStyleSheet("color: #d1d5db; font-size: 14px; background-color: #1f2937; padding: 10px; border-radius: 6px;")
        self.lbl_schedule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_schedule)
        
        layout.addSpacing(10)
        
        btn_twitch = QPushButton("Visitar Twitch")
        btn_twitch.setFixedWidth(200)
        btn_twitch.clicked.connect(lambda: webbrowser.open("https://www.twitch.tv/Latinokodi"))
        layout.addWidget(btn_twitch, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()

    def refresh_list(self):
        # Clear grid
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
            
        instances = self.manager.get_all()
        
        if not instances:
            # Show empty state
            empty_lbl = QLabel("No hay instancias instaladas.\nHaz clic en 'Nueva Instalación' para comenzar.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #6b7280; font-size: 18px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
        else:
            # Grid logic: 3 columns max? Or dynamic based on width? 
            # Simple grid: 3 columns
            cols = 3
            for idx, inst in enumerate(instances):
                row = idx // cols
                col = idx % cols
                card = InstanceCard(inst)
                card.launch_clicked.connect(self.launch_instance_by_id)
                card.manage_clicked.connect(self.show_context_menu)
                self.grid_layout.addWidget(card, row, col)

    def show_install_dialog(self):
        dlg = InstallDialog(self)
        dlg.instance_created.connect(self.on_instance_created)
        dlg.exec()

    def on_instance_created(self, name, path, version):
        self.manager.register_instance(name, path, version)
        self.refresh_list()
        
        instances = self.manager.get_all()
        new_inst = next((i for i in instances if i.path == path), None)
        
        if new_inst:
             self.prompt_shortcut(new_inst)

    def detect_instances(self):
        detected = self.manager.detect_installed_instances()
        self.refresh_list()
        if detected:
             QMessageBox.information(self, "Detectar", f"Se encontraron {len(detected)} instalaciones nuevas.")
        else:
             QMessageBox.information(self, "Detectar", "No se encontraron nuevas instalaciones.")

    def launch_instance_by_id(self, inst_id):
        inst = self.manager.get_by_id(inst_id)
        if inst:
            exe = inst.executable_path
            if os.path.exists(exe):
                import subprocess
                args = [exe]
                if os.path.exists(inst.portable_data_path) or "Detected" not in inst.version:
                    args.append("-p")
                
                subprocess.Popen(args, cwd=inst.path)
            else:
                QMessageBox.critical(self, "Error", "No se encuentra el ejecutable kodi.exe")

    def show_context_menu(self, inst_id, pos):
        inst = self.manager.get_by_id(inst_id)
        if not inst: return

        menu = QMenu(self)
        menu.setStyleSheet(DARK_THEME) # Apply theme to menu too

        action_launch = QAction("Iniciar", self)
        action_launch.triggered.connect(lambda: self.launch_instance_by_id(inst_id))
        
        action_shortcut = QAction("Crear Acceso Directo", self)
        action_shortcut.triggered.connect(lambda: self.prompt_shortcut(inst))
        
        action_clean = QAction("Limpiar Datos (Reseteo)", self)
        action_clean.triggered.connect(lambda: self.clean_instance(inst))
        
        action_delete = QAction("Eliminar Instancia", self)
        action_delete.triggered.connect(lambda: self.delete_instance(inst))
        
        menu.addAction(action_launch)
        menu.addSeparator()
        menu.addAction(action_shortcut)
        menu.addAction(action_clean)
        menu.addSeparator()
        menu.addAction(action_delete)
        
        # Adjust pos to be slightly offset from button
        # pos passed is global top right of button
        menu.exec(pos)

    def prompt_shortcut(self, inst):
        is_portable = (os.path.exists(inst.portable_data_path) or "Detected" not in inst.version)
        dlg = ShortcutDialog(inst.name, inst.executable_path, inst.path, is_portable, self)
        dlg.exec()

    def clean_instance(self, inst):
        reply = QMessageBox.question(self, "Confirmar Limpieza", 
                                   f"¿Estás seguro de que deseas limpiar los datos de '{inst.name}'?\nEsto borrará todos los addons y configuraciones.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.clean_sweep(inst.id)
                QMessageBox.information(self, "Éxito", "Instancia limpiada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al limpiar: {str(e)}")

    def delete_instance(self, inst):
        reply = QMessageBox.question(self, "Confirmar Eliminación", 
                                   f"¿Estás seguro de que deseas eliminar '{inst.name}'?\nEsto borrará los archivos permanentemente.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.manager.remove_instance(inst.id, delete_files=True)
            if success:
                self.refresh_list()
                if msg:
                     QMessageBox.warning(self, "Aviso", msg)
                else:
                     QMessageBox.information(self, "Éxito", "Instancia eliminada.")
            else:
                QMessageBox.critical(self, "Error", f"Error al eliminar la instancia: {msg}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Best base for custom styling
    app.setStyleSheet(DARK_THEME)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
