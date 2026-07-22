# Boreas Evidence Dashboard

Static analytics site for the Boreas avalanche + weather platform, built with
the OSS version of [Evidence.dev](https://evidence.dev) directly against the
gold-layer tables in `boreas.duckdb`.

Pages (in `pages/`):

| Page | Content |
|------|---------|
| `index.md` | Danger-level map for a chosen date, level counters, 60-day heatmap |
| `avalanche.md` | Per-region danger history, distribution, warning table |
| `weather.md` | Weather map + national daily trends (temp, snow, rain, wind) |

## Local development

```bash
cd evidence
npm install
npm run sources   # materialize source queries from ../boreas.duckdb
npm run dev       # http://localhost:3000
```

The DuckDB path is read from `sources/boreas/connection.options.yaml`
(default `../boreas.duckdb`) or the env var
`EVIDENCE_SOURCE__boreas__filename`.

## Production build

```bash
npm run sources
npm run build     # static site → evidence/build/
```

Serve `evidence/build/` with any static server (nginx, Caddy, `npx serve`, …).

## Dagster integration

The `evidence_dashboard` asset in `src/dagster_boreas/assets/evidence_assets.py`
depends on both gold models (`3_gold/avalanche_per_region`,
`3_gold/weather_per_region`) and runs `evidence sources` + `evidence build`
after they materialize, so the daily schedule refreshes the site
automatically. Requires `node` + `npm` on the Dagster host and a one-time
`npm install` inside `evidence/`.
