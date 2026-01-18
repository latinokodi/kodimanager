
import pytest
import os
import shutil
import sys
import time
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from kodimanager.core.manager import InstanceManager
from kodimanager.utils.shortcuts import ShortcutManager

def test_folder_deletion_success(tmp_path):
    # Setup
    config_dir = tmp_path / "config"
    instance_manager = InstanceManager(config_dir=str(config_dir))
    
    kodi_path = tmp_path / "InstSuccess"
    os.makedirs(kodi_path)
    inst = instance_manager.register_instance("InstSuccess", str(kodi_path), "19.5")
    
    # Mock shortcut deletion to avoid errors
    with patch.object(ShortcutManager, 'delete_shortcut', return_value=True):
        result = instance_manager.remove_instance(inst.id, delete_files=True)
        
    assert result is True
    assert not os.path.exists(kodi_path)
    assert len(instance_manager.get_all()) == 0

def test_folder_deletion_failure_keeps_instance(tmp_path):
    # Setup
    config_dir = tmp_path / "config"
    instance_manager = InstanceManager(config_dir=str(config_dir))
    
    kodi_path = tmp_path / "InstFail"
    os.makedirs(kodi_path)
    inst = instance_manager.register_instance("InstFail", str(kodi_path), "19.5")
    
    # Mock rmtree to fail always
    def failing_rmtree(path, onerror=None):
        raise OSError("Permission denied")

    with patch("shutil.rmtree", side_effect=failing_rmtree):
        # Also need to mock os.path.exists to return True (simulating file still there)
        # But we need real exists for setup, so we only mock it during the call if possible
        # Or just let rmtree fail and rely on the fact that the directory actually still exists in reality?
        # The code checks os.path.exists(instance.path) to verify deletion.
        # Since we are mocking rmtree to do nothing (raise error), the real folder stays.
        
        with patch.object(ShortcutManager, 'delete_shortcut', return_value=True):
             result = instance_manager.remove_instance(inst.id, delete_files=True)
             
    assert result is False
    assert os.path.exists(kodi_path)
    # Important: Instance should still be in the manager
    assert len(instance_manager.get_all()) == 1
