import os
import threading
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QProgressBar, 
                            QFileDialog, QMessageBox, QRadioButton, QButtonGroup, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt, QThread

from ..core.downloader import KodiDownloader
from ..core.installer import KodiInstaller
from ..utils.shortcuts import ShortcutManager

class InstallThread(QThread):
    progress = pyqtSignal(str, float) # status, percentage (0-1)
    finished_signal = pyqtSignal(bool, str) # success, message
    
    def __init__(self, version_data, name, target_path):
        super().__init__()
        self.version_data = version_data
        self.name = name
        self.target_path = target_path
        self.downloader = KodiDownloader()
        
    def run(self):
        try:
            temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'KodiManager_DL')
            if not os.path.exists(temp_dir): os.makedirs(temp_dir)
            
            installer_path = os.path.join(temp_dir, self.version_data['filename'])
            
            def dl_progress(curr, total):
                if total:
                    self.progress.emit("Descargando...", (curr / total) * 0.5)
            
            self.progress.emit("Iniciando descarga...", 0.1)
            self.downloader.download_file(self.version_data['url'], installer_path, progress_callback=dl_progress)
            
            self.progress.emit("Instalando...", 0.6)
            final_path = os.path.join(self.target_path, self.name)
            if not os.path.exists(final_path): os.makedirs(final_path)
            
            success, msg = KodiInstaller.install(installer_path, final_path)
            
            if success:
                self.progress.emit("Limpiando...", 0.9)
                if os.path.exists(installer_path): os.remove(installer_path)
                self.finished_signal.emit(True, final_path)
            else:
                self.finished_signal.emit(False, msg)
                
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class InstallDialog(QDialog):
    instance_created = pyqtSignal(str, str, str) # name, path, version

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Instalación de Kodi")
        self.resize(500, 300)
        self.setup_ui()
        self.downloader = KodiDownloader()
        self.load_versions()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Version Selection
        layout.addWidget(QLabel("Versión de Kodi:"))
        self.lbl_version_display = QLabel("Cargando...")
        self.lbl_version_display.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_version_display)
        
        # Name
        layout.addWidget(QLabel("Nombre de la Instancia:"))
        self.le_name = QLineEdit("Kodi Portable")
        layout.addWidget(self.le_name)
        
        # Path
        layout.addWidget(QLabel("Ruta de Instalación:"))
        path_layout = QHBoxLayout()
        self.le_path = QLineEdit(os.path.join(os.getcwd(), "Instances"))
        self.btn_browse = QPushButton("Explorar...")
        self.btn_browse.clicked.connect(self.browse_path)
        path_layout.addWidget(self.le_path)
        path_layout.addWidget(self.btn_browse)
        layout.addLayout(path_layout)
        
        # Progress
        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_install = QPushButton("Instalar")
        self.btn_install.clicked.connect(self.start_install)
        # Disable install until version is loaded
        self.btn_install.setEnabled(False) 
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_install)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
    def load_versions(self):
        # Run in thread or just simplified here (could block briefly)
        try:
             self.selected_version = None
             # Just a quick blocking call for now, can optimize later if needed
             self.versions = self.downloader.get_available_versions()
             
             if self.versions:
                 v = self.versions[0] # Take the first (and only) one
                 tag = v.get('tag', '')
                 display = f"{v['version']}"
                 if tag:
                     display += f" {tag}"
                 display += f" - {v['codename']}"
                 
                 self.lbl_version_display.setText(display)
                 self.selected_version = v
                 self.btn_install.setEnabled(True)
             else:
                 self.lbl_version_display.setText("No se encontraron versiones")
                 
        except:
            self.lbl_status.setText("Error cargando versiones")
            self.lbl_version_display.setText("Error")
            
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Destino")
        if path:
            self.le_path.setText(path)
            
    def start_install(self):
        if not self.selected_version: return
        
        version_data = self.selected_version
        name = self.le_name.text().strip()
        path = self.le_path.text().strip()
        
        if not name or not path:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return
            
        self.btn_install.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = InstallThread(version_data, name, path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished_signal.connect(self.install_finished)
        self.worker.start()
        
    def update_progress(self, status, val):
        self.lbl_status.setText(status)
        self.progress.setValue(int(val * 100))
        
    def install_finished(self, success, result):
        self.btn_install.setEnabled(True)
        if success:
            self.lbl_status.setText("Completado!")
            self.progress.setValue(100)
            
            # Emit signal
            version = self.selected_version['version']
            self.instance_created.emit(self.le_name.text(), result, version)
            
            QMessageBox.information(self, "Éxito", "Instalación completada correctamente.")
            self.accept()
        else:
            self.lbl_status.setText(f"Error: {result}")
            QMessageBox.critical(self, "Error", f"Fallo la instalación: {result}")

class ShortcutDialog(QDialog):
    def __init__(self, instance_name, executable_path, instance_path, is_portable, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Acceso Directo")
        self.resize(400, 150)
        self.instance_name = instance_name
        self.executable_path = executable_path
        self.instance_path = instance_path
        self.is_portable = is_portable
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("¿Dónde deseas crear el acceso directo?"))
        
        self.btn_desktop = QRadioButton("Escritorio")
        self.btn_desktop.setChecked(True)
        self.btn_folder = QRadioButton("En la carpeta de la instancia")
        
        layout.addWidget(self.btn_desktop)
        layout.addWidget(self.btn_folder)
        
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Crear")
        ok_btn.clicked.connect(self.create_shortcut)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)
        
    def create_shortcut(self):
        try:
            target_dir = os.path.join(os.path.expanduser("~"), "Desktop") if self.btn_desktop.isChecked() else self.instance_path
            link_name = f"Kodi - {self.instance_name}.lnk"
            link_path = os.path.join(target_dir, link_name)
            
            args = "-p" if self.is_portable else ""
            ShortcutManager.create_shortcut(self.executable_path, link_path, args, self.instance_path)
            
            QMessageBox.information(self, "Éxito", f"Acceso directo creado en:\n{link_path}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
