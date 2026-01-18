import json
import os
import threading
import webbrowser
from typing import Dict, Any

from .core.manager import InstanceManager
from .core.downloader import KodiDownloader
from .core.installer import KodiInstaller
from .utils.shortcuts import ShortcutManager

class KodiManagerAPI:
    def __init__(self):
        self.manager = InstanceManager()
        self.downloader = KodiDownloader()
        self._window = None

    def set_window(self, window):
        self._window = window

    def get_instances(self) -> str:
        """Returns JSON string of all instances."""
        instances = self.manager.get_all()
        return json.dumps([i.to_dict() for i in instances])

    def detect_instances(self) -> str:
        """Triggers detection and returns new list."""
        self.manager.detect_installed_instances()
        return self.get_instances()

    def launch_instance(self, instance_id: str) -> Dict[str, Any]:
        instance = self.manager.get_by_id(instance_id)
        if not instance:
            return {"success": False, "error": "Instance not found"}
        
        exe_path = instance.executable_path
        if not os.path.exists(exe_path):
            return {"success": False, "error": f"Executable not found at {exe_path}"}
            
        try:
            import subprocess
            # Determine flags
            args = [exe_path]
            # Simple heuristic for portable mode
            if os.path.exists(instance.portable_data_path) or "Detected" not in instance.version:
                 args.append("-p")
                 
            subprocess.Popen(args, cwd=instance.path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_versions(self) -> str:
        """Returns JSON list of versions."""
        try:
            versions = self.downloader.get_available_versions()
            return json.dumps(versions)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def install_instance(self, version_idx: int, name: str, path: str) -> Dict[str, Any]:
        """
        Installs an instance. This is a blocking call if run directly.
        In pywebview, we might want to run this in a thread and send events back.
        """
        # We need to fetch versions again or cache them.
        # For simplicity, we assume frontend sends the version object or we refetch.
        # Better: Frontend sends the version data object directly? 
        # API params limited to primitives usually.
        # Let's say frontend calls get_available_versions first, then passes the version object.
        pass 
        # Actually simplest is: Frontend passes version_url and filename.
    
    def install_instance_async(self, version_url: str, filename: str, version_tag: str, name: str, target_path: str):
        """Starts installation in a thread and reports progress via window.evaluate_js"""
        thread = threading.Thread(target=self._install_worker, args=(version_url, filename, version_tag, name, target_path))
        thread.start()
        return {"success": True, "message": "Installation started"}

    def _install_worker(self, url, filename, version, name, target_path):
        try:
            temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'KodiManager_DL')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            installer_path = os.path.join(temp_dir, filename)
            
            def progress(current, total):
                if total:
                    p = int((current / total) * 50)
                    if self._window:
                        self._window.evaluate_js(f'window.updateInstallProgress({p})')

            # Download
            if self._window:
                 self._window.evaluate_js('window.updateInstallStatus("Downloading...")')
                 
            self.downloader.download_file(url, installer_path, progress_callback=progress)
            
            if self._window:
                 self._window.evaluate_js(f'window.updateInstallProgress(50)')
                 self._window.evaluate_js('window.updateInstallStatus("Installing...")')

            # Install
            final_path = os.path.join(target_path, name)
            if not os.path.exists(final_path):
                os.makedirs(final_path)

            success, msg = KodiInstaller.install(installer_path, final_path)
            
            if success:
                if self._window:
                    self._window.evaluate_js(f'window.updateInstallProgress(90)')
                    self._window.evaluate_js('window.updateInstallStatus("Cleaning up...")')

                if os.path.exists(installer_path):
                    os.remove(installer_path)

                # Register
                inst = self.manager.register_instance(name, final_path, version)

                if self._window:
                    self._window.evaluate_js(f'window.updateInstallProgress(100)')
                    # Pass instance ID (quote it as string)
                    self._window.evaluate_js(f'window.onInstallComplete(true, "", "{inst.id}")')
            else:
                 if self._window:
                    self._window.evaluate_js(f'window.onInstallComplete(false, "{msg}", null)')

        except Exception as e:
            if self._window:
                 self._window.evaluate_js(f'window.onInstallComplete(false, "{str(e)}", null)')


    def select_folder(self) -> str:
        try:
            import subprocess
            cmd = [
                "powershell", 
                "-NoProfile", 
                "-Command", 
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$d.ShowNewFolderButton = $true; "
                "if ($d.ShowDialog() -eq 'OK') { Write-Host $d.SelectedPath }"
            ]
            
            # Use startupinfo to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
            if result.returncode == 0:
                return result.stdout.strip()
            return ""
        except Exception as e:
            print(f"Error using PS dialog: {e}")
            return ""

    def delete_instance(self, instance_id: str) -> Dict[str, Any]:
        success, msg = self.manager.remove_instance(instance_id, delete_files=True)
        return {"success": success, "message": msg}

    def clean_instance(self, instance_id: str) -> bool:
        try:
            self.manager.clean_sweep(instance_id)
            return True
        except:
            return False

    def create_shortcut(self, instance_id: str, on_desktop: bool = True) -> bool:
        instance = self.manager.get_by_id(instance_id)
        if not instance:
            return False
            
        if on_desktop:
            target_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            target_dir = instance.path

        fname = f"Kodi - {instance.name}.lnk"
        
        shortcut_path = os.path.join(target_dir, fname)
        
        args = ""
        if os.path.exists(instance.portable_data_path) or "Detected" not in instance.version:
                args = "-p"

        return ShortcutManager.create_shortcut(
            target_path=instance.executable_path,
            shortcut_path=shortcut_path,
            arguments=args,
            work_dir=instance.path
        )

    def open_url(self, url: str):
        webbrowser.open(url)
