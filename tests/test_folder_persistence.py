
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
    
    # Mock shortcut deletion and process killing
    with patch.object(ShortcutManager, 'delete_shortcut', return_value=True), \
         patch.object(InstanceManager, '_kill_process_in_folder', return_value=None):
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
        # We assume real internal os.path.exists works
        
        with patch.object(ShortcutManager, 'delete_shortcut', return_value=True), \
             patch.object(InstanceManager, '_kill_process_in_folder', return_value=None):
             result = instance_manager.remove_instance(inst.id, delete_files=True)
             
    assert result is False
    assert os.path.exists(kodi_path)
    # Important: Instance should still be in the manager
    assert len(instance_manager.get_all()) == 1
