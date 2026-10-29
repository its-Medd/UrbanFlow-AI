<div align="center">

<img src="web/static/ditwin-logo.svg" alt="Ditwin logo" width="220">

# Ditwin

### A digital twin workspace for urban mobility and water planning

Explore Laâyoune in 3D, run road simulations, and evaluate water scenarios using your own data.

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests](https://github.com/its-Medd/UrbanFlow-AI/actions/workflows/tests.yml/badge.svg)](https://github.com/its-Medd/UrbanFlow-AI/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Getting started](#getting-started) ·
[Features](#features) ·
[Architecture](#architecture) ·
[Team](#team) ·
[Acknowledgements](#acknowledgements)

</div>

---

## Overview

A road disruption or a water shortage can affect an entire city. Ditwin provides a workspace for examining these situations through geographic visualization, traffic simulation, and water balance calculations.

The project focuses on Laâyoune while supporting imported georeferenced road networks and user-supplied water measurements.

Ditwin starts with an empty operational workspace. Road inputs, water measurements, and AI credentials must come from the user.

## Features

### Geographic workspace

- Explore mapped buildings in a 3D view.
- Display imported road networks in their geographic locations.
- Inspect road properties and switch map perspectives.
- Use MapLibre and OpenStreetMap without a Mapbox token.

Building geometry comes from external geographic providers. Available heights may be inferred and should not be treated as surveyed measurements.

### Road simulation

- Import georeferenced SUMO networks and matching demand files.
- Configure named simulation runs.
- Execute simulations through the SUMO engine.
- Follow job status and inspect recorded results.
- Review replay, heatmaps, and analysis when their output files are available.

Simulation results describe the supplied traffic demand. They are not live traffic observations.

### Water planning

- Import production, demand, storage, and capacity measurements.
- Retain the source reference and observation timestamp.
- Evaluate production losses and demand reductions.
- Forecast storage over a selected horizon.
- Calculate unmet demand and storage overflow.

The water model uses an hourly storage mass balance with constant rates. It does not simulate hydraulic pressure or control infrastructure.

### Optional AI assistant

- Connect an Anthropic or Groq provider.
- Use the existing AgentSUMO coordination and MCP tools.
- Work with simulation files and analysis through configured integrations.

AI chat remains unavailable until a valid provider credential is configured. Direct road and water workflows do not require an AI key.

## Getting started

### Requirements

| Requirement | Purpose |
|---|---|
| Python 3.12 or 3.13 | Application runtime |
| SUMO 1.24 or later | Road simulation |
| WebGL-capable browser | Interactive map |
| Internet connection | External map tiles and browser resources |
| Node.js and npm | Optional filesystem MCP integration |
| Anthropic or Groq credential | Optional AI assistant |

### Clone the repository

```bash
git clone https://github.com/its-Medd/UrbanFlow-AI.git
cd UrbanFlow-AI
```

### Install on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

### Install on Linux or macOS

```bash
python -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"
cp .env.example .env
```

### Configure the environment

Edit `.env` for your installation.

| Variable | Description |
|---|---|
| `SUMO_HOME` | SUMO installation root containing `bin/sumo` or `bin/sumo.exe` |
| `LLM_PROVIDER` | `anthropic` or `groq` |
| `ANTHROPIC_API_KEY` | Server credential for Anthropic |
| `GROQ_API_KEY` | Server credential for Groq |
| `LLM_MODEL` | Optional tool-capable model identifier |
| `MULTI_AGENT_MODE` | Enables specialist advisory calls through the configured provider |
| `MAPBOX_TOKEN` | Optional public `pk.` token; leave blank for MapLibre and OpenStreetMap |
| `AGENTSUMO_MCP_OUTPUT_BASE` | Optional workspace root; runtime files use `<root>/output` |

SUMO can also be discovered through `PATH`.

Never commit `.env`, private tokens, or provider credentials.

### Start Ditwin

```bash
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Open:

- Application: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Capability status: http://127.0.0.1:8000/api/health

Alternatively, use:

```bash
uv sync --extra dev
uv run ditwin
```

## Road workflow

1. Import a georeferenced `.net.xml` network.
2. Import matching `.rou.xml` or `.trips.xml` demand.
3. Open **Road simulation**.
4. Select the assets, name the run, and choose its duration.
5. Start the simulation and follow its status in **Runs**.
6. Open the available replay, heatmap, or analysis outputs.

Supported run durations range from **30 to 7200 seconds**.

Networks without a geographic projection are rejected because local XY coordinates cannot be positioned reliably on the map. Demand must reference the selected network.

## Water workflow

Open **Water simulation**, select a JSON measurements file, and choose **Import measurements**.

### Required measurement fields

| Field | Description |
|---|---|
| `source` | Source name or dataset reference, up to 200 characters |
| `observed_at` | ISO 8601 observation timestamp including a timezone |
| `production_m3_day` | Production rate in cubic metres per day |
| `demand_m3_day` | Demand rate in cubic metres per day |
| `storage_m3` | Current usable storage in cubic metres |
| `storage_capacity_m3` | Positive usable storage capacity in cubic metres |

Production, demand, and storage must be nonnegative. Storage cannot exceed capacity. Unknown fields and nonfinite numbers are rejected.

Imported measurements are stored in:

```text
output/water/measurements.json
```

Importing a new file replaces the current measurements.

### Forecast settings

- Horizon: **1–168 hours**
- Production loss: **0–100%**
- Demand reduction: **0–100%**

The calculation adjusts the supplied rates, updates storage each hour, and records unmet demand and overflow. The application validates the input structure; users remain responsible for the accuracy and freshness of their measurements.

## Architecture

```text
Browser
   |
   v
FastAPI application
   |
   +-- Geographic workspace
   |      +-- MapLibre / optional Mapbox
   |      +-- OpenStreetMap / OpenFreeMap
   |
   +-- Road workflow
   |      +-- Validated network and demand imports
   |      +-- SUMO execution
   |      +-- Replay, heatmaps and SQLite analysis
   |
   +-- Water workflow
   |      +-- Measurement validation
   |      +-- Hourly storage balance
   |
   +-- Optional AI assistant
          +-- Anthropic / Groq
          +-- SUMO MCP tools
          +-- SQLite MCP integration
          +-- Filesystem MCP integration
```

## Project structure

```text
UrbanFlow-AI/
├── agentsumo/               # AI coordination, clients and configuration
├── agentsumo_mcp/           # SUMO tool server and execution
├── web/
│   ├── app.py               # FastAPI application and AI WebSocket
│   ├── workspace.py         # Imports, readiness and simulation jobs
│   ├── water.py             # Water measurements and forecast API
│   ├── cli.py               # Ditwin command
│   ├── templates/           # Main interface
│   └── static/              # Styles, scripts, branding and vendor assets
├── tests/                   # Automated checks
├── docs/                    # Documentation and upstream references
├── output/                  # Local runtime data, excluded from Git
├── .github/workflows/       # Continuous integration
├── .env.example             # Configuration template
├── pyproject.toml           # Dependencies and package configuration
├── README.md
└── LICENSE
```

The application uses the Ditwin brand. Python package names remain `agentsumo` and `agentsumo_mcp` for compatibility with the upstream implementation.

## Water API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/water/measurements` | Read imported measurements |
| `PUT` | `/api/water/measurements` | Validate and replace measurements |
| `POST` | `/api/water/forecast` | Calculate a storage forecast |

Forecast requests return HTTP **409
