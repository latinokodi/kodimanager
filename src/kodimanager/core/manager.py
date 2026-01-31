import json
import os
import shutil
import uuid
import time
from typing import List, Optional
from .models import KodiInstance
from ..utils.shortcuts import ShortcutManager

class InstanceManager:
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = config_dir
        else:
            # Default to APPDATA
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            self.config_dir = os.path.join(appdata, 'KodiManager')
        
        self.instances_file = os.path.join(self.config_dir, 'instances.json')
        self._ensure_config_dir()
        self.instances: List[KodiInstance] = self._load_instances()

    def _ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def _load_instances(self) -> List[KodiInstance]:
        if not os.path.exists(self.instances_file):
            return []
        try:
            with open(self.instances_file, 'r') as f:
                data = json.load(f)
                return [KodiInstance.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def _save_instances(self):
        with open(self.instances_file, 'w') as f:
            json.dump([i.to_dict() for i in self.instances], f, indent=4)

    def get_all(self) -> List[KodiInstance]:
        return self.instances

    def get_by_id(self, instance_id: str) -> Optional[KodiInstance]:
        for i in self.instances:
            if i.id == instance_id:
                return i
        return None

    def register_instance(self, name: str, path: str, version: str) -> KodiInstance:
        instance = KodiInstance(
            id=str(uuid.uuid4()),
            name=name,
            path=path,
            version=version,
            created_at=time.time()
        )
        self.instances.append(instance)
        self._save_instances()
        return instance

    def _kill_process_in_folder(self, path: str):
        try:
            from ..utils.process import kill_process_by_path
            kill_process_by_path(path)
        except ImportError:
            pass

    def remove_instance(self, instance_id: str, delete_files: bool = False) -> tuple[bool, str]:
        instance = self.get_by_id(instance_id)
        if not instance:
            return False, "Instancia no encontrada"
        
        warning_msg = ""
        
        # 1. Delete files first if requested
        if delete_files and os.path.exists(instance.path):
            # First, kill any running processes in this folder
            self._kill_process_in_folder(instance.path)
            
            max_retries = 3
            for attempt in range(max_retries):
                # Robust python deletion
                try:
                    def on_rm_error(func, path, exc_info):
                        os.chmod(path, 0o777)
                        try:
                            func(path)
                        except Exception:
                            pass

                    shutil.rmtree(instance.path, onerror=on_rm_error)
                except Exception:
                    pass
                
                if not os.path.exists(instance.path):
                    break
                    
                time.sleep(0.5) # Wait before retry
            
            # Critical Check: If folder still exists, we abort the removal from DB
            if os.path.exists(instance.path):
                 return False, f"No se pudo eliminar la carpeta:\n{instance.path}\n\nVerifique que KODI no esté ejecutándose y que no tenga archivos abiertos."
        
        # 2. Delete shortcut if exists (Best effort)
        try:
            shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", f"Kodi - {instance.name}.lnk")
            ShortcutManager.delete_shortcut(shortcut_path)
        except Exception:
            pass # Ignore errors here deletion

        # 3. Remove from registry
        self.instances = [i for i in self.instances if i.id != instance_id]
        self._save_instances()

        return True, warning_msg

    def clean_sweep(self, instance_id: str):
        """Removes the portable_data directory to reset the instance."""
        instance = self.get_by_id(instance_id)
        if not instance:
            raise ValueError("Instance not found")
        
        portable_data = instance.portable_data_path
        if os.path.exists(portable_data):
            shutil.rmtree(portable_data)

    def update_instance_version_record(self, instance_id: str, new_version: str):
        instance = self.get_by_id(instance_id)
        if instance:
            instance.version = new_version
            self._save_instances()

    def detect_installed_instances(self) -> List[KodiInstance]:
        """Scans common paths for Kodi installations and registers them if not already detected."""
        detected = []
        
        # Common paths to check
        potential_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Kodi'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Kodi'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Kodi'),
            # Could add more custom paths if needed
        ]
        
        found_paths = []
        for p in potential_paths:
            if os.path.exists(os.path.join(p, 'kodi.exe')):
                found_paths.append(p)

        # Check against existing instances to avoid duplicates
        existing_paths = [i.path.lower() for i in self.instances]
        
        for p in found_paths:
            if p.lower() in existing_paths:
                continue
                
            # It's new!
            # Try to determine version? For now, we might label it "Detected"
            # Or use a utility to existing executable version info (requires more libs usually)
            # We'll just register it.
            
            # Simple version check using file modification or just "Unknown"
            # In a real scenario, we could parse 'kodi.exe --version' output
            
            version = "Detected"
            
            # Try getting version from kodi.exe
            try:
                # This could be slow, maybe do it async or just leave as "Detected"
                pass
            except:
                pass

            inst = self.register_instance(
                name=f"Kodi Detected ({os.path.basename(p)})",
                path=p,
                version=version
            )
            detected.append(inst)
            
        return detected

