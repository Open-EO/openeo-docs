# Spectral Operations

Spectral operations work across a sensor’s bands. They let you select the information that matters, calculate indices, and add derived bands to a cube.

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

## Select only the required bands

`filter_bands` reduces a cube to named bands or to a wavelength range. Selecting bands early makes a process graph clearer and can substantially reduce processing volume.

### Python

``` python
import openeo

connection = openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent={"west": 4.30, "east": 4.55, "south": 50.80, "north": 50.98},
    temporal_extent=["2024-06-01", "2024-06-30"],
)
red_nir = sentinel2.filter_bands(["B04", "B08"])
```

Band names are collection-specific. Check the collection metadata rather than assuming that every backend uses the same Sentinel band labels.

------------------------------------------------------------------------

## Calculate NDVI

`ndvi` is a convenience process for the normalized difference between near-infrared and red reflectance. It adds an NDVI band while retaining the cube’s spatial and temporal dimensions.

### Python

``` python
ndvi = red_nir.ndvi(nir="B08", red="B04", target_band="NDVI")
ndvi.download("ndvi.tif", format="GTiff")
```

For indices without a dedicated process, use `normalized_difference` or an `apply_dimension` callback with arithmetic processes. For example, normalized difference is suitable for NDWI and NBR when you supply the appropriate pair of input bands.

------------------------------------------------------------------------

## Workflow: combine an index with a temporal composite

Spectral and temporal operations are normally chained. Here the index is calculated for each acquisition and then reduced to a monthly median; this is generally more meaningful than calculating the index from separately aggregated red and NIR bands.

### Python

``` python
monthly_ndvi = (
    red_nir.ndvi(nir="B08", red="B04", target_band="NDVI")
    .aggregate_temporal_period(period="month", reducer="median")
)
```

This is a workflow example rather than a separate process: `ndvi` is calculated per acquisition and `aggregate_temporal_period` then creates the monthly product. The temporal process is documented in the [Temporal Operations](../../documentation/cube_operations/temporal_operations.llms.md) page.

## Spectral process details

Each process below has its own backend filter. Generic dimension processes are shown here with `dimension="bands"`.

## Calculate a normalized difference

Use `normalized_difference` for a two-band index when no dedicated convenience process exists. For example, it can create NDWI from green and near-infrared bands or NBR from near-infrared and shortwave-infrared bands.

``` python
ndwi = cube.normalized_difference(first_band="B03", second_band="B08")
```

## Aggregate an index over time

`aggregate_temporal_period` groups an index into calendar periods such as monthly medians.

``` python
monthly_ndvi = ndvi.aggregate_temporal_period(period="month", reducer="median")
```

## Apply a process across bands

Use `apply_dimension` with `dimension="bands"` when the calculation needs a custom combination of the band array. Prefer a dedicated index process when one exists because its band semantics are clearer.

``` python
derived = cube.apply_dimension(
  dimension="bands",
  process=lambda bands: bands[1] / bands[0],
)
```

## Reduce the band dimension

Use `reduce_dimension` with `dimension="bands"` to collapse several bands into one value, for example a mean brightness or maximum response. The process removes the reduced dimension.

``` python
brightness = cube.reduce_dimension(dimension="bands", reducer="mean")
```

## Scale spectral values

Use `linear_scale_range` to convert stored digital numbers into a physical range before calculating indices or exporting data. Confirm the source scaling in the collection metadata first.

``` python
reflectance = cube.linear_scale_range(
  input_min=0, input_max=10000, output_min=0, output_max=1
)
```

## Select an array element

Use `array_element` when a callback returns an array and the workflow needs one position, such as selecting a particular component from a model result.

``` python
red = openeo.processes.array_element(data=band_array, index=0)
```

## Apply a process to an array

Use `array_apply` when every element of an array should receive the same process graph, for example scaling each value before converting the array back into a cube dimension.

``` python
scaled = openeo.processes.array_apply(
  data=band_array,
  process=lambda value: value.multiply(0.0001),
)
```
