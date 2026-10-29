# Ditwin

Ditwin is a Python workspace for georeferenced SUMO road simulations and water balance forecasts. It combines a 3D map, recorded simulation replay, heatmaps, SQLite analysis, and an optional AI assistant. The workspace starts empty. No example traffic, artificial water readings, illustrative facility pins, or predefined assistant answers are supplied.

## Install and run

Requirements: Python 3.12 or 3.13, SUMO 1.24+ for traffic execution, and a WebGL browser. The optional AI tool integration also requires Node.js/npm for the filesystem MCP server.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

On Linux/macOS use `source .venv/bin/activate` and `cp .env.example .env`. Alternatively use `uv sync --extra dev` and `uv run ditwin`. Open http://127.0.0.1:8000. API documentation is at `/docs` and capability status at `/api/health`.

## Configuration

| Variable | Purpose |
|---|---|
| `SUMO_HOME` | SUMO installation root containing `bin/sumo` or `bin/sumo.exe`. Discovery through PATH is also supported. |
| `LLM_PROVIDER` | `groq` or `anthropic`. |
| `GROQ_API_KEY`, `ANTHROPIC_API_KEY` | Server credential for the chosen provider. Without a key, chat stays unavailable and direct simulation workflows remain usable. |
| `LLM_MODEL` | Optional tool-capable model identifier. |
| `MULTI_AGENT_MODE` | Optional specialist advisory calls through the configured AI provider. These incur real provider usage. |
| `MAPBOX_TOKEN` | Optional public `pk.` browser token. Leave blank for MapLibre and OpenStreetMap. |
| `AGENTSUMO_MCP_OUTPUT_BASE` | Optional workspace root. The UI and simulation tools use `<root>/output`. |

Keep `.env` and credentials out of Git. Map tiles require internet access. Browser fonts and icons also use external CDNs. Building footprints come from OpenStreetMap via OpenFreeMap. Provider building heights can be inferred and must not be treated as surveyed dimensions. Preserve map attribution.

## Road workflow

1. Import a georeferenced SUMO `.net.xml` and a matching `.rou.xml` or `.trips.xml` using the workspace import control. Files use real geographic coordinates for display. Local XY networks without a projection are rejected.
2. Open **Road simulation**, select both assets, name the run and choose a duration from 30 to 7200 seconds.
3. Review the job in **Runs**. Replay, heatmaps and analysis become available only when their output files exist. SUMO failures surface as failed jobs.

Traffic demand must come from your own data preparation process. Ditwin does not supply measured traffic or generate traffic observations. SUMO outputs are simulations of the input demand, not live road conditions.

## Water workflow

Open **Water simulation**, select a JSON file containing your measurements and click **Import measurements**. All fields are required:

| Field | Required value |
|---|---|
| `source` | Nonempty source name or dataset reference, up to 200 characters |
| `observed_at` | ISO 8601 timestamp including a timezone |
| `production_m3_day` | Measured production rate in cubic metres per day, zero or greater |
| `demand_m3_day` | Measured demand rate in cubic metres per day, zero or greater |
| `storage_m3` | Usable measured storage in cubic metres, zero or greater |
| `storage_capacity_m3` | Positive usable storage capacity, at least the current storage |

Unknown fields, nonfinite numbers and invalid storage ranges are rejected. Data persists locally under `output/water/measurements.json`. Importing replaces the current measurements. Record source and measurement time accurately; the application validates structure but cannot verify that supplied readings are authentic or current.

Choose a forecast horizon of 1–168 hours, production loss and demand reduction percentages. The hourly mass balance applies constant adjusted rates, caps storage at capacity and records unmet demand and overflow. Results retain the source timestamp. This is a planning calculation, not hydraulic pressure modeling, sensor ingestion or infrastructure control. There are no preset production, demand, reserve, district shares or facility coordinates.

API: `PUT /api/water/measurements`, `GET /api/water/measurements`, `POST /api/water/forecast`. Forecasts require imported measurements and otherwise return HTTP 409.

## Architecture

| Component | Location |
|---|---|
| FastAPI routes and AI WebSocket | `web/app.py` |
| Safe imports, readiness and SUMO job queue | `web/workspace.py` |
| Validated water inputs and storage model | `web/water.py` |
| Main map and workspace interface | `web/templates/index.html`, `web/static/workspace.js` |
| Water import and chart interface | `web/static/water.js` |
| Geographic building layer | `web/static/ditwin-city.js` |
| AI coordination and MCP clients | `agentsumo/` |
| SUMO tool server and execution | `agentsumo_mcp/` |
| Local files, job history and SQLite results | `output/` (ignored by Git) |

The Python package names remain `agentsumo` and `agentsumo_mcp` for compatibility with the upstream code. The application command and visual brand are Ditwin. The MIT license and upstream notices remain in place.

## Development checks

```powershell
python -m pytest tests/ -q
git diff --check
git status --short
```

Test fixtures exist only inside tests and temporary test directories. They do not populate the application. GitHub Actions installs development dependencies and runs the test suite. Generated assets, caches, credentials and runtime outputs are excluded from source distribution archives.

## Git handoff

Review your changes and environment before committing:

```powershell
git status --short
git add .
git diff --cached --stat
git commit -m "Prepare Ditwin with imported data workflows"
```

Set the remote to your own Git repository before pushing. This cleanup does not publish to GitHub or alter the existing remote. Verify authentication, network exposure and provider quotas before deployment. The current server is a single-workspace application without user authentication or tenant isolation. Restrict it to trusted users or place access control in front of it.

For a temporary sharing session run `cloudflared tunnel --url http://127.0.0.1:8000`. The backend and tunnel must stay running; a quick tunnel receives a new URL when restarted. This does not make the application a managed production service.
