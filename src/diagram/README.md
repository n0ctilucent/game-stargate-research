# diagrams/ — Architecture Diagrams

This directory stores all architecture, topology, and infrastructure diagrams for the **game-stargate-research** project (Dreamland Stargate / Skynet distributed control plane). All diagrams are in [draw.io / diagrams.net](https://draw.io) format (`.drawio`). Open them with the draw.io desktop app or at [app.diagrams.net](https://app.diagrams.net).

---

## Diagram Index

### `filesystem.drawio` — Project Filesystem Layout
Maps the directory structure of the game-stargate-research repository: top-level files (`Makefile`, `configure.ac`, `requirements.txt`, etc.), source layout, docs, logs, and test directories. Useful for onboarding — gives a quick visual tree of where code, config, and data live.

### `minecraft.drawio` — Minecraft Server Topology
Depicts the Minecraft server architecture: dimensions (Overworld, Nether), BlueMap visualization layer, core plugins (EssentialsX, CoreProtect, WorldGuard), and the deep rail network connecting AI testing hubs. Includes hub coordinates and zone annotations for the Bitsmasher cluster.

### `minecraft-network.drawio` — Network Topology & Role Permissions
Two-page diagram:

1. **machines** — Host inventory across `lab.bitsmasher.net` (Linux Mint / Debian) and DigitalOcean:
   - **chonk.lab.bitsmasher.net** — Chonk host (gateway, orchestration hub)
   - **blowfish.lab.bitsmasher.net** — MariaDB Neural-Data Vault (OpenBSD 7.8, Hub-07)
   - **mc.s1yb0rg.com** — Remote Minecraft server instance
   - **www.bitsmasher.net / LOBBY** — Lobby server

2. **permissions** — LuckPerms role hierarchy with weight-based inheritance:
   - **janitor** (weight 100) — Server Admin, all permissions
   - **sherrif** (weight 99) — Moderator (`/kick`, `/ban`, `/invsee`)
   - **hacker** (weight 20) — Enhanced User (`/fly`, creative gamemode, deathchest)
   - **hobo** (weight 10) — "Look but don't touch" read-only access
   - **ninja** (weight 20) — Survival user (itemsorter, claims, fly disabled, BlueMap visibility)

---

## Editing Diagrams

Draw.io files are plain XML. To edit:

1. Open in [app.diagrams.net](https://app.diagrams.net) → *Open from* → select the `.drawio` file
2. Or open locally with the **draw.io** desktop application (Electron)
3. Save as `.drawio` (editable XML) or export to PNG/PDF for static viewing

The `minecraft-network.drawio` file was last edited with draw.io v29.3.6; older files were created with v19.0.3 and should open without compatibility issues.

---

*Created for theDevilsVoice | Last Updated: 2026-11-06*
