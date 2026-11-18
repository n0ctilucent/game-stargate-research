"""Unit tests for automated rail control, registry synchronization, and telemetry processing."""
import json
import os
import sys
import pytest
from pathlib import Path

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rail.rail_manager import RailRegistry, MarkerManager, RailManager
from rail.skynet_rail_control import SkynetRailController, DEFAULT_HUBS


def test_rail_registry_loading(tmp_path):
    """Verifies that RailRegistry properly parses switches and saves updates."""
    mock_registry = tmp_path / "rail_registry.json"
    initial_data = {
        "switches": {
            "test_switch_01": {
                "name": "Test Switch Alpha",
                "coords": {"x": 100, "y": 64, "z": 200},
                "state": False
            }
        }
    }
    mock_registry.write_text(json.dumps(initial_data))

    reg = RailRegistry(mock_registry)
    sw = reg.get_switch("test_switch_01")
    assert sw is not None
    assert sw["name"] == "Test Switch Alpha"
    assert sw["state"] is False

    # Test state persistence
    success = reg.set_switch_state("test_switch_01", True)
    assert success is True

    # Reload from disk
    reg2 = RailRegistry(mock_registry)
    assert reg2.get_switch("test_switch_01")["state"] is True


def test_marker_manager_updates(tmp_path):
    """Verifies that MarkerManager updates POI colors dynamically."""
    mock_markers = tmp_path / "markers.json"
    initial_markers = {
        "markers": [
            {"id": "switch_alpha", "color": "#FF0000"}
        ]
    }
    mock_markers.write_text(json.dumps(initial_markers))

    mm = MarkerManager(mock_markers)
    updated = mm.update_marker("switch_alpha", active=True)
    assert updated is True

    # Verify persisted color
    with open(mock_markers) as f:
        data = json.load(f)
    assert data["markers"][0]["color"] == "#00FF00"


def test_skynet_hub_mapping():
    """Verifies that SkynetRailController defines known hubs with valid coordinates."""
    controller = SkynetRailController()
    assert "HUB_06" in DEFAULT_HUBS
    assert "HUB_03" in DEFAULT_HUBS
    assert DEFAULT_HUBS["HUB_06"]["x"] == -1212
    assert DEFAULT_HUBS["HUB_03"]["z"] == -658


def test_rail_manager_toggle_switch_mock(monkeypatch):
    """Verifies toggle_switch calls toggle_rail and updates registry."""
    manager = RailManager()

    # Mock toggle_rail to avoid requiring live RCON
    toggled_coords = []
    def mock_toggle_rail(x, y, z, state):
        toggled_coords.append((x, y, z, state))
        return True

    monkeypatch.setattr(manager, "toggle_rail", mock_toggle_rail)

    # Use a registered switch
    success = manager.toggle_switch("washington_terminus_main", True)
    assert success is True
    assert len(toggled_coords) == 1
    assert toggled_coords[0] == (-1212, 76, -670, True)
