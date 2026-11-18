# Distributed Railway Control & Automation Architecture

**Target Environment:** Paper 1.21.1 (`chonk.lab.bitsmasher.net`)  
**Control Subsystem:** Stargate Research Control Plane (`game-stargate-research`)  
**Digital Twin Registry:** `config/rail_registry.json`

---

## 1. Subsystem Overview & Node Allocation

The bitsmasher.net distributed railway architecture coordinates automated switching, entity safety verification, and telemetry tracking across multi-node hardware accelerators:

| Host / Node | Role & Hardware | Operational Responsibility |
| :--- | :--- | :--- |
| **Chonk** (`10.10.8.60`) | Core PaperMC Server & Ollama | Executes `/setblock` RCON commands (port 25575), tracks entities in world, runs local Ollama inference (`:11434`). |
| **Stargate** (`10.10.16.66`) | FastMCP Hub & Orchestrator | Runs `TelemetryListener` (port 5005) and `RailTelemetryProcessor`, dispatching routing decisions and BlueMap POI updates. |
| **Skynet** (`10.10.16.10`) | Path Optimization & NPU | Runs Hailo-8L NPU path planning and Observer signal tower toggles (`skynet_rail_control.py`). |
| **Edge-T** (`10.10.16.4`) | Vision Safety Daemon (Coral TPU)| Performs entity proximity verification (`check_safety` on port 8808) before switches toggle, preventing cart collision with players/mobs. |
| **Jetson Nodes** (`10.10.12.90–.93`)| Edge Builder Containers | Runs containerized `rail-builder` (port 8091) and `redstone-builder` (port 8092) for 3D procedural track and schematic synthesis. |

---

## 2. Core Components in `src/rail/`

### 2.1 [rail_manager.py](file:///home/franklin/workspace/gaming/game-stargate-research/src/rail/rail_manager.py)
* **Thread-Safe RCON (`SafeMCRcon`):** Replaces legacy `signal.alarm()` timeout handling with native socket timeouts, permitting RCON execution inside worker threads and asynchronous task pools without `ValueError: signal only works in main thread`.
* **Digital Twin Registry (`RailRegistry`):** Reads and updates `config/rail_registry.json`. Synchronously detects file modifications on disk (`is_registry_changed()`) and tracks switch coordinates (`coords: {x, y, z}`) and Boolean states.
* **Edge-T Safety Interlock (`check_safety`):** Connects to the Coral TPU vision daemon on `10.10.16.4:8808` to verify no entities are within 5 blocks of a switch.
* **Switch Toggle API (`toggle_switch`):**
  ```python
  from rail.rail_manager import RailManager
  manager = RailManager()
  success = manager.toggle_switch("washington_terminus_main", state=True)
  ```

### 2.2 [telemetry_receiver.py](file:///home/franklin/workspace/gaming/game-stargate-research/src/rail/telemetry_receiver.py)
* **Ingestion:** Consumes `CART_PASS` and detector rail packets forwarded by `chonk_telemetry_bridge.py`.
* **AI & Deterministic Routing:**
  * When `ENABLE_LLM_ROUTING=1`, queries Chonk Ollama (`http://10.10.8.60:11434/api/generate`) with a 2-second timeout.
  * Defaults to the deterministic node mapping (`CHONK-01..03`, `HUB_06`, `HUB_03`) to guarantee 20 TPS performance during heavy building cycles.
* **Execution:** Calls `rail_manager.toggle_switch()` to align track and updates `logs/rail_traffic.log`.

### 2.3 [skynet_rail_control.py](file:///home/franklin/workspace/gaming/game-stargate-research/src/rail/skynet_rail_control.py)
* Interfaces with vertical Observer-wall signal chains at key hubs:
  * `HUB_06` (`washington_terminus_main`): `(-1212, 76, -670)`
  * `HUB_03` (`deep_rail_vertical_1`): `(-1283, 77, -658)`
* Dispatches `STOP` (`redstone_block`) or `CLEAR` (`air`) to trigger physical redstone displays without ticking delay.

### 2.4 [containment_rail_builder.py](file:///home/franklin/workspace/gaming/game-stargate-research/src/rail/containment_rail_builder.py)
* **Corner Geometry Synthesis:** Enforces standard unpowered `minecraft:rail[shape=...]` and inert `minecraft:polished_deepslate` roadbed ($Y=63$) at 90° turns.
* **Schematic Output:** Emits verified `.schem` and `.json` manifests for all four orbital loop corners (`CONTAINMENT_ORBITAL_CORNER_NW..SW`) and the AI Lab building spur.

---

## 3. Digital Twin Switch Schema (`config/rail_registry.json`)

```json
{
  "switches": {
    "washington_terminus_main": {
      "name": "Washington Terminus - Main Switch",
      "coords": { "x": -1212, "y": 76, "z": -670 },
      "state": false
    },
    "deep_rail_vertical_1": {
      "name": "Deep Rail Vertical Transition A",
      "coords": { "x": -1283, "y": 77, "z": -658 },
      "state": false
    },
    "chonk_01_sensor": {
      "name": "Sensor Node CHONK-01",
      "coords": { "x": 1585, "y": 59, "z": 670 },
      "state": false
    }
  }
}
```

---

## 4. Verification & Testing

Run the automated rail test suites:
```bash
# Verify containment rail corners and vector calculations (13 tests)
pytest /home/minecraft/test/test_containment_rail.py

# Verify live switch toggle via CLI
python3 src/rail/skynet_rail_control.py --hub HUB_06 --status CLEAR

# Run telemetry receiver simulation
python3 src/rail/telemetry_receiver.py
```
