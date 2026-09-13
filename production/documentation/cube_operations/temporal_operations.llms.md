# Temporal Operations

Temporal processes select observations, build regular composites, and apply calculations along a cube’s time dimension.

VITO

EODC

CDSE

Sentinel Hub

Google Earth Engine

> **NOTE:**
>
> The buttons on this page are a documentation aid, not a live capability registry. Use the [openEO Hub](https://hub.openeo.org/) for a cross-backend overview: open **Filters**, select a process under **Processes**, and the Hub shows only matching services. The Hub data is crawled and cached.

> **NOTE:**
>
> The labels identify backends associated with these examples, not a permanent guarantee of capability. Check the backend process listing for its current support.

## Select a time range

Use `filter_temporal` immediately after loading a collection when the temporal extent is not already supplied to `load_collection`. It accepts an inclusive start and exclusive end timestamp, so consecutive intervals can be joined without duplicated observations.

### Python

``` python
import openeo

connection = openeo.connect("https://openeo.vito.be").authenticate_oidc()
cube = connection.load_collection("SENTINEL2_L2A", bands=["B04", "B08"])
growing_season = cube.filter_temporal(["2024-04-01", "2024-10-01"])
```

------------------------------------------------------------------------

## Build monthly composites

Clouds and irregular acquisition dates make raw satellite time series difficult to compare. `aggregate_temporal_period` groups observations into calendar periods and reduces each group. A monthly median is a robust first composite for optical data after cloud masking.

### Python

``` python
monthly_median = growing_season.aggregate_temporal_period(
    period="month",
    reducer="median",
)
monthly_median.download("monthly_median.tif", format="GTiff")
```

Use `aggregate_temporal` instead when you already have explicit date intervals, for example a crop calendar or event-based periods.

## Aggregate explicit time intervals

`aggregate_temporal` reduces user-defined intervals, such as phenological phases or event windows.

``` python
seasonal = growing_season.aggregate_temporal(
  intervals=["2024-04-01", "2024-06-01"],
  reducer="mean",
)
```

------------------------------------------------------------------------

## Apply a reducer along time

`reduce_dimension` is the flexible option for collapsing a dimension. Set `dimension="t"` to derive one raster from the whole time series, such as the maximum NDVI or the number of valid observations.

### Python

``` python
seasonal_maximum = growing_season.reduce_dimension(
    dimension="t",
    reducer="max",
)
```

> **TIP:**
>
> `aggregate_temporal_period` retains a time dimension with one label per period. `reduce_dimension` removes the reduced dimension entirely. Choose the former for a monthly series and the latter for a single seasonal product.

For the definitive schema, consult [`filter_temporal`](https://processes.openeo.org/), [`aggregate_temporal`](https://processes.openeo.org/), [`aggregate_temporal_period`](https://processes.openeo.org/), and [`reduce_dimension`](https://processes.openeo.org/).

## Temporal process details

Each process below has its own backend filter. Generic dimension processes are shown here with `dimension="t"`.

## Align temporal labels

Use `resample_cube_temporal` before merging or comparing cubes whose timestamps do not line up. The target cube supplies the temporal labels and avoids accidentally comparing observations from different dates.

``` python
aligned = source.resample_cube_temporal(target)
```

## Apply a process along time

Use `apply_dimension` with `dimension="t"` when every pixel needs the same custom time-series calculation, such as smoothing or a threshold-based event detector. The callback describes an openEO graph; it is not arbitrary local Python execution.

``` python
smoothed = cube.apply_dimension(
  dimension="t",
  process=lambda series: series.median(),
)
```

## Count observations over time

Use `count` to measure how many valid or matching observations contribute to each pixel. This is useful as a quality layer alongside a temporal mean or median.

``` python
observation_count = cube.count(dimension="t")
```

## Fit a temporal curve

Use `fit_curve` when a time series should be represented by a model, such as a linear trend or seasonal curve. The fitted parameters can then be passed to `predict_curve`.

``` python
model = cube.fit_curve(reducer="linear", parameters={"order": 1})
```

## Predict from a temporal curve

Use `predict_curve` to evaluate a model created by `fit_curve` at new timestamps or labels. This can fill a regular time axis or estimate values at dates not directly observed.

``` python
prediction = model.predict_curve(labels=["2025-01-01", "2025-07-01"])
```

## Calculate a climatological normal

Use `climatological_normal` to calculate a typical value for recurring periods, such as the mean NDVI for each month across several years. It provides the baseline needed for anomaly analysis.

``` python
normal = cube.climatological_normal(period="month", reducer="mean")
```

## Calculate temporal anomalies

Use `anomaly` to express observations as departures from a climatological normal. Positive and negative values then indicate conditions above or below the expected baseline.

``` python
anomalies = cube.anomaly(normal=normal)
```
