import os
import subprocess
import shutil
from typing import Optional

class KodiInstaller:
    @staticmethod
    def install(installer_path: str, target_dir: str) -> tuple[bool, str]:
        """
        Installs Kodi silently to target_dir using the NSIS installer.
        Returns (success, message)
        """
        if not os.path.exists(installer_path):
            return False, f"Installer not found: {installer_path}"
        
        target_dir = os.path.abspath(target_dir)
        
        # NSIS Silent install command
        cmd = f'"{installer_path}" /S /D={target_dir}'
        
        print(f"Running installer: {cmd}")
        
        try:
            # Use shell=True to ensure command parsing works as expected for batch-like strings
            # and to potentially help with permission elevation prompts if they weren't silent
            # (though /S inhibits them).
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Double check if target exists, sometimes NSIS fails silently
                if os.path.exists(target_dir):
                     return True, "Success"
                else:
                     return False, "Installer finished with code 0 but directory not found (Permission issue?)"
            else:
                msg = f"Installer failed with code {result.returncode}.\nStderr: {result.stderr}\nStdout: {result.stdout}"
                print(msg)
                return False, msg
                
                
        except Exception as e:
            if "740" in str(e):
               return False, "Esta operación requiere permisos de Administrador (WinError 740).\nPor favor ejecuta Kodi Manager como Administrador."
            return False, str(e)

    @staticmethod
    def create_portable_marker(target_dir: str):
        """
        Creates the portable_data folder to ensure portable mode.
        Wait, user asked for -p flag in shortcut.
        However, creating this folder enforces it regardless of shortcut.
        We will leave this as an optional helper or for 'ensure portable' logic.
        """
        data_path = os.path.join(target_dir, "portable_data")
        if not os.path.exists(data_path):
            os.makedirs(data_path)
