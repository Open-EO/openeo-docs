# Exploring Carbon dynamics from MODIS product in CDSE using openEO

This notebook demonstrates how easily MODIS data accessed and analysed in the Copernicus Data Space Ecosystem (CDSE) using openEO.

As a simple example, we explore vegetation and carbon dynamics over Antwerp. We use MODIS products such as NDVI, GPP and LAI to look at how vegetation changes over time and how this can be related to carbon uptake.

The focus is not on building a complex carbon analysis application, but on showing how an analysis can be done with openEO and executed in the CDSE cloud, without having to download and process the underlying satellite data locally.

Let us first connect to the openEO CDSE backend that offers several MODIS products. To explore more on about the data that are avilable in the CDSE STAC catalogue please visit [this notebook](../../../../client_examples/openeo-community-examples/python/MODIS/MODIS_data_using_openEO.llms.md).

``` python
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

import openeo
```

``` python
connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

    Authenticated using refresh token.

``` python
antwerp_polygon = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [4.04, 51.00],
                        [4.76, 51.00],
                        [4.76, 51.45],
                        [4.04, 51.45],
                        [4.04, 51.00]
                    ]
                ]
            },
            "properties": {}
        }
    ]
}

temporal_extent = ["2025-01-01", "2026-01-01"]
```

Since this notebooks uses several different MODIS products, it is convenient to wrap the STAC-loading logic in a small helper function that takes a collection ID and a list of bands, and returns the corresponding data cube for our area and time range.

``` python
def get_stac_cube(collection, bands):
    url = f"https://stac.dataspace.copernicus.eu/v1/collections/{collection}"
    stac_cube = connection.load_stac(url,
                                     temporal_extent=temporal_extent,
                                     spatial_extent=antwerp_polygon,
                                     bands=bands
                                     )
    return stac_cube
```

We start with NDVI product as an indicator of vegetation greenness and aggregate it spatially to obtain a time series over the area of interest.

``` python
collection_id1 = "modis-aqua-myd13a1"
bands1 = ["500m 16 days NDVI"]
ndvi_cube = get_stac_cube(collection_id1, bands1)
```

``` python
ndvi_ts = ndvi_cube.band("500m 16 days NDVI").aggregate_spatial(
    geometries=antwerp_polygon,
    reducer="mean"
)
```

``` python
ndvi_ts.execute_batch(title="NDVI timeseries in Antwerp", outputfile="carbon/ndvi_timeseries_antwerp.csv")
```

    0:00:00 Job 'j-2609071621044237b12d5f1d315ecfce': send 'start'
    0:00:08 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:00:13 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:00:20 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:00:28 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:00:38 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:00:50 Job 'j-2609071621044237b12d5f1d315ecfce': queued (progress 0%)
    0:01:06 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:01:25 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:01:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:02:19 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:02:57 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:03:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:04:42 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:05:42 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:06:42 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:07:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:08:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:09:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:10:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:11:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:12:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:13:43 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:14:44 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:15:44 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:16:44 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:17:45 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:18:45 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:19:45 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:20:46 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:21:46 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:22:46 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:23:46 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:24:47 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:25:47 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:26:47 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:27:48 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:28:48 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:29:48 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:30:48 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:31:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:32:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:33:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:34:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:35:49 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:36:50 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:37:50 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:38:50 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:39:50 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:40:51 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:41:51 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:42:51 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:43:51 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:44:51 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:45:52 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:46:52 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:47:52 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:48:52 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:49:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:50:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:51:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:52:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:53:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:54:53 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:55:54 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:56:54 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:57:54 Job 'j-2609071621044237b12d5f1d315ecfce': running (progress N/A)
    0:58:55 Job 'j-2609071621044237b12d5f1d315ecfce': finished (progress 100%)

``` python
df = pd.read_csv("carbon/ndvi_timeseries_antwerp.csv", index_col=0)
df.index = pd.to_datetime(df.index)
df = df.sort_index()
plt.figure(figsize=(6, 3))
plt.plot(df.index, df["band_unnamed"], label="NDVI",marker="o")
plt.xticks(rotation=45)
plt.legend()
plt.show()
```

![](CarbonProduces_files/figure-html/cell-9-output-1.png)

The resulting time series shows the expected seasonal variation in vegetation activity, with higher values during the growing season and lower values towards winter.

We then retrieve GPP (Gross Primary Productivity) and use it together with LAI (Leaf Area Index) to derive a simple carbon uptake efficiency indicator.

``` python
collection_id3 = "modis-aqua-myd17a2h"
bands3 = ["Gpp_500m"]
gpp = get_stac_cube(collection_id3, bands3)
```

Let us now access the LAI product, available as 8-day composites. We need LAI specifically for the carbon uptake efficiency calculation: GPP / LAI.

``` python
collection_id2 = "modis-aqua-myd15a2h"
bands2 = ["Lai_500m"]
lai_fpar = get_stac_cube(collection_id2, bands2)
```

Note that `gpp` and `lai_fpar` are still two separate datacubes at this point, so dividing them directly doesn’t align their bands or dimensions properly, so this result isn’t reliable yet. The correct approach is to merge the two cubes first with `merge_cubes`, so their dimensions are aligned, and only then select and divide the specific bands we need to get carbon uptake efficiency.

``` python
merged_cube = gpp.merge_cubes(lai_fpar)
carbon_uptake = merged_cube.band("Gpp_500m")/ merged_cube.band("Lai_500m")
```

``` python
carbon_uptake.execute_batch(title="Carbon Uptake", outputfile="carbon/carbon_uptake_antwerp.nc")
```

    0:00:00 Job 'j-2609071720054af8b861027e4d566e97': send 'start'
    0:00:11 Job 'j-2609071720054af8b861027e4d566e97': created (progress 0%)
    0:00:17 Job 'j-2609071720054af8b861027e4d566e97': queued (progress 0%)
    0:00:23 Job 'j-2609071720054af8b861027e4d566e97': queued (progress 0%)
    0:00:31 Job 'j-2609071720054af8b861027e4d566e97': queued (progress 0%)
    0:00:41 Job 'j-2609071720054af8b861027e4d566e97': queued (progress 0%)
    0:00:53 Job 'j-2609071720054af8b861027e4d566e97': queued (progress 0%)
    0:01:09 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:01:28 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:01:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:02:23 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:03:00 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:03:47 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:04:45 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:05:46 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:06:46 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:07:46 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:08:46 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:09:47 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:10:47 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:11:47 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:12:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:13:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:14:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:15:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:16:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:17:48 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:18:49 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:19:49 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:20:49 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:21:50 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:22:50 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:23:50 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:24:51 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:25:51 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:26:51 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:27:51 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:28:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:29:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:30:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:31:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:32:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:33:52 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:34:53 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:35:53 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:36:53 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:37:54 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:38:54 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:39:54 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:40:54 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:41:55 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:42:55 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:43:57 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:44:57 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:45:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:46:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:47:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:48:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:49:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:50:58 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:51:59 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:52:59 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:53:59 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:55:00 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:56:00 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:57:00 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:58:00 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    0:59:01 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:00:01 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:01:01 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:02:02 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:03:02 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:04:02 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:05:02 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:06:03 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:07:03 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:08:03 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:09:03 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:10:03 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:11:04 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:12:04 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:13:04 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)
    1:14:05 Job 'j-2609071720054af8b861027e4d566e97': running (progress N/A)

``` python
carbon_uptake_ds = xr.open_dataset("carbon/carbon_uptake_antwerp.nc")
carbon_uptake_ds
```

![](data:image/svg+xml;base64,PHN2ZyBzdHlsZT0icG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMDsgaGVpZ2h0OiAwOyBvdmVyZmxvdzogaGlkZGVuIj4KPGRlZnM+CjxzeW1ib2wgaWQ9Imljb24tZGF0YWJhc2UiIHZpZXdib3g9IjAgMCAzMiAzMiI+CjxwYXRoIGQ9Ik0xNiAwYy04LjgzNyAwLTE2IDIuMjM5LTE2IDV2NGMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di00YzAtMi43NjEtNy4xNjMtNS0xNi01eiIgLz4KPHBhdGggZD0iTTE2IDE3Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPHBhdGggZD0iTTE2IDI2Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPC9zeW1ib2w+CjxzeW1ib2wgaWQ9Imljb24tZmlsZS10ZXh0MiIgdmlld2JveD0iMCAwIDMyIDMyIj4KPHBhdGggZD0iTTI4LjY4MSA3LjE1OWMtMC42OTQtMC45NDctMS42NjItMi4wNTMtMi43MjQtMy4xMTZzLTIuMTY5LTIuMDMwLTMuMTE2LTIuNzI0Yy0xLjYxMi0xLjE4Mi0yLjM5My0xLjMxOS0yLjg0MS0xLjMxOWgtMTUuNWMtMS4zNzggMC0yLjUgMS4xMjEtMi41IDIuNXYyN2MwIDEuMzc4IDEuMTIyIDIuNSAyLjUgMi41aDIzYzEuMzc4IDAgMi41LTEuMTIyIDIuNS0yLjV2LTE5LjVjMC0wLjQ0OC0wLjEzNy0xLjIzLTEuMzE5LTIuODQxek0yNC41NDMgNS40NTdjMC45NTkgMC45NTkgMS43MTIgMS44MjUgMi4yNjggMi41NDNoLTQuODExdi00LjgxMWMwLjcxOCAwLjU1NiAxLjU4NCAxLjMwOSAyLjU0MyAyLjI2OHpNMjggMjkuNWMwIDAuMjcxLTAuMjI5IDAuNS0wLjUgMC41aC0yM2MtMC4yNzEgMC0wLjUtMC4yMjktMC41LTAuNXYtMjdjMC0wLjI3MSAwLjIyOS0wLjUgMC41LTAuNSAwIDAgMTUuNDk5LTAgMTUuNSAwdjdjMCAwLjU1MiAwLjQ0OCAxIDEgMWg3djE5LjV6IiAvPgo8cGF0aCBkPSJNMjMgMjZoLTE0Yy0wLjU1MiAwLTEtMC40NDgtMS0xczAuNDQ4LTEgMS0xaDE0YzAuNTUyIDAgMSAwLjQ0OCAxIDFzLTAuNDQ4IDEtMSAxeiIgLz4KPHBhdGggZD0iTTIzIDIyaC0xNGMtMC41NTIgMC0xLTAuNDQ4LTEtMXMwLjQ0OC0xIDEtMWgxNGMwLjU1MiAwIDEgMC40NDggMSAxcy0wLjQ0OCAxLTEgMXoiIC8+CjxwYXRoIGQ9Ik0yMyAxOGgtMTRjLTAuNTUyIDAtMS0wLjQ0OC0xLTFzMC40NDgtMSAxLTFoMTRjMC41NTIgMCAxIDAuNDQ4IDEgMXMtMC40NDggMS0xIDF6IiAvPgo8L3N5bWJvbD4KPC9kZWZzPgo8L3N2Zz4=)

``` xr-text-repr-fallback
<xarray.Dataset> Size: 5GB
Dimensions:  (t: 46, x: 5124, y: 5101)
Coordinates:
  * t        (t) datetime64[ns] 368B 2025-01-01 2025-01-09 ... 2025-12-27
  * x        (x) float64 41kB 5.723e+05 5.723e+05 ... 6.235e+05 6.235e+05
  * y        (y) float64 41kB 5.701e+06 5.701e+06 ... 5.65e+06 5.65e+06
Data variables:
    crs      |S1 1B ...
    var      (t, y, x) float32 5GB ...
Attributes:
    Conventions:  CF-1.9
    institution:  Copernicus Data Space Ecosystem openEO API - 0.73.0a16.dev2...
    description:  
    title:        
```

xarray.Dataset

Dimensions:

- t: 46
- x: 5124
- y: 5101

Coordinates: (3)

t

\(t\)

datetime64\[ns\]

2025-01-01 ... 2025-12-27

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
t

long_name :  
t

axis :  
T

    array(['2025-01-01T00:00:00.000000000', '2025-01-09T00:00:00.000000000',
           '2025-01-17T00:00:00.000000000', '2025-01-25T00:00:00.000000000',
           '2025-02-02T00:00:00.000000000', '2025-02-10T00:00:00.000000000',
           '2025-02-18T00:00:00.000000000', '2025-02-26T00:00:00.000000000',
           '2025-03-06T00:00:00.000000000', '2025-03-14T00:00:00.000000000',
           '2025-03-22T00:00:00.000000000', '2025-03-30T00:00:00.000000000',
           '2025-04-07T00:00:00.000000000', '2025-04-15T00:00:00.000000000',
           '2025-04-23T00:00:00.000000000', '2025-05-01T00:00:00.000000000',
           '2025-05-09T00:00:00.000000000', '2025-05-17T00:00:00.000000000',
           '2025-05-25T00:00:00.000000000', '2025-06-02T00:00:00.000000000',
           '2025-06-10T00:00:00.000000000', '2025-06-18T00:00:00.000000000',
           '2025-06-26T00:00:00.000000000', '2025-07-04T00:00:00.000000000',
           '2025-07-12T00:00:00.000000000', '2025-07-20T00:00:00.000000000',
           '2025-07-28T00:00:00.000000000', '2025-08-05T00:00:00.000000000',
           '2025-08-13T00:00:00.000000000', '2025-08-21T00:00:00.000000000',
           '2025-08-29T00:00:00.000000000', '2025-09-06T00:00:00.000000000',
           '2025-09-14T00:00:00.000000000', '2025-09-22T00:00:00.000000000',
           '2025-09-30T00:00:00.000000000', '2025-10-08T00:00:00.000000000',
           '2025-10-16T00:00:00.000000000', '2025-10-24T00:00:00.000000000',
           '2025-11-01T00:00:00.000000000', '2025-11-09T00:00:00.000000000',
           '2025-11-17T00:00:00.000000000', '2025-11-25T00:00:00.000000000',
           '2025-12-03T00:00:00.000000000', '2025-12-11T00:00:00.000000000',
           '2025-12-19T00:00:00.000000000', '2025-12-27T00:00:00.000000000'],
          dtype='datetime64[ns]')

x

\(x\)

float64

5.723e+05 5.723e+05 ... 6.235e+05

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_x_coordinate

long_name :  
x coordinate of projection

units :  
m

    array([572265., 572275., 572285., ..., 623475., 623485., 623495.],
          shape=(5124,))

y

\(y\)

float64

5.701e+06 5.701e+06 ... 5.65e+06

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_y_coordinate

long_name :  
y coordinate of projection

units :  
m

    array([5701335., 5701325., 5701315., ..., 5650355., 5650345., 5650335.],
          shape=(5101,))

Data variables: (2)

crs

()

\|S1

...

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

crs_wkt :  
PROJCS\["WGS 84 / UTM zone 31N", GEOGCS\["WGS 84", DATUM\["World Geodetic System 1984", SPHEROID\["WGS 84", 6378137.0, 298.257223563, AUTHORITY\["EPSG","7030"\]\], AUTHORITY\["EPSG","6326"\]\], PRIMEM\["Greenwich", 0.0, AUTHORITY\["EPSG","8901"\]\], UNIT\["degree", 0.017453292519943295\], AXIS\["Geodetic longitude", EAST\], AXIS\["Geodetic latitude", NORTH\], AUTHORITY\["EPSG","4326"\]\], PROJECTION\["Transverse_Mercator", AUTHORITY\["EPSG","9807"\]\], PARAMETER\["central_meridian", 3.0\], PARAMETER\["latitude_of_origin", 0.0\], PARAMETER\["scale_factor", 0.9996\], PARAMETER\["false_easting", 500000.0\], PARAMETER\["false_northing", 0.0\], UNIT\["m", 1.0\], AXIS\["Easting", EAST\], AXIS\["Northing", NORTH\], AUTHORITY\["EPSG","32631"\]\]

spatial_ref :  
PROJCS\["WGS 84 / UTM zone 31N", GEOGCS\["WGS 84", DATUM\["World Geodetic System 1984", SPHEROID\["WGS 84", 6378137.0, 298.257223563, AUTHORITY\["EPSG","7030"\]\], AUTHORITY\["EPSG","6326"\]\], PRIMEM\["Greenwich", 0.0, AUTHORITY\["EPSG","8901"\]\], UNIT\["degree", 0.017453292519943295\], AXIS\["Geodetic longitude", EAST\], AXIS\["Geodetic latitude", NORTH\], AUTHORITY\["EPSG","4326"\]\], PROJECTION\["Transverse_Mercator", AUTHORITY\["EPSG","9807"\]\], PARAMETER\["central_meridian", 3.0\], PARAMETER\["latitude_of_origin", 0.0\], PARAMETER\["scale_factor", 0.9996\], PARAMETER\["false_easting", 500000.0\], PARAMETER\["false_northing", 0.0\], UNIT\["m", 1.0\], AXIS\["Easting", EAST\], AXIS\["Northing", NORTH\], AUTHORITY\["EPSG","32631"\]\]

    [1 values with dtype=|S1]

var

(t, y, x)

float32

...

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
var

units :  

grid_mapping :  
crs

    [1202326104 values with dtype=float32]

Indexes: (3)

t

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(DatetimeIndex(['2025-01-01', '2025-01-09', '2025-01-17', '2025-01-25',
                   '2025-02-02', '2025-02-10', '2025-02-18', '2025-02-26',
                   '2025-03-06', '2025-03-14', '2025-03-22', '2025-03-30',
                   '2025-04-07', '2025-04-15', '2025-04-23', '2025-05-01',
                   '2025-05-09', '2025-05-17', '2025-05-25', '2025-06-02',
                   '2025-06-10', '2025-06-18', '2025-06-26', '2025-07-04',
                   '2025-07-12', '2025-07-20', '2025-07-28', '2025-08-05',
                   '2025-08-13', '2025-08-21', '2025-08-29', '2025-09-06',
                   '2025-09-14', '2025-09-22', '2025-09-30', '2025-10-08',
                   '2025-10-16', '2025-10-24', '2025-11-01', '2025-11-09',
                   '2025-11-17', '2025-11-25', '2025-12-03', '2025-12-11',
                   '2025-12-19', '2025-12-27'],
                  dtype='datetime64[ns]', name='t', freq=None))

x

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([572265.0, 572275.0, 572285.0, 572295.0, 572305.0, 572315.0, 572325.0,
           572335.0, 572345.0, 572355.0,
           ...
           623405.0, 623415.0, 623425.0, 623435.0, 623445.0, 623455.0, 623465.0,
           623475.0, 623485.0, 623495.0],
          dtype='float64', name='x', length=5124))

y

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([5701335.0, 5701325.0, 5701315.0, 5701305.0, 5701295.0, 5701285.0,
           5701275.0, 5701265.0, 5701255.0, 5701245.0,
           ...
           5650425.0, 5650415.0, 5650405.0, 5650395.0, 5650385.0, 5650375.0,
           5650365.0, 5650355.0, 5650345.0, 5650335.0],
          dtype='float64', name='y', length=5101))

Attributes: (4)

Conventions :  
CF-1.9

institution :  
Copernicus Data Space Ecosystem openEO API - 0.73.0a16.dev20260817+7

description :  

title :  

``` python
# plot mean carbon uptake over the AOI
carbon_uptake_var = next(
    data_array
    for _, data_array in carbon_uptake_ds.data_vars.items()
    if {"x", "y"}.issubset(data_array.dims)
    and data_array.dtype.kind in "fiu"
    and "t" in data_array.dims
)
mean_carbon_uptake = carbon_uptake_var.mean(dim=["x", "y"], skipna=True)

plt.figure(figsize=(7, 3.5))
plt.plot(
    mean_carbon_uptake.t,
    mean_carbon_uptake,
    marker="o"
)

plt.xlabel("Date")
plt.ylabel("GPP / LAI")
plt.title("Mean Carbon Uptake Efficiency over Antwerp")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
```

![](CarbonProduces_files/figure-html/cell-15-output-1.png)

The results provide a first look at the seasonal dynamics of vegetation and carbon uptake over the study area. NDVI increases through spring, remains relatively high during summer, and decreases again towards autumn and winter. The derived carbon uptake indicator follows a similar seasonal pattern, with generally higher values during the growing season and lower values towards the end of the year. This is a simple example, but it illustrates how MODIS products can be combined to move from satellite observations to a meaningful environmental indicator.

``` python
print("completed successfully")
```

Back to top
