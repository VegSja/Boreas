---
title: Weather detail
---

```sql all_dates
select distinct date
from boreas.weather_per_region
order by date desc
```

<DateInput
  name=weather_date
  data={all_dates}
  dates=date
  defaultValue={all_dates[0].date}
/>

```sql weather_map
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
where date = '${inputs.weather_date.value}'
```

## Temperature — {inputs.weather_date.value}

<PointMap
  data={weather_map}
  lat=center_lat
  long=center_lon
  value=average_temperature
  valueFmt="0.0"
  height=420
  startingZoom=4
  startingCoords={[65, 15]}
  colorPalette={['#313695','#74add1','#e0f3f8','#fee090','#f46d43','#a50026']}
/>

<Grid cols=3>
  <BigValue data={weather_map} value=max_temp agg=max title="Max temp (°C)" fmt="0.0" />
  <BigValue data={weather_map} value=average_temperature agg=avg title="Avg temp (°C)" fmt="0.0" />
  <BigValue data={weather_map} value=min_temp agg=min title="Min temp (°C)" fmt="0.0" />
  <BigValue data={weather_map} value=max_snowfall agg=max title="Max snowfall (mm)" fmt="0.0" />
  <BigValue data={weather_map} value=max_rain agg=max title="Max rain (mm)" fmt="0.0" />
  <BigValue data={weather_map} value=max_windspeed agg=max title="Max wind (m/s)" fmt="0.0" />
</Grid>

## Trends (all regions, daily aggregate)

```sql trend
select
    date,
    avg(average_temperature) as avg_temp,
    avg(max_snowfall)        as avg_max_snowfall,
    avg(max_rain)            as avg_max_rain,
    avg(max_snow_depth)      as avg_max_snow_depth,
    avg(max_windspeed)       as avg_max_wind
from boreas.weather_per_region
group by date
order by date
```

<LineChart data={trend} x=date y=avg_temp yAxisTitle="°C" title="Average temperature" />

<Grid cols=2>
  <LineChart data={trend} x=date y=avg_max_snowfall title="Max snowfall (mm)" />
  <LineChart data={trend} x=date y=avg_max_rain title="Max rain (mm)" />
  <LineChart data={trend} x=date y=avg_max_snow_depth title="Max snow depth (cm)" />
  <LineChart data={trend} x=date y=avg_max_wind title="Max wind (m/s)" />
</Grid>

## Recent records

```sql recent
select *
from boreas.weather_per_region
order by date desc
limit 200
```

<DataTable data={recent} rows=20 search=true />
