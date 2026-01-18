import psutil
import os
import time

def kill_process_by_path(target_path: str) -> bool:
    """
    Terminates any process running from the given path (or subdirectories).
    Returns True if processes were killed or none were found, False if failed.
    """
    # Normalize path
    target_path = os.path.abspath(target_path).lower()
    
    killed_any = False
    
    try:
        for proc in psutil.process_iter(['pid', 'exe', 'name']):
            try:
                exe_path = proc.info.get('exe')
                if exe_path:
                    exe_path = os.path.abspath(exe_path).lower()
                    if exe_path.startswith(target_path):
                        print(f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) running from {exe_path}")
                        proc.kill()
                        killed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        if killed_any:
            # Wait a moment for OS to release locks
            time.sleep(1.0)
            
        return True
    except Exception as e:
        print(f"Error checking/killing processes: {e}")
        return False
