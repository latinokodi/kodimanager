import os
import win32com.client # type: ignore
from typing import Optional

class ShortcutManager:
    @staticmethod
    def create_shortcut(target_path: str, shortcut_path: str, arguments: str = "", work_dir: str = "", icon_path: str = ""):
        """
        Creates a Windows shortcut using WScript.Shell via COM.
        This avoids external heavy deps, utilizing standard Windows capabilities usable from Python 
        via pywin32 (which is standard) or ctypes.
        Since we might not want to depend on pywin32 if possible, we can use a VBS script wrapper or ctypes.
        However, pywin32 is robust. We'll try to use it if available, else fallback or just require it.
        Given "pywinshortcut" mentioned in plan, but let's stick to standard pywin32 (pip install pywin32).
        """
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = work_dir or os.path.dirname(target_path)
            if icon_path:
                shortcut.IconLocation = icon_path
            shortcut.WindowStyle = 1 # Normal window
            shortcut.Save()
            return True
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False

    @staticmethod
    def delete_shortcut(shortcut_path: str) -> bool:
        """
        Deletes a shortcut if it exists.
        """
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting shortcut: {e}")
            return False
