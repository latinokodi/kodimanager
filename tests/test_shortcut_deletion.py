import pytest
import os
import shutil
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from kodimanager.core.manager import InstanceManager
from kodimanager.utils.shortcuts import ShortcutManager

def test_shortcut_deletion(tmp_path):
    # Setup mocks
    config_dir = tmp_path / "config"
    instance_manager = InstanceManager(config_dir=str(config_dir))
    
    # Create dummy instance
    kodi_path = str(tmp_path / "Inst1")
    os.makedirs(kodi_path)
    inst = instance_manager.register_instance("TestInstance", kodi_path, "19.5")
    
    # Create dummy shortcut
    desktop = tmp_path / "Desktop"
    os.makedirs(desktop)
    shortcut_path = desktop / f"Kodi - {inst.name}.lnk"
    with open(shortcut_path, "w") as f:
        f.write("mock shortcut")
        
    assert os.path.exists(shortcut_path)

    # Mock expanduser to point to our temp desktop
    with patch("os.path.expanduser", return_value=str(tmp_path)):
        instance_manager.remove_instance(inst.id)
        
    assert not os.path.exists(shortcut_path)

