import ctypes
import sys
import os

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def restart_as_admin():
    """
    Restarts the current script with admin privileges.
    """
    # Get the executable and arguments
    # If running from python script: python.exe script.py
    # If frozen (exe): executable.exe
    
    # We can use sys.executable for both usually, but let's be careful with arguments.
    
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        else:
            # Running as python script
            # sys.executable is the python interpreter
            # logic: runas python.exe "script.py params"
            
            # Use sys.argv directly to reconstruct command
            # But ShellExecute needs clean separation of file and params
            
            # File: python.exe
            # Params: "path/to/script.py" arg1 arg2
            
            # Important: Wrap script path in quotes in case of spaces
            cmd_params = f'"{script}" {params}'
            
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd_params, None, 1)
            
        # Exit current process
        sys.exit(0)
    except Exception as e:
        print(f"Error restarting as admin: {e}")
        # If user cancels UAC, it raises an error usually or returns <=32
        pass
