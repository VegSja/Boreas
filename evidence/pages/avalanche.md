---
title: Avalanche detail
---

```sql regions
select distinct region_name from boreas.avalanche_per_region order by 1
```

<Dropdown data={regions} name=region value=region_name defaultValue="Lyngen" />

```sql region_history
select
    date,
    danger_level,
    main_text
from boreas.avalanche_per_region
where region_name = '${inputs.region.value}'
order by date
```

# {inputs.region.value}

## Danger level over time

<LineChart
  data={region_history}
  x=date
  y=danger_level
  yMin=0
  yMax=5
  yAxisTitle="Danger level"
  markers=true
/>

## Distribution of danger levels

```sql region_dist
select
    danger_level::varchar as danger_level,
    count(*) as n
from boreas.avalanche_per_region
where region_name = '${inputs.region.value}'
group by 1
order by 1
```

<BarChart data={region_dist} x=danger_level y=n sort=false />

## Recent warnings

<DataTable data={region_history} rows=25 search=true>
  <Column id=date />
  <Column id=danger_level align=center />
  <Column id=main_text wrap=true />
</DataTable>

## Country-wide daily average

```sql daily_avg
select
    date,
    avg(danger_level) as avg_danger,
    max(danger_level) as max_danger
from boreas.avalanche_per_region
group by date
order by date
```

<LineChart data={daily_avg} x=date y={['avg_danger','max_danger']} yAxisTitle="Danger level" />
