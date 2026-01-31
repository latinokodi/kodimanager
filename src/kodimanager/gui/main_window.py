import os
import sys
import webbrowser
import math
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QScrollArea, QPushButton, QLabel, QFrame,
                            QTabWidget, QMessageBox, QMenu, QApplication, QGridLayout, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QPixmap

from ..core.manager import InstanceManager
from ..core.models import KodiInstance
from ..utils import admin
from .dialogs import InstallDialog, ShortcutDialog, AboutDialog
from .styles import GLASS_THEME
from .worker import Worker

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Header: Name + Menu
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        name_label = QLabel(self.instance.name)
        name_label.setObjectName("CardTitle")
        name_label.setWordWrap(True)
        
        btn_menu = QPushButton("⋮") # Vertical ellipsis is cleaner
        btn_menu.setFixedSize(30, 30)
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.setObjectName("MenuBtn")
        btn_menu.clicked.connect(self.on_menu_click)
        
        header_layout.addWidget(name_label, 1) # Expand name
        header_layout.addWidget(btn_menu)
        layout.addLayout(header_layout)
        
        # Divider Line (Optional, maybe just spacing)
        # line = QFrame()
        # line.setFrameShape(QFrame.Shape.HLine)
        # line.setStyleSheet("background-color: #27272a; height: 1px; border: none;")
        # layout.addWidget(line)

        # Details Information
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        # Version Badge / Text
        ver_label = QLabel(f"Versión: {self.instance.version}")
        ver_label.setObjectName("CardSubtitle")
        ver_label.setStyleSheet("color: #60a5fa; font-weight: 600;") # Blue accent text
        details_layout.addWidget(ver_label)
        
        # Path
        path_label = QLabel(self.instance.path)
        path_label.setObjectName("CardSubtitle")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("color: #71717a; font-size: 12px;") # Muted text
        details_layout.addWidget(path_label)
        
        layout.addLayout(details_layout)
        
        layout.addStretch()
        
        # Launch Button
        btn_launch = QPushButton("INICIAR")
        btn_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_launch.setFixedHeight(40) # Taller button
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
        
        # Show About Dialog on startup if not suppressed
        if "--no-splash" not in sys.argv:
            self.show_about_dialog()

    def setup_manager_view(self):
        toolbar = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #f3f4f6; margin-bottom: 10px;")
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
        
        # About Button
        self.btn_about = QPushButton("Acerca de")
        self.btn_about.setObjectName("ActionBtn")
        self.btn_about.clicked.connect(self.show_about_dialog)

        # Ko-fi Button
        self.btn_kofi = QPushButton("☕ Cómprame un café")
        self.btn_kofi.setObjectName("KofiBtn")
        self.btn_kofi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_kofi.clicked.connect(lambda: webbrowser.open("https://ko-fi.com/latinokodi"))
        
        toolbar.addWidget(self.btn_kofi)
        toolbar.addSpacing(10)

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
        
        # Progress Bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { height: 4px; background: #27272a; border: none; } QProgressBar::chunk { background: #2563eb; }")
        self.main_layout.addWidget(self.progress_bar)
        
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
        self.progress_bar.setVisible(True)
        self.btn_detect.setEnabled(False)
        self.worker = Worker(self.manager.detect_installed_instances)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.start()

    def on_detection_finished(self, detected):
        self.progress_bar.setVisible(False)
        self.btn_detect.setEnabled(True)
        if isinstance(detected, Exception):
            QMessageBox.critical(self, "Error", f"Error al detectar: {str(detected)}")
            return
            
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
        menu.setStyleSheet(GLASS_THEME) # Apply theme to menu too

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
    app.setStyleSheet(GLASS_THEME)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
