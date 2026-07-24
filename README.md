```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
```

**Avalanche Data Platform**

---

## Overview

Boreas is a comprehensive data platform that collects, processes, and visualizes avalanche danger and weather data from Norwegian regions. The platform combines data from multiple sources to provide insights into avalanche conditions and weather patterns.

## Architecture

The platform consists of these main components, all orchestrated by **Dagster**:

| Component | Purpose | Technology |
|-----------|---------|------------|
| **dagster_boreas** | Orchestration (assets, jobs, schedule) | Dagster |
| **dlt_boreas** | Data ingestion pipelines | DLT (Data Load Tool) |
| **dbt_boreas** | Data transformation, modeling, and tests | dbt |
| **evidence** | Analytics dashboard | Evidence.dev (OSS) |
| **elementary** | Data observability & quality report | elementary-data |
| **src** | Shared configuration and data models | Python |

## Data Flow

```
External APIs → DLT Pipelines → DuckDB (Bronze)
                                    ↓
                              dbt Transformations (Silver → Gold)
                                    ↓
                    ┌───────────────┴───────────────┐
              Evidence.dev                    Elementary
           (analytics site)             (data-quality report)
```

1. **Extract** — DLT pipelines fetch data from external APIs
2. **Load** — Raw data is stored in DuckDB (Bronze layer)
3. **Transform** — dbt models clean and aggregate data (Silver/Gold layers). Elementary's dbt package captures test results, freshness, and anomaly metrics into an `elementary` schema on every run.
4. **Visualize** — Evidence.dev renders a static analytics site from the gold layer
5. **Observe** — Elementary generates a self-contained HTML report of test results, source freshness, and anomaly detection

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Boreas

# Install Python dependencies
uv sync

# Install dbt packages (dbt_utils, elementary)
cd dbt_boreas && uv run dbt deps && cd ..

# Install Evidence.dev dependencies (needed for the dashboard asset)
cd evidence && npm install && cd ..
```

### Running the Data Pipeline

The pipeline is orchestrated by **Dagster**. Both dlt ingestion and dbt
transformations are exposed as Dagster assets in `dagster_boreas/`, wired
together automatically via matching asset keys (`1_bronze/<table>` →
`2_silver/*` → `3_gold/*`).

**Launch the Dagster UI:**

```bash
uv run dg dev
```

Then open http://localhost:3000 and click *Materialize all* to run the full
pipeline (dlt bronze → dbt silver → dbt gold). A daily schedule
(`boreas_daily`, 05:00 Europe/Oslo) is defined but stopped by default —
enable it from the *Automation* tab.

**Run without the UI:**

```bash
# Materialize the entire graph
uv run dg launch --assets "*"

# Materialize just the dlt bronze layer
uv run dg launch --assets "1_bronze/*"

# List everything Dagster knows about
uv run dg list defs
```

**Legacy standalone runs (still supported):**

```bash
# dlt pipelines directly
uv run python -m dlt_boreas.run_dlt_pipelines

# dbt from its project dir
cd dbt_boreas && uv run dbt build
```

**Configuration:** dlt settings live in `dlt_boreas/.dlt/config.toml`.

### Evidence.dev Dashboard (OSS)

A static analytics site built with the open-source version of Evidence.dev,
queried directly against the DuckDB gold layer (danger map, region heatmap,
weather trends).

**Local dev:**

```bash
cd evidence
npm install
npm run sources   # materialize queries from ../boreas.duckdb
npm run dev       # http://localhost:3000
```

**Dagster-integrated build:** the `4_reporting/evidence_dashboard` asset
depends on both gold models and runs `evidence sources && evidence build`
after they refresh — so `uv run dg launch --assets "*"` or the daily
schedule regenerates the site into `evidence/build/`. Requires
`node`/`npm` on the host and a one-time `npm install` in `evidence/`.

**Docker:** `docker compose up --build evidence` serves the built site at
`http://localhost:8080` (nginx), with the Elementary report available at
`http://localhost:8080/elementary/`.

### Elementary Data Observability

dbt tests, source freshness, and anomaly detection results are captured
into an `elementary` schema in `boreas.duckdb` by the `elementary` dbt
package (via on-run-end hooks). A dedicated Dagster asset
(`4_reporting/elementary_report`) runs `edr report` after the gold layer
and writes a single self-contained `index.html` to
`evidence/elementary/index.html`.

The file lives **outside** `evidence/build/` so it survives Evidence's
build step, then gets copied into the nginx container and served at
`/elementary/`.

Elementary tests are declared in `dbt_boreas/models/3_gold/schema.yml`
(volume anomalies + column anomalies on `avalanche_per_region` and
`weather_per_region`) and configured to emit **warnings** rather than
errors, so they surface as WARN asset checks in Dagster without failing
the pipeline.

## Project Structure

```
Boreas/
├── src/dagster_boreas/          # Dagster orchestration (assets, jobs, schedule)
│   ├── assets/
│   │   ├── dlt_assets.py       # Bronze ingestion asset wrappers
│   │   ├── dbt_assets.py       # Silver/Gold dbt model assets
│   │   ├── evidence_assets.py  # Evidence.dev build asset
│   │   └── elementary_assets.py# Elementary HTML report asset
│   └── resources/               # DuckDB resource
├── dlt_boreas/                  # Data ingestion (DLT)
│   ├── pipelines/               # Pipeline definitions
│   ├── sources/                 # Data source implementations
│   └── .dlt/config.toml         # dlt runtime config (start/end dates, APIs)
├── dbt_boreas/                  # Data transformation (dbt)
│   ├── models/
│   │   ├── 1_bronze/            # Raw source declarations + freshness
│   │   ├── 2_silver/            # Cleaned data layer
│   │   └── 3_gold/              # Business logic + elementary anomaly tests
│   ├── macros/                  # dbt macros
│   ├── packages.yml             # dbt_utils + elementary
│   └── profiles.yml
├── evidence/                    # Evidence.dev static analytics site
│   ├── pages/                   # Dashboard pages
│   ├── sources/boreas/          # SQL queries against DuckDB gold
│   ├── elementary/index.html    # Elementary report (generated by Dagster)
│   └── build/                   # npm build output (generated)
├── src/config/                  # Norwegian avalanche region catalog
├── src/models/                  # Shared data model classes
├── .dagster_home/               # Dagster instance state (gitignored)
└── boreas.duckdb                # Local warehouse (gitignored)
```

## Data Sources

### Avalanche Data
- **Source**: Norwegian Avalanche Warning Service API
- **Content**: Danger levels, warnings, regional information

### Weather Data
- **Source**: Weather API (forecast and historical)
- **Content**: Temperature, precipitation, wind speed, humidity

### Regional Data
- **Source**: Static configuration
- **Content**: 23 Norwegian avalanche regions with geographic boundaries
- **Coverage**: From Svalbard to Rogaland

## Development

### Adding New Data Sources
1. Create source implementation in `dlt_boreas/sources/`
2. Add pipeline in `dlt_boreas/pipelines/`
3. Update `dlt_boreas/run_dlt_pipelines.py`
4. Create corresponding dbt models

## Dashboard Features

**Evidence.dev site (`/`):**
- **Interactive Maps** — avalanche danger and per-variable weather maps by date
- **Time Series** — per-region danger history and national daily weather trends
- **Heatmap** — 60-day danger level heatmap by region
- **Warning Tables** — searchable, filterable tables of latest warnings

**Elementary report (`/elementary/`):**
- **Test results** — pass/warn/fail status for every dbt test
- **Source freshness** — how recent each bronze table is
- **Anomaly detection** — volume + column anomalies on gold models
- **Model & column lineage** — visual DAG with test coverage

## Configuration

### DLT Configuration
- Configure API endpoints and credentials in `dlt_boreas/.dlt/config.toml`
- Adjust pipeline settings in individual pipeline files

### dbt Configuration
- Database connection settings in `dbt_boreas/profiles.yml`
- Model configurations in `dbt_boreas/dbt_project.yml`

### Evidence Configuration
- Pages live in `evidence/pages/`, source queries in `evidence/sources/boreas/`
- DuckDB path is set via `EVIDENCE_SOURCE__boreas__filename` (Dagster asset
  sets this automatically)

### Elementary Configuration
- Anomaly + volume tests declared in `dbt_boreas/models/3_gold/schema.yml`
- All elementary tests emit `warn` severity (see `dbt_boreas/dbt_project.yml`)
  so they never fail the pipeline
- The `edr` CLI uses `dbt_boreas/profiles.yml`; DuckDB path is passed via
  `BOREAS_DUCKDB_PATH` env var so it resolves correctly regardless of CWD
