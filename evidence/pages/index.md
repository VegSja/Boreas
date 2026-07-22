---
title: Boreas — Avalanche & Weather
---

<Details title="About">
Integrated avalanche danger and weather data across Norwegian regions.
Sourced from the Norwegian Avalanche Warning Service and weather APIs,
transformed through the Boreas dbt gold layer.
</Details>

```sql latest_date
select max(date)::varchar as d from boreas.avalanche_per_region
```

```sql date_bounds
select
  min(date)::varchar as min_d,
  max(date)::varchar as max_d
from boreas.avalanche_per_region
```

## Pick a date

<DateInput
  name=selected_date
  data={latest_date}
  dates=d
  defaultValue={latest_date[0].d}
/>

```sql avalanche_today
select
    region_name,
    region_id,
    danger_level,
    main_text,
    center_lat,
    center_lon
from boreas.avalanche_per_region
where date = '${inputs.selected_date.value}'
```

```sql weather_today
select
    center_lat,
    center_lon,
    max_temp,
    average_temperature,
    min_temp,
    max_snowfall,
    max_rain,
    max_snow_depth,
    max_windspeed,
    weather_type
from boreas.weather_per_region
where date = '${inputs.selected_date.value}'
```

## Danger levels — {inputs.selected_date.value}

<PointMap
  data={avalanche_today}
  lat=center_lat
  long=center_lon
  name=region_name
  value=danger_level
  valueFmt="0"
  pointName=region_name
  height=460
  startingZoom=4
  startingCoords={[65, 15]}
  colorPalette={['#1a9850','#ffff33','#fdae61','#f46d43','#7f0000']}
/>

<Grid cols=5>
  <BigValue data={avalanche_today.filter(r => r.danger_level === 1)} value=region_name agg=count title="Level 1 — Low" fmt="#,##0" />
  <BigValue data={avalanche_today.filter(r => r.danger_level === 2)} value=region_name agg=count title="Level 2 — Moderate" fmt="#,##0" />
  <BigValue data={avalanche_today.filter(r => r.danger_level === 3)} value=region_name agg=count title="Level 3 — Considerable" fmt="#,##0" />
  <BigValue data={avalanche_today.filter(r => r.danger_level === 4)} value=region_name agg=count title="Level 4 — High" fmt="#,##0" />
  <BigValue data={avalanche_today.filter(r => r.danger_level === 5)} value=region_name agg=count title="Level 5 — Extreme" fmt="#,##0" />
</Grid>

## Danger level heatmap by region

```sql heatmap
select
    date,
    region_name,
    avg(danger_level) as danger_level
from boreas.avalanche_per_region
where date >= date '${inputs.selected_date.value}' - interval 60 day
  and date <= date '${inputs.selected_date.value}'
group by date, region_name
order by date
```

<Heatmap
  data={heatmap}
  x=date
  y=region_name
  value=danger_level
  valueFmt=0
  colorPalette={['#1a9850','#ffff33','#fdae61','#f46d43','#7f0000']}
  chartAreaHeight=520
/>

## Explore

- [Avalanche detail](./avalanche)
- [Weather detail](./weather)

## Latest data

<DataTable data={avalanche_today.filter(r => r.region_name)} rows=all search=true>
  <Column id=region_name />
  <Column id=danger_level align=center />
  <Column id=main_text wrap=true />
</DataTable>
