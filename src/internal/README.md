# Internal — game-stargate-research/src

Core infrastructure modules for the Stargate cluster coordination and telemetry pipeline.

## Structure

```
internal/
├── __init__.py           # Package root (empty)
├── registry_manager.py   # Voxel-payload sync logging via parquet
├── vertex_bridge.py      # Gemini API bridge for greebling metadata enhancement
└── telemetry/            # Telemetry listener internals
    ├── README.md         # Sub-directory docs
    ├── validator.py      # Packet structure validation
    └── __pycache__/      # Compiled bytecode
```

## Modules

### `registry_manager.py` — Registry Manager

Parquet-backed model registry for tracking sync events across cluster nodes.

- **Storage:** Single `registry.parquet` file (path configurable at init).
- **Schema columns:** `model_id`, `version`, `host_target`, `acceleration`, `format`, `vertex_enhanced`, `last_sync`, `tokens_used`.
- **Primary method:** `log_sync_event(model_id, host, enhanced=False)` — appends a row and persists to parquet.
- **Auto-detection:** Detects `skynet` in host name to flag Hailo-8L acceleration; defaults to `"None"` otherwise.

```python
from internal.registry_manager import RegistryManager

rm = RegistryManager("/path/to/registry.parquet")
ts = rm.log_sync_event("gemini-1.5-flash", "10.10.16.10", enhanced=True)
```

### `vertex_bridge.py` — Vertex Bridge

Google Gemini API client that enhances local voxel metadata with AI-generated greebling deltas.

- **Default model:** `gemini-1.5-flash-002`.
- **Budget guard:** Caps vertex-enhanced calls at 150/month via parquet audit (`_check_budget`). Budget exceeded falls back to local Llama-3 reasoning.
- **Primary method:** `enhance_voxels(primitive_metadata, style_tag)` — sends primitive foundation + vision classification context to Gemini and returns a JSON greebling delta (depth, lighting, material contrast).

```python
from internal.vertex_bridge import VertexBridge

vb = VertexBridge(project_id="stargate-cluster", model_name="gemini-1.5-flash-002")
result = vb.enhance_voxels("rectangular_foundation_40x30", "medieval_bastion")
```

### `telemetry/` — Telemetry Listener

Internal telemetry processing logic for the grid-tie sensor network.

#### `validator.py` — Packet Validator

Validates incoming telemetry packets against expected schemas before routing to handlers.

- **Required fields:** `EVENT`, `timestamp`.
- **CART_PASS events:** also requires `coords`.
- Returns `True` on valid, logs error and returns `False` otherwise.

```python
from internal.telemetry.validator import validate_telemetry_packet

valid = validate_telemetry_packet({"EVENT": "CART_PASS", "timestamp": 1234567890, "coords": [100, 64, -200]})
# Returns True

invalid = validate_telemetry_packet({"EVENT": "CART_PASS"})
# Logs "Missing required field: timestamp" and returns False
```

## Dependencies

- `pandas` (parquet I/O)
- `networkx` (graph utilities, imported but not yet used in active code paths)
- `google-genai` (Gemini API client, picked up from `GEMINI_API_KEY` env var or `.envrc`)

## Notes

- `__init__.py` is currently empty; this module is imported directly by path rather than as a package.
- Both `registry_manager.py` and `vertex_bridge.py` default to `registry.parquet` in the working directory — adjust paths for production use.
- Vertex Bridge budget audit runs monthly calendar checks on `last_sync`; consider adding per-day caps for high-frequency testing.
