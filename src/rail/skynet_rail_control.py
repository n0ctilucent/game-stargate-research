#!/usr/bin/env python3
"""
skynet_rail_control.py — Skynet Control Plane Signal Tower & Switch Interface
Distributed Stargate/Skynet Architecture / Paper 1.21.1

Manages Observer-wall vertical signal chains and RCON switch toggles on Chonk (10.10.8.60).
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path if invoked standalone
PROJECT_SRC = Path(__file__).resolve().parent.parent
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from rail.rail_manager import SafeMCRcon, RailRegistry
from utils.config_utils import Config, setup_logging

logger = setup_logging("skynet_rail_control")

# Hub coordinate mapping (with fallback to known physical Signal Bases)
DEFAULT_HUBS = {
    "HUB_06": {"x": -1212, "y": 76, "z": -670, "switch_id": "washington_terminus_main"},
    "HUB_03": {"x": -1283, "y": 77, "z": -658, "switch_id": "deep_rail_vertical_1"}
}


class SkynetRailController:
    """Manages signal tower observer states and switch lines from the Skynet plane."""

    def __init__(
        self,
        chonk_ip: str | None = None,
        rcon_port: int | None = None,
        rcon_pass: str | None = None,
        registry: RailRegistry | None = None
    ):
        self.chonk_ip = chonk_ip or getattr(Config, "CHONK_IP", "10.10.8.60")
        self.rcon_port = int(rcon_port or getattr(Config, "RCON_PORT", 25575))
        self.rcon_pass = rcon_pass or getattr(Config, "RCON_PASS", "dinosaurExTraVaGanZa1969")
        self.registry = registry or RailRegistry()

    def update_signal_tower(self, hub_id: str, status: str) -> bool:
        """
        Interfaces with the signal tower at the specified Hub using Observer-Wall updates.
        status: "STOP" (places redstone_block) or "CLEAR" / "GO" (places air).
        """
        hub_data = DEFAULT_HUBS.get(hub_id)
        if not hub_data:
            # Check registry
            switch = self.registry.get_switch(hub_id)
            if switch and "coords" in switch:
                hub_data = switch
            else:
                logger.error(f"Unknown Hub ID: {hub_id}")
                return False

        coords = hub_data.get("coords") if "coords" in hub_data else hub_data
        block_type = "redstone_block" if status.upper() == "STOP" else "air"

        command = f"setblock {coords['x']} {coords['y']} {coords['z']} {block_type}"

        if SafeMCRcon is None:
            logger.error("SafeMCRcon library not available")
            return False

        try:
            with SafeMCRcon(self.chonk_ip, self.rcon_pass, port=self.rcon_port) as mcr:
                resp = mcr.command(command)
                logger.info(f"Signal {hub_id} ({coords['x']},{coords['y']},{coords['z']}) set to {status}: {resp}")
                return True
        except Exception as e:
            logger.error(f"RCON Link to Chonk ({self.chonk_ip}) failed: {e}")
            return False


# Module-level convenience function matching legacy call signatures
_default_controller = None

def update_signal_tower(hub_id: str, status: str) -> bool:
    global _default_controller
    if _default_controller is None:
        _default_controller = SkynetRailController()
    return _default_controller.update_signal_tower(hub_id, status)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skynet Signal Tower Controller")
    parser.add_argument("--hub", default="HUB_06", choices=list(DEFAULT_HUBS.keys()), help="Target Hub ID")
    parser.add_argument("--status", default="STOP", choices=["STOP", "CLEAR", "GO"], help="Signal Status")
    args = parser.parse_args()

    success = update_signal_tower(args.hub, args.status)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
