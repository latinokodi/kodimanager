import sys
import os

# Ensure we can find the src package
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from kodimanager.gui.main_window import main

if __name__ == "__main__":
    main()
