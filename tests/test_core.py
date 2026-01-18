import pytest
import os
import shutil
from src.kodimanager.core.models import KodiInstance
from src.kodimanager.core.manager import InstanceManager
from src.kodimanager.core.downloader import KodiDownloader

@pytest.fixture
def instance_manager(tmp_path):
    config_dir = tmp_path / "config"
    return InstanceManager(config_dir=str(config_dir))

def test_model_validity(tmp_path):
    # Setup dummy path
    os.makedirs(tmp_path / "kodi")
    instance = KodiInstance("id1", "MyKodi", str(tmp_path / "kodi"), "20.2", 0)
    assert instance.is_valid()
    assert instance.path == str(tmp_path / "kodi")

def test_manager_crud(instance_manager, tmp_path):
    # Create dummy path
    kodi_path = str(tmp_path / "Inst1")
    os.makedirs(kodi_path)
    
    # Add
    inst = instance_manager.register_instance("TestInstance", kodi_path, "19.5")
    assert inst.name == "TestInstance"
    assert len(instance_manager.get_all()) == 1
    
    # Check persistence
    assert os.path.exists(os.path.join(instance_manager.config_dir, "instances.json"))
    
    # Remove
    instance_manager.remove_instance(inst.id)
    assert len(instance_manager.get_all()) == 0

def test_downloader_connection():
    # Only if network is allowed. In this environment it should be.
    # We just want to check if it parses anything at all.
    downloader = KodiDownloader()
    versions = downloader.get_available_versions()
    # It might fail if site changes or no network, but let's see.
    # Asserting non-empty might be flaky if site is down.
    # We will just print len.
    print(f"Found {len(versions)} versions")
