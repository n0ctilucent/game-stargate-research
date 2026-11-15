# game-stargate-research

**Dreamland Stargate MCP — Distributed Text-to-Building Minecraft (T2BM) Control Plane.**

A cyber-noir themed, AI-driven infrastructure for orchestrating Minecraft construction across a distributed mesh of hardware nodes. Built around the "Industrial Singularity" aesthetic: high-tech materials, deepslate/tuff palettes, automated schematic deployment, and real-time telemetry-driven rail management.

---

## Project Overview

Stargate acts as the central architectural agent within the Dreamland/Skynet cluster, bridging LLM inference with Minecraft server-side tools (WorldEdit, RCON, MCP, BlueMap). It converts textual building intents into validated schematics deployed via an AI-accelerated control plane.

**Current State:** Active — v5 Industrial Standards in production. Greeble-driven spatial mutation engine. NVIDIA Jetson edge cluster integrated for CUDA-accelerated voxel processing.

---

## Architecture & Hardware Constructs

```
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│   Stargate (Hub-01)    │◄───►│    Skynet (Hub-00)     │◄───►│    Edge-T (Hub-06)     │
│   Central Orchestrator │     │ Structural Integrity   │     │ Greebling Verification │
│   T2BM Inference Hub   │     │ Global Coordinates     │     │ Permutation Testing    │
│   FastMCP & Telemetry  │     │ Hailo-8L + USB TPU     │     │ Integrated Edge TPU    │
└────────────────────────┘     └────────────────────────┘     └────────────────────────┘
            │                               │                              │
            ▼                               ▼                              ▼
  Minecraft Paper Server            BlueMap Visualizer             Deep Rail Network
  (Chonk: RCON / WorldEdit)      (Web Interface / API)         (Observer Signal Towers)
```

### Hardware Inventory

| Node | Hostname / IP | Hardware Spec | Role / Zone |
|------|---------------|---------------|-------------|
| **Stargate** (Hub-01) | `stargate.research.bitsmasher.net` (`10.10.16.66`) | Raspberry Pi 5, 8GB RAM, 476.9 GB NVMe SSD | Central Orchestrator, T2BM inference nexus, FastMCP server, TCP telemetry listener |
| **Skynet** (Hub-00) | `skynet-pi5.local` (`10.10.16.10`) | Raspberry Pi 5, Hailo-8L NPU (13 TOPS) + Google Coral Edge TPU (USB) | Structural integrity audits, high-density geometric voxel expansion (Skynet AI Testing Field) |
| **Edge-T** (Hub-06) | `tpu-host.local` (`10.10.16.4`) | ASUS Tinker Edge T, Integrated Edge TPU (4 TOPS) | Reactive mutation, perimeter vision, low-latency terrain analysis (Neural Uplink & Solar Induction) |
| **Edge-J01..J04** | `10.10.16.20`–`23` | NVIDIA Jetson Nano / Orin Edge Cluster | CUDA-accelerated voxel processing, real-time greeble injection |
| **Chonk Host** | `chonk.lab.bitsmasher.net` (`10.10.8.60`) | Multi-core x86_64 host, Paper 26.2 (Java 25) | Dedicated Paper Minecraft server, WorldEdit, BlueMap API, RCON command bridge |
| **Blowfish** (Hub-07) | `blowfish.lab.bitsmasher.net` (`10.10.16.1` / `10.10.12.15`) | OpenBSD 7.8 | MariaDB Neural-Data Vault (`bluemap` database, historical telemetry) |

### Network & Service Matrix

| Service | Host | Port / Protocol | Purpose |
|---------|------|-----------------|---------|
| **FastMCP Server** | Stargate (`10.10.16.66`) | `8989` HTTP | FastMCP endpoint exposing health checks and Vertex AI custom training pipeline |
| **Telemetry Ingestion** | Stargate (`10.10.16.66`) | `5005` TCP | Receives in-game telemetry events (`CART_PASS`, redstone triggers) |
| **Skynet WebSocket** | Skynet (`10.10.16.10`) | `8765` WS | WebSocket control plane for NPU geometric expansion |
| **Edge-T WebSocket** | Edge-T (`10.10.16.4`) | `8765` WS | WebSocket interface for Edge TPU computer vision and terrain verification |
| **Minecraft Server** | Chonk (`10.10.8.60`) | `25565` TCP | Paper Minecraft server game port |
| **RCON Bridge** | Chonk (`10.10.8.60`) | `25575` TCP | Server remote console command execution |
| **BlueMap Web / API** | Chonk (`10.10.8.60`) | `8100` HTTP | Real-time map rendering and marker overlays |
| **MariaDB Vault** | Blowfish (`10.10.16.1`) | `3306` TCP | Relational data store for spatial registries and telemetry |
| **MariaDB FastMCP** | Blowfish (`10.10.16.1`) | `8989` HTTP | Dedicated FastMCP server for MariaDB SQL inspection and queries |

---

## T2BM Interlayer Protocol

The Text-to-Building Minecraft (T2BM) interlayer operates via intent-based construction primitives rather than raw coordinate dumps. All mappings and protocols conform to [TB2M_SPEC.md](src/TB2M_SPEC.md).

### Semantic Intent Mapping

| Intent Keyword | Target Block Palette | Architectural Function |
|----------------|----------------------|------------------------|
| `base_plate` | `deepslate_tiles` | Structural foundation and baseline slab |
| `skeleton` | `polished_tuff` / `polished_deepslate` | Load-bearing structural frame and columns |
| `reactor` | `crying_obsidian` | Power core and high-energy central containment |
| `lumen` | `pearlescent_froglight` | Recessed cybernetic illumination |
| `greeble_accent` | `emerald_block` / `tinted_glass` | High-tech visual detail and energy conduits |

### Schematic Classification

- **Foundation (`Foundation`):** Initial base structure generated by primary LLM reasoning.
- **Delta (`Delta`):** AI-synthesized mutations layered onto existing foundations (e.g., `emerald_delta.json` applying greeble layers to standard structural pillars).
- **Metadata Requirement:** Every schematic artifact must have an accompanying JSON metadata descriptor including `schematic_type`, `author`, `hash`, and `dimensions`.

---

## Project Structure

```
game-stargate-research/
├── bin/                              # Cluster operational scripts
│   ├── common.sh                     # Shell library: logging, error handling, config parsing
│   └── hydrate.sh                    # Automated environment hydration and dependency sync
├── docs/                             # Architecture specs and guidelines
│   ├── CONTEXT.md                    # Core project context, roles, and hardware topology
│   ├── GEMINI.md                     # LLM development directives and architectural constraints
│   ├── settings.json                 # Node and environment-specific settings
│   ├── first-vertex-build.txt        # Initial Vertex AI greeble build log
│   └── time.txt                      # Historical timing benchmarks
├── logs/                             # Runtime logs
│   ├── stargate.log                  # Daemon application log
│   ├── stargate-service.log          # systemd unit output
│   ├── rail_traffic.log              # Deep rail network event log
│   └── telemetry_receiver.log        # TCP telemetry stream log
├── src/                              # Core codebase
│   ├── deploy.sh                     # systemd service installer script
│   ├── GEMINI.md                     # Node-specific operational prompt
│   ├── logging.conf                  # Standardized logging configuration
│   ├── stargate-daemon.py            # Primary Stargate daemon process
│   ├── stargate-daemon.service       # systemd unit definition for Stargate daemon
│   ├── TB2M_SPEC.md                  # T2BM interlayer specification (source of truth)
│   ├── telemetry_listener.py         # Async TCP listener routing incoming telemetry packets
│   ├── diagram/                      # Architectural diagrams and visualization tools
│   │   ├── filesystem.drawio         # Draw.io repository layout diagram
│   │   ├── minecraft.drawio          # Draw.io Minecraft server & zone topology
│   │   ├── minecraft-network.drawio  # Draw.io network hosts & LuckPerms role hierarchy
│   │   ├── network_diagram.py        # Python diagram generator using `diagrams` library
│   │   └── README.md                 # Diagrams index and usage instructions
│   ├── handlers/                     # Event handlers for telemetry
│   │   ├── cart_handler.py           # Processes in-game CART_PASS and minecart detections
│   │   └── README.md                 # Guide for creating new telemetry event handlers
│   ├── internal/                     # Core coordination and AI bridge internals
│   │   ├── registry_manager.py       # Parquet-backed model registry (`registry.parquet`)
│   │   ├── vertex_bridge.py          # Google Gemini API bridge for voxel greebling
│   │   ├── telemetry/                # Internal packet parsing and validation
│   │   │   ├── validator.py          # Strict packet schema validation
│   │   │   └── README.md             # Telemetry internal architecture notes
│   │   └── README.md                 # Internal modules reference and dependencies
│   ├── mcp_server/                   # Model Context Protocol services
│   │   ├── fastmcp.service           # systemd unit definition for FastMCP
│   │   ├── mcp_server.py             # FastMCP server exposing Vertex AI training & tools
│   │   ├── schematic_generator_orchestrator.py # Multi-step MCP building orchestrator
│   │   ├── train_remote.py           # Remote LoRA fine-tuning task for Vertex AI (NVIDIA L4)
│   │   └── README.md                 # FastMCP server documentation and exposed tools
│   ├── rail/                         # Transit and signal automation
│   │   ├── rail_manager.py           # Rail registry management and route switching
│   │   ├── skynet_rail_control.py    # Observer-wall signal tower control via RCON
│   │   └── telemetry_receiver.py     # Rail telemetry processor with LLM orchestration hook
│   ├── server_tools/                 # Minecraft server management utilities
│   │   ├── hardware.txt              # Host address reference table
│   │   ├── main.py                   # Whitelist management entry point
│   │   ├── mcrcon.py                 # Pure-Python MCRCON client implementation (TLS support)
│   │   ├── status.py                 # Server status and ping monitor using `mcstatus`
│   │   └── README.md                 # Server tools guide and protocol details
│   └── utils/                        # Shared utility modules
│       └── config_utils.py           # Unified logging setup and configuration constants
├── test/                             # Automated test suite
│   ├── requirements-test.txt         # Test dependencies
│   ├── test_connectivity.py         # Network reachability and parquet registry schema tests
│   ├── test_content_fetch.py         # MCP documentation content retrieval tests
│   ├── test_end_to_end_sync.py       # End-to-end sync verification
│   └── test_mariadb_mcp.py           # FastMCP client test querying MariaDB on Blowfish
├── emerald_delta.json                # Active Emerald Mirror greeble mutation spec
├── registry.parquet                  # Persistent Parquet block/model registry
├── requirements.txt                  # Production Python dependencies
├── Makefile                          # Build, lint, and deploy targets
└── CHANGELOG.md                      # Detailed version history
```

---

## Subpackages & Core Services

### 1. Stargate Daemon & Telemetry Ingestion
- **Daemon (`src/stargate-daemon.py`):** Starts the async TCP telemetry listener on port `5005` and provides WebSocket dispatch (`dispatch_build_intent`) to remote NPU/TPU workers (`Skynet` and `Edge-T`).
- **Telemetry Listener (`src/telemetry_listener.py`):** Ingests JSON packets, validates them with `internal.telemetry.validator.validate_telemetry_packet`, and routes valid packets to handlers registered in `EVENT_HANDLERS`.
- **Cart Handler (`src/handlers/cart_handler.py`):** Receives `CART_PASS` signals triggered by physical detector rails in Minecraft and forwards them to `RailTelemetryProcessor`.

### 2. FastMCP Server & Training Pipeline
- **FastMCP Server (`src/mcp_server/mcp_server.py`):** Runs on port `8989`. Exposes:
  - `greet`: Diagnostic health check tool.
  - `stage_and_train_vertex`: Uploads tokenized JSONL training sets to Google Cloud Storage (`gs://`) and dispatches non-blocking Vertex AI Custom Training Jobs running LoRA fine-tuning on NVIDIA L4 GPUs.
- **Remote Training Script (`src/mcp_server/train_remote.py`):** Standalone HuggingFace/PEFT training loop executed inside the Vertex AI container (`Gemma-2-2B` LoRA fine-tuning).
- **Service Unit (`src/mcp_server/fastmcp.service`):** Configured for systemd auto-restart on the Raspberry Pi 5 node.

### 3. Rail Network & Signal Control
- **Rail Manager (`src/rail/rail_manager.py`):** Loads and tracks updates to `rail_registry.json` and BlueMap markers.
- **Signal Control (`src/rail/skynet_rail_control.py`):** Controls vertical Observer-Wall Void-Tech signal towers at transit hubs (`HUB_06`, `HUB_03`) via zero-lag RCON block placement (`setblock ... redstone_block` / `air`).
- **Telemetry Receiver (`src/rail/telemetry_receiver.py`):** Integrates telemetry events with LLM-driven priority scheduling for automated minecart routing.

### 4. Internal AI Bridges & Registry
- **Parquet Registry (`src/internal/registry_manager.py`):** High-speed model sync tracking saved to `registry.parquet`. Captures sync timestamp, target host, hardware acceleration (detects Hailo-8L), and token usage.
- **Vertex Bridge (`src/internal/vertex_bridge.py`):** Connects to Google Gemini API (`gemini-1.5-flash-002`) to generate structural greebling deltas (depth, lighting, material contrast). Enforces a strict monthly budget guard (max 150 calls/month).

### 5. Server Tools
- **MCRCON (`src/server_tools/mcrcon.py`):** Thread-safe, pure-Python Minecraft RCON client supporting TLS encryption (`tlsmode=1` or `2`), timeout management, context manager protocols, and interactive CLI operation.
- **Status Checker (`src/server_tools/status.py`):** Probes Paper Minecraft server latency and player rosters using `mcstatus`.

---

## Setup & Deployment

### 1. Hydrate Environment
Run the automated hydration script to configure directories and verify requirements:

```bash
./bin/hydrate.sh
```

Or execute standard Makefile targets:

```bash
make stargate       # Prepares the Python environment and installs dependencies
```

> [!NOTE]
> The target deployment node is an ARM aarch64 Raspberry Pi 5 (`stargate`). Python dependencies requiring compiled binaries (`pyarrow`, `torch`) should match the host architecture.

### 2. Deploy Services
Install and activate the systemd background daemons:

```bash
# Deploy the primary Stargate daemon
sudo cp src/stargate-daemon.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stargate-daemon.service

# Deploy the FastMCP service
sudo cp src/mcp_server/fastmcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fastmcp.service
```

---

## Testing & Quality Assurance

Run the test suite from the repository root:

```bash
# Verify Python source compilation across all modules
python3 -m compileall -q src test

# Run individual pytest modules
pytest test/test_connectivity.py
pytest test/test_content_fetch.py
pytest test/test_end_to_end_sync.py
```

### MariaDB MCP Integration Test
To verify the remote MariaDB FastMCP connection on Blowfish:

```bash
python3 test/test_mariadb_mcp.py
```

---

## Aesthetic & Construction Guidelines

- **Style:** Cyber-noir / Industrial Singularity (William Gibson Neuromancer aesthetic).
- **Primary Materials:** Polished deepslate, tuff tiles, crying obsidian, emerald accents, black concrete backing, pearlescent froglights.
- **Greebling Standard:** High surface depth variation, recessed lighting channels, visible conduit runs, and layered facade plating.
- **Emerald Mirror Module:** See `emerald_delta.json` for the multi-layered 5×5 pillar enhancement specification deployed across the Industrial Singularity zone.

---

## Key References & Subpackage Guides

- [TB2M Spec (`src/TB2M_SPEC.md`)](src/TB2M_SPEC.md) — Intent-to-block protocol specification
- [FastMCP Server Guide (`src/mcp_server/README.md`)](src/mcp_server/README.md) — FastMCP tools, training parameters, and setup
- [Internal Modules Guide (`src/internal/README.md`)](src/internal/README.md) — Parquet registry manager, Vertex bridge, and validator
- [Server Tools Guide (`src/server_tools/README.md`)](src/server_tools/README.md) — Pure Python MCRcon client and status checker
- [Architecture Diagrams (`src/diagram/README.md`)](src/diagram/README.md) — Draw.io filesystem, Minecraft, and network diagrams
- [Telemetry Handlers (`src/handlers/README.md`)](src/handlers/README.md) — Event handler development and registration
- [Emerald Delta Definition (`emerald_delta.json`)](emerald_delta.json) — Active greeble schema for structural pillars
- [Project Context (`docs/CONTEXT.md`)](docs/CONTEXT.md) — Node hardware specifications and network topology
- [CHANGELOG (`CHANGELOG.md`)](CHANGELOG.md) — Detailed version and migration history

---

*Dreamland Control Plane | Bitsmasher Cluster | Updated: November 2026*
