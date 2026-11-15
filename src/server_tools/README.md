# Custom Server Tools

Tools for interacting with Minecraft servers (MCRcon client and status checking).

## Setup

```sh
python -m venv _test
. _test/bin/activate.fish  # or: source _test/bin/activate on bash/zsh
python3 -m pip install -r requirements.txt
```

**Requirements:**

| Package | Source |
|---------|--------|
| `mcstatus` | https://github.com/py-mine/mcstatus |
| `rcon` | https://pypi.org/project/rcon/ |

## Components

### mcrcon.py — RCON Client

A full implementation of the Minecraft Remote Console (RCON) protocol in pure Python. Features include:

- TCP connection to an RCON-enabled Minecraft server
- Password authentication via constructor argument, environment variable (`RCON_PASSWORD`), or interactive prompt
- TLS encryption support (`tlsmode=1` for basic TLS, `tlsmode=2` for self-signed certs)
- Timeout handling (default 5 s; configurable)
- Context manager protocol (`with MCRcon(...) as mcr:`) for safe connection teardown
- Interactive CLI mode: run `python -m mcrcon HOST --password PASS -p PORT`

**MCRcon constructor signature:**

```py
MCRcon(host, password, port=25575, tlsmode=0, timeout=5)
```

**Usage example:**

```python
from mcrcon import MCRcon

mc_pass = os.environ.get("MC_PASS", "dinosaurExTraVaGanZa1969%%")
with MCRcon("127.0.0.1", mc_pass) as mcr:
    resp = mcr.command("/whitelist add bob")
```

### status.py — Server Status Checker

Uses `mcstatus.JavaServer` to probe a live Minecraft server for status, latency, and player information.

**Default target:** `10.10.8.11:25565`

Run it directly to get an overview of the connected server:

```sh
python status.py
```

Example output format:
```
The server has N player(s) online and replied in X ms
The server replied in X ms
```

> **Note:** `query()` requires the `enable-query=true` flag in the server's `server.properties`.

### main.py — Entry Point (Whitelist Tool)

A simple script that uses `MCRcon` to add a player to the whitelist. Demonstrates the standard usage pattern for the RCON client.

```sh
python main.py  # adds "bob" to whitelist; MC_PASS env var overrides default password
```

## Hardware / Infrastructure (from hardware.txt)

| Node | Role | Address:Port |
|------|------|-------------|
| STARGATE_MCP | Orchestrator | 10.10.16.66:8765 |
| SKYNET_CORE | Hailo-8L + USB TPU | 10.10.16.10:8766 |
| EDGE_T_NODE | Asus Tinker Edge-T | 10.10.16.4:8767 |

**Service mapping:**

| Service | Address:Port |
|---------|-------------|
| RCON_BRIDGE | 10.10.8.60:25575 |
| BLUEMAP_API | 10.10.8.60:8100 |

## License

SPDX-License-Identifier: GPL-3.0-or-later  
Copyright © 2022–2025 franklin <franklin@bitsmasher.net>
