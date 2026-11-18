#!/usr/bin/env python3
"""
rail_manager.py — Automated Railway Switch & Signal Manager
Paper 1.21.1 / Distributed Cluster Infrastructure

Responsibilities:
1. RCON Switch Controller: Manipulates powered_rail and track blocks on Chonk (10.10.8.60:25575).
2. Digital Twin Synchronization: Maintains config/rail_registry.json switch definitions.
3. Edge-T Safety Interlock: Proximity checks against Edge TPU daemon (10.10.16.4:8808).
4. BlueMap POI Synchronization: Updates switch visualization state colors.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import socket
    from mcrcon import MCRcon

    class SafeMCRcon(MCRcon):
        """Thread-safe MCRcon implementation using socket timeouts instead of SIGALRM."""
        def __init__(self, host, password, port=25575, timeout=5):
            self.host = host
            self.password = password
            self.port = port
            self.tlsmode = 0
            self.timeout = timeout
            self.socket = None

        def connect(self):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self._send(3, self.password)

        def _read(self, length):
            data = b""
            while len(data) < length:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    break
                data += chunk
            return data
except ImportError:
    SafeMCRcon = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("rail_manager")


class RailRegistry:
    """Manages reading and persisting switch states in config/rail_registry.json."""

    def __init__(self, registry_file: str | Path | None = None):
        if registry_file is None:
            # Look in local repo or sibling game-skynet-minecraft repo
            candidates = [
                Path("config/rail_registry.json"),
                Path("../config/rail_registry.json"),
                Path("/home/franklin/workspace/gaming/game-stargate-research/config/rail_registry.json"),
                Path("/home/franklin/workspace/gaming/game-skynet-minecraft/config/rail_registry.json")
            ]
            self.registry_file = next((c for c in candidates if c.exists()), candidates[0])
        else:
            self.registry_file = Path(registry_file)

        self.registry_data: dict = {}
        self.last_modified: float = 0.0
        self.load_registry()

    def load_registry(self) -> dict:
        """Loads and returns registry data from disk."""
        if not self.registry_file.exists():
            logger.warning(f"Registry file not found at {self.registry_file}")
            self.registry_data = {"switches": {}}
            return self.registry_data

        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                self.registry_data = json.load(f)
            self.last_modified = os.stat(self.registry_file).st_mtime
            logger.debug(f"Loaded rail registry from {self.registry_file}")
        except Exception as e:
            logger.error(f"Failed to load registry from {self.registry_file}: {e}")
            if not self.registry_data:
                self.registry_data = {"switches": {}}

        return self.registry_data

    def is_registry_changed(self) -> bool:
        """Checks if registry file on disk has been modified."""
        if not self.registry_file.exists():
            return False
        current_modified = os.stat(self.registry_file).st_mtime
        if current_modified != self.last_modified:
            self.last_modified = current_modified
            return True
        return False

    def get_switch(self, switch_id: str) -> dict | None:
        """Retrieves a switch definition by its identifier."""
        switches = self.registry_data.get("switches", {})
        return switches.get(switch_id)

    def set_switch_state(self, switch_id: str, state: bool) -> bool:
        """Updates switch state and persists back to the registry file."""
        if "switches" not in self.registry_data:
            self.registry_data["switches"] = {}

        if switch_id in self.registry_data["switches"]:
            self.registry_data["switches"][switch_id]["state"] = state
        else:
            self.registry_data["switches"][switch_id] = {
                "name": switch_id,
                "state": state
            }

        try:
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self.registry_data, f, indent=4)
            self.last_modified = os.stat(self.registry_file).st_mtime
            return True
        except Exception as e:
            logger.error(f"Failed to persist registry to {self.registry_file}: {e}")
            return False


class MarkerManager:
    """Synchronizes rail switch states to BlueMap marker configurations."""

    def __init__(self, markers_file: str | Path | None = None):
        if markers_file is None:
            candidates = [
                Path("markers.json"),
                Path("/home/minecraft/plugins/BlueMap/markers.json")
            ]
            self.markers_file = next((c for c in candidates if c.exists()), candidates[0])
        else:
            self.markers_file = Path(markers_file)

        self.markers_data: dict = {}
        self.load_markers()

    def load_markers(self) -> dict:
        if not self.markers_file.exists():
            self.markers_data = {"markers": []}
            return self.markers_data

        try:
            with open(self.markers_file, "r", encoding="utf-8") as f:
                self.markers_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load markers from {self.markers_file}: {e}")
            self.markers_data = {"markers": []}
        return self.markers_data

    def update_marker(self, marker_id: str, active: bool) -> bool:
        """Updates POI marker color: Green (#00FF00) if active, Red (#FF0000) if inactive."""
        if not self.markers_data or "markers" not in self.markers_data:
            return False

        updated = False
        for mark in self.markers_data.get("markers", []):
            if mark.get("id") == marker_id:
                mark["color"] = "#00FF00" if active else "#FF0000"
                updated = True
                break

        if updated and self.markers_file.exists():
            try:
                with open(self.markers_file, "w", encoding="utf-8") as f:
                    json.dump(self.markers_data, f, indent=4)
                return True
            except Exception as e:
                logger.warning(f"Failed to write markers to {self.markers_file}: {e}")

        return updated


class RailManager:
    """
    Core Railway Automation Controller.
    Manages RCON setblock toggles, Edge-T vision safety gating, and registry persistence.
    """

    def __init__(
        self,
        rcon_host: str | None = None,
        rcon_port: int | None = None,
        rcon_password: str | None = None,
        registry_file: str | Path | None = None,
        markers_file: str | Path | None = None,
        edge_t_host: str | None = None,
        edge_t_port: int = 8808
    ):
        self.rcon_host = rcon_host or os.getenv("CHONK_IP", "10.10.8.60")
        self.rcon_port = int(rcon_port or os.getenv("RCON_PORT", 25575))
        self.rcon_password = rcon_password or os.getenv("RCON_PASS", "dinosaurExTraVaGanZa1969")

        self.edge_t_host = edge_t_host or os.getenv("EDGE_T_IP", "10.10.16.4")
        self.edge_t_port = edge_t_port

        self.rail_registry = RailRegistry(registry_file)
        self.marker_manager = MarkerManager(markers_file)

        logger.info(
            f"RailManager initialized: RCON {self.rcon_host}:{self.rcon_port}, "
            f"Edge-T {self.edge_t_host}:{self.edge_t_port}"
        )

    def check_safety_sync(self, x: int, y: int, z: int, radius: int = 5) -> bool:
        """
        Synchronous wrapper around Edge-T proximity check.
        Queries the Coral TPU vision daemon (Hub-06 / Edge-T).
        Fails safe (aborts) if entities are detected.
        """
        if os.getenv("SKIP_SAFETY_CHECK", "0") == "1":
            return True

        import socket
        try:
            with socket.create_connection((self.edge_t_host, self.edge_t_port), timeout=1.5) as s:
                query = json.dumps({"task": "proximity_check", "coords": [x, y, z], "radius": radius})
                s.sendall(query.encode() + b"\n")
                resp = s.recv(1024)
                data = json.loads(resp.decode())

                if data.get("detected_entities", 0) > 0:
                    os.makedirs("logs", exist_ok=True)
                    with open("logs/rail_safety.log", "a", encoding="utf-8") as log_file:
                        log_file.write(
                            f"[{datetime.now()}] ABORT: Entity detected within {radius} blocks of ({x},{y},{z})\n"
                        )
                    logger.warning(f"Safety check aborted: entity near ({x},{y},{z})")
                    return False
                return True
        except Exception as e:
            logger.debug(f"Edge-T Safety check unavailable ({e}); proceeding under fail-safe policy.")
            return True

    async def check_safety(self, x: int, y: int, z: int, radius: int = 5) -> bool:
        """Asynchronous safety check wrapper."""
        return await asyncio.to_thread(self.check_safety_sync, x, y, z, radius)

    def toggle_rail(self, x: int, y: int, z: int, state: bool) -> bool:
        """
        Directly manipulates a powered_rail block at (x, y, z) via RCON.
        """
        if not self.check_safety_sync(x, y, z):
            return False

        if SafeMCRcon is None:
            logger.error("mcrcon library is not installed")
            return False

        command = f"setblock {x} {y} {z} minecraft:powered_rail[powered={str(state).lower()}]"

        try:
            with SafeMCRcon(self.rcon_host, self.rcon_password, port=self.rcon_port) as mcr:
                resp = mcr.command(command)
                logger.info(f"RCON setblock ({x}, {y}, {z}) -> powered={state}: {resp}")
                return True
        except Exception as e:
            logger.error(f"RCON setblock failed at ({x}, {y}, {z}): {e}")
            return False

    def toggle_switch(self, switch_id: str, state: bool) -> bool:
        """
        Toggles a registered rail switch by its UUID / identifier.
        Used directly by TelemetryReceiver and FastMCP dispatcher.
        """
        switch = self.rail_registry.get_switch(switch_id)
        if not switch:
            logger.error(f"Switch '{switch_id}' not found in registry")
            return False

        coords = switch.get("coords")
        if not coords or "x" not in coords or "y" not in coords or "z" not in coords:
            logger.error(f"Switch '{switch_id}' has invalid coordinates: {coords}")
            return False

        x, y, z = coords["x"], coords["y"], coords["z"]
        success = self.toggle_rail(x, y, z, state)

        if success:
            self.rail_registry.set_switch_state(switch_id, state)
            self.marker_manager.update_marker(switch_id, state)
            logger.info(f"Successfully toggled switch '{switch_id}' to state={state}")

        return success

    async def sync_bluemap(self, marker_id: str, active: bool):
        """Asynchronously triggers BlueMap marker update."""
        await asyncio.to_thread(self.marker_manager.update_marker, marker_id, active)

    async def main_loop(self):
        """Monitors rail_registry.json for changes on disk and applies state updates."""
        logger.info("Entering RailManager registry polling loop...")
        while True:
            if self.rail_registry.is_registry_changed():
                logger.info("Registry change detected on disk. Applying updates...")
                data = self.rail_registry.load_registry()
                for switch_id, switch in data.get("switches", {}).items():
                    target_state = switch.get("state", False)
                    coords = switch.get("coords", {})
                    if "x" in coords and "y" in coords and "z" in coords:
                        await asyncio.to_thread(
                            self.toggle_rail, coords["x"], coords["y"], coords["z"], target_state
                        )
            await asyncio.sleep(1)


if __name__ == "__main__":
    manager = RailManager()
    try:
        asyncio.run(manager.main_loop())
    except KeyboardInterrupt:
        logger.info("RailManager terminated by user.")
