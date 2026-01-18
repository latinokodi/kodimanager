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
from .dialogs import InstallDialog, ShortcutDialog, AboutDialog
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
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        self.setup_manager_view()
        
        # Show About Dialog on startup
        self.show_about_dialog()

    def setup_manager_view(self):
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
        
        # Admin Restart Button
        self.btn_admin = QPushButton("Reiniciar (Admin)")
        self.btn_admin.setObjectName("ActionBtn")
        self.btn_admin.setStyleSheet("background-color: #f59e0b; color: white;") # Orange for attention
        self.btn_admin.clicked.connect(lambda: admin.restart_as_admin())
        
        # About Button
        self.btn_about = QPushButton("Acerca de")
        self.btn_about.setObjectName("ActionBtn")
        self.btn_about.clicked.connect(self.show_about_dialog)
        
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
            
        toolbar.addWidget(self.btn_about)
            
        self.main_layout.addLayout(toolbar)
        
        # Scroll Area for Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

    def show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec()

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
