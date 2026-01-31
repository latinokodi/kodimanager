import os
import sys
import threading
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QProgressBar, 
                            QFileDialog, QMessageBox, QRadioButton, QButtonGroup, 
                            QWidget, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QPixmap
import webbrowser

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
            # Determine app root directory (works for both script and frozen exe)
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                # Up 3 levels from gui/dialogs.py -> src/kodimanager/gui -> src/kodimanager -> src -> root
                # actually just use os.getcwd() if running from source usually works, but safer relative to key file
                # If running from launcher.py, CWD is usually project root.
                app_dir = os.getcwd()

            installers_dir = os.path.join(app_dir, 'Kodi_Installers')
            if not os.path.exists(installers_dir):
                os.makedirs(installers_dir)
            
            installer_path = os.path.join(installers_dir, self.version_data['filename'])
            
            def dl_progress(curr, total):
                if total:
                    self.progress.emit("Descargando...", (curr / total) * 0.5)
            
            if os.path.exists(installer_path):
                 self.progress.emit("Instalador encontrado. Verificando...", 0.1)
                 # fast forward
                 self.progress.emit("Preparando instalación...", 0.5)
            else:
                self.progress.emit("Iniciando descarga...", 0.1)
                self.downloader.download_file(self.version_data['url'], installer_path, progress_callback=dl_progress)
            
            self.progress.emit("Instalando...", 0.6)
            final_path = os.path.join(self.target_path, self.name)
            if not os.path.exists(final_path): os.makedirs(final_path)
            
            success, msg = KodiInstaller.install(installer_path, final_path)
            
            if success:
                self.progress.emit("Finalizando...", 0.9)
                # We KEEP the installer now
                # if os.path.exists(installer_path): os.remove(installer_path)
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
        self.setStyleSheet("background-color: #111827; color: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main Card Frame
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 12px;
                border: 1px solid #374151;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Header
        header = QLabel("Nueva Instalación")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa;")
        card_layout.addWidget(header)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        sep1.setStyleSheet("background-color: #4b5563; max-height: 1px;")
        card_layout.addWidget(sep1)
        
        # Version Selection
        lbl_ver = QLabel("Versión de Kodi:")
        lbl_ver.setStyleSheet("color: #9ca3af; font-size: 14px;")
        card_layout.addWidget(lbl_ver)
        
        self.lbl_version_display = QLabel("Cargando...")
        self.lbl_version_display.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        card_layout.addWidget(self.lbl_version_display)
        
        # Name input
        lbl_name = QLabel("Nombre de la Instancia:")
        lbl_name.setStyleSheet("color: #9ca3af; font-size: 14px;")
        card_layout.addWidget(lbl_name)
        
        self.le_name = QLineEdit("Kodi Portable")
        self.le_name.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
            }
        """)
        card_layout.addWidget(self.le_name)
        
        # Path input
        lbl_path = QLabel("Ruta de Instalación:")
        lbl_path.setStyleSheet("color: #9ca3af; font-size: 14px;")
        card_layout.addWidget(lbl_path)
        
        path_layout = QHBoxLayout()
        self.le_path = QLineEdit(os.path.join(os.getcwd(), "Instances"))
        self.le_path.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
            }
        """)
        
        self.btn_browse = QPushButton("Explorar...")
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6b7280;
            }
        """)
        self.btn_browse.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.le_path)
        path_layout.addWidget(self.btn_browse)
        card_layout.addLayout(path_layout)
        
        # Separator 2
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        sep2.setStyleSheet("background-color: #4b5563; max-height: 1px;")
        card_layout.addWidget(sep2)
        
        # Progress
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #f59e0b;") # Orange for status
        card_layout.addWidget(self.lbl_status)
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #374151;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 4px;
            }
        """)
        self.progress.setVisible(False)
        card_layout.addWidget(self.progress)
        
        layout.addWidget(card)
        
        # Buttons Setup outside/bottom
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9ca3af;
                font-weight: bold;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1f2937;
                color: white;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_install = QPushButton("Instalar")
        self.btn_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:disabled {
                background-color: #4b5563;
                color: #9ca3af;
            }
        """)
        self.btn_install.clicked.connect(self.start_install)
        # Disable install until version is loaded
        self.btn_install.setEnabled(False) 
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_install)
        
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

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de Kodi Manager")
        self.setMinimumWidth(500) # changed from FixedSize to prevent cropping
        # Allow height to grow as needed
        self.setStyleSheet("background-color: #111827; color: white;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("KODI Manager")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Versión 3.0 (PyQt6 Edition)")
        subtitle.setStyleSheet("color: gray;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        author = QLabel("Latinokodi 2026")
        author.setStyleSheet("color: #60a5fa; font-weight: bold;")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = os.path.join(os.path.dirname(__file__), "LKU-LOGO-Small.png")
        if os.path.exists(logo_path):
            logo_lbl = QLabel()
            pixmap = QPixmap(logo_path)
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
        schedule_text = (
            "<html><head/><body><p align='center'>"
            "<span style='font-size:14px; font-weight:600; color:#60a5fa;'>📅 Horario de Directos</span><br/>"
            "<span style='font-size:12px; color:#e5e7eb;'>Lunes, Miércoles, Viernes y Domingos</span></p>"
            "<p align='center' style='font-size:12px; color:#9ca3af;'>"
            "🇲🇽 7:00 PM | 🇨🇴 🇵🇪 8:00 PM | 🇻🇪 9:00 PM<br/>"
            "🇦🇷 🇨🇱 10:00 PM | 🇪🇸 2:00 AM"
            "</p></body></html>"
        )
        self.lbl_schedule = QLabel(schedule_text)
        self.lbl_schedule.setStyleSheet("background-color: #1f2937; padding: 10px; border-radius: 6px;")
        self.lbl_schedule.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_schedule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_schedule)
        
        layout.addSpacing(20)
        
        btn_twitch = QPushButton("Visitar Twitch")
        btn_twitch.setFixedWidth(200)
        btn_twitch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_twitch.setStyleSheet("background-color: #9146ff; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        btn_twitch.clicked.connect(lambda: webbrowser.open("https://www.twitch.tv/Latinokodi"))
        
        layout.addWidget(btn_twitch, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(15)
        
        btn_enter = QPushButton("Entrar en la app")
        btn_enter.setFixedWidth(200)
        btn_enter.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_enter.setStyleSheet("background-color: #10b981; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px;")
        btn_enter.clicked.connect(self.accept)
        
        layout.addWidget(btn_enter, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()

