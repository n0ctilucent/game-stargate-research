#!/usr/bin/env python3
"""
telemetry_receiver.py — Rail Telemetry Ingestion & AI Routing Processor
Stargate Control Plane / Paper 1.21.1 Distributed Infrastructure

Ingests `CART_PASS` and detector rail events dispatched by chonk_telemetry_bridge,
evaluates switch routing via Ollama LLM (or deterministic fallback), and dispatches
state changes to RailManager.
"""

import asyncio
import json
import logging
import os
import urllib.request
from pathlib import Path

from rail.rail_manager import RailManager
from utils.config_utils import setup_logging, Config

rail_traffic_logger = setup_logging("rail_traffic", log_file="logs/rail_traffic.log")
logger = setup_logging("telemetry_receiver")

# Deterministic fallback mapping when LLM inference is disabled or unreachable
DEFAULT_NODE_SWITCH_MAP = {
    "CHONK-01": "chonk_01_sensor",
    "CHONK-02": "chonk_02_sensor",
    "CHONK-03": "chonk_03_sensor",
    "HUB_06": "washington_terminus_main",
    "HUB_03": "deep_rail_vertical_1"
}


class RailTelemetryProcessor:
    def __init__(
        self,
        rcon_host: str | None = None,
        rcon_port: int | None = None,
        rcon_password: str | None = None,
        ollama_url: str | None = None,
        ai_model: str = "mistral"
    ):
        host = rcon_host or getattr(Config, "CHONK_IP", "10.10.8.60")
        port = rcon_port or getattr(Config, "RCON_PORT", 25575)
        password = rcon_password or getattr(Config, "RCON_PASS", "dinosaurExTraVaGanZa1969")

        self.ollama_url = ollama_url or os.getenv("OLLAMA_HOST", "http://10.10.8.60:11434") + "/api/generate"
        self.ai_model = os.getenv("AI_MODEL", ai_model)

        self.rail_manager = RailManager(
            rcon_host=host,
            rcon_port=port,
            rcon_password=password
        )
        logger.info(f"RailTelemetryProcessor initialized (RCON {host}:{port}, Ollama {self.ollama_url})")

    def _query_ollama_sync(self, prompt: str) -> str | None:
        """Queries the Ollama endpoint synchronously with a strict 2-second timeout."""
        payload = json.dumps({
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(
            self.ollama_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except Exception as e:
            logger.debug(f"Ollama inference unavailable ({e}); falling back to deterministic routing rules.")
            return None

    async def _orchestrate_with_llm(self, event_data: dict) -> dict:
        """
        Determines train priority and switch toggles using LLM evaluation
        with graceful fallback to deterministic switch mapping.
        """
        node = event_data.get("NODE") or event_data.get("node")
        coords = event_data.get("coords") or event_data.get("data", {})
        rail_id = event_data.get("rail_id")

        rail_traffic_logger.info(f"LLM Orchestration: Receiving event: {event_data}")

        # Attempt Ollama inference if enabled
        if os.getenv("ENABLE_LLM_ROUTING", "0") == "1":
            prompt = (
                f"You are the Stargate Rail Orchestrator. A cart passed sensor node {node} at {coords}. "
                f"Available switches: {list(DEFAULT_NODE_SWITCH_MAP.values())}. "
                f"Return JSON strictly formatted as: {{\"action\": \"toggle_switch\", \"switch_id\": \"<id>\", \"state\": true/false}}"
            )
            raw_response = await asyncio.to_thread(self._query_ollama_sync, prompt)
            if raw_response:
                try:
                    decision = json.loads(raw_response)
                    if "action" in decision:
                        return decision
                except Exception:
                    logger.debug("Failed to parse LLM JSON response; falling back to deterministic rule.")

        # Deterministic Fallback Rule
        switch_id = DEFAULT_NODE_SWITCH_MAP.get(node)
        if not switch_id and rail_id:
            for k, v in DEFAULT_NODE_SWITCH_MAP.items():
                if k.lower() in rail_id.lower():
                    switch_id = v
                    break

        if switch_id:
            # By default, toggle the switch to active (True) upon cart pass
            llm_decision = {"action": "toggle_switch", "switch_id": switch_id, "state": True}
        else:
            llm_decision = {"action": "no_action"}

        rail_traffic_logger.info(f"LLM Orchestration: Decision for {node}: {llm_decision}")
        return llm_decision

    async def process_rail_event(self, event_data: dict):
        """
        Ingests, parses, logs, and orchestrates rail telemetry events.
        """
        rail_traffic_logger.info(f"Received rail telemetry: {json.dumps(event_data)}")

        raw_decision = await self._orchestrate_with_llm(event_data)
        decisions = raw_decision if isinstance(raw_decision, list) else [raw_decision]

        for llm_decision in decisions:
            action = llm_decision.get("action")

            if action == "toggle_switch":
                switch_id = llm_decision.get("switch_id")
                state = llm_decision.get("state", True)
                logger.info(f"Orchestrator toggling switch '{switch_id}' to state={state}")

                success = await asyncio.to_thread(self.rail_manager.toggle_switch, switch_id, state)
                if success:
                    logger.info(f"Successfully executed routing decision for {switch_id}.")
                else:
                    logger.error(f"Failed to execute routing decision for {switch_id}.")

            elif action == "no_action":
                logger.debug("Orchestrator decided no action is required for this event.")
            else:
                logger.warning(f"Unknown routing decision: {action}. Taking no action.")


if __name__ == "__main__":
    async def simulate_event():
        processor = RailTelemetryProcessor()
        test_event = {
            "EVENT": "CART_PASS",
            "NODE": "CHONK-01",
            "coords": {"x": 1585, "y": 59, "z": 670},
            "timestamp": "2026-11-15T11:00:00Z"
        }
        await processor.process_rail_event(test_event)

    try:
        asyncio.run(simulate_event())
    except KeyboardInterrupt:
        logger.info("Telemetry receiver simulation stopped.")
