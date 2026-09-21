# Access MODIS data using openEO

The Copernicus Data Space Ecosystem (CDSE) also offers MODIS (Moderate Resolution Imaging Spectroradiometer), a 36-band multispectral scanner that measures visible-to-thermal-infrared radiances for atmosphere, land, and ocean monitoring. Registered CDSE users can access it directly through the OData API, but if you also want to search, subset, and process the data as part of a larger workflow, accessing them from the STAC catalogue using openEO is often the more convenient solution.

openEO is generally used to run processing directly in the cloud; simple examples include computing vegetation indices, aggregating time series, or masking clouds, without first downloading the underlying data on your own machine. However, the goal of this notebook is to show how to discover and fetch a MODIS collection and access it using openEO.

Before connecting and fetching data with openEO, let’s first explore what MODIS products are available as STAC collections in the CDSE catalogue. For more information about this data, see the documentation: https://documentation.dataspace.copernicus.eu/Data.html

``` python
from pystac_client import Client
import pandas as pd
```

Let’s connect to the CDSE STAC catalogue.

``` python
stac_url = "https://stac.dataspace.copernicus.eu/v1/"
client = Client.open(stac_url)

collections = list(client.get_collections())
print(f"Total collections available in CDSE STAC catalogue: {len(collections)}")
```

    Total collections available in CDSE STAC catalogue: 419

At the time of preparing this notebook, the CDSE STAC catalogue held several hundred collections across many missions. Since we’re only interested in MODIS here, so let us simply filter down to collections whose ID starts with “modis”.

``` python
# get the collection whose id starts with "modis"
modis_collections = [c for c in collections if c.id.startswith("modis")]
print(f"Found {len(modis_collections)} collections that start with 'modis'")
```

    Found 40 collections that start with 'modis'

Each MODIS collection differs by product type, spatial resolution, and temporal revisit(e.g. daily vs 8-day vs 16-day composites). Let’s print a few of them, along with their descriptions, to get a sense of what’s on offer.

``` python
collection_overview = []

for collection in modis_collections[:10]:
    temporal_intervals = collection.extent.temporal.intervals
    temporal_extent = temporal_intervals[0] if temporal_intervals else None

    collection_overview.append(
        {
            "Collection ID": collection.id,
            "Title": collection.title,
            "Temporal extent": temporal_extent
        }
    )

display(pd.DataFrame(collection_overview))
```

|  | Collection ID | Title | Temporal extent |
|----|----|----|----|
| 0 | modis-aqua-myd09a1 | MODIS Aqua Surface Reflectance 8-Day L3 Global... | \[2002-07-04 00:00:00+00:00, None\] |
| 1 | modis-aqua-myd09q1 | MODIS Aqua Surface Reflectance 8-Day L3 Global... | \[2002-07-04 00:00:00+00:00, None\] |
| 2 | modis-aqua-myd10a1 | MODIS Aqua Snow Cover Daily Global 500m | \[2002-07-08 00:00:00+00:00, None\] |
| 3 | modis-aqua-myd10a2 | MODIS Aqua Snow Cover 8-Day L3 Global 500m | \[2002-07-04 00:00:00+00:00, None\] |
| 4 | modis-aqua-myd11a1 | MODIS Aqua Land Surface Temperature Emissivity... | \[2002-07-07 00:00:00+00:00, None\] |
| 5 | modis-aqua-myd11a2 | MODIS Aqua Land Surface Temperature Emissivity... | \[2002-07-04 00:00:00+00:00, None\] |
| 6 | modis-aqua-myd13a1 | MODIS Aqua Vegetation Indices 16-Day L3 Global... | \[2002-07-04 00:00:00+00:00, None\] |
| 7 | modis-aqua-myd13a2 | MODIS Aqua Vegetation Indices 16-Day L3 Global... | \[2002-07-04 00:00:00+00:00, None\] |
| 8 | modis-aqua-myd13q1 | MODIS Aqua Vegetation Indices 16-Day L3 Global... | \[2002-07-04 00:00:00+00:00, None\] |
| 9 | modis-aqua-myd14a1 | MODIS Aqua Thermal Anomalies Fire Daily L3 Glo... | \[2002-07-04 00:00:00+00:00, None\] |

From the list of IDs and descriptions above, let us say we are interested only in the 8-day composite Land Surface Temperature & Emissivity product, for the region of Antwerp, Belgium.

``` python
collection_id = "modis-aqua-myd11a2"
stac_url = f"https://stac.dataspace.copernicus.eu/v1/collections/{collection_id}"
```

Now let’s access this same collection using openEO. Rather than pulling the full global tiles and cropping them ourselves, openEO lets us pass the STAC collection URL along with a spatial and temporal extent, and the subsetting happens on the server side, so we fetch only the data we need.

``` python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

    Authenticated using refresh token.

``` python
stac_cube = connection.load_stac(
    stac_url,
    temporal_extent=["2024-01-01", "2024-01-31"], 
    spatial_extent={"west": 4.137726, "south": 50.986963, "east": 4.994659, "north": 51.334044}
)
```

Now, we submit the openEO batch job, openEO processes it in the CDSE cloud, and we poll until it is done.

``` python
job = stac_cube.create_job(title = "LST Daily MODIS example")
job.start_and_wait()
```

    0:00:00 Job 'j-260818073450443184694a65064e04f1': send 'start'
    0:00:02 Job 'j-260818073450443184694a65064e04f1': created (progress 0%)
    0:00:07 Job 'j-260818073450443184694a65064e04f1': queued (progress 0%)
    0:00:14 Job 'j-260818073450443184694a65064e04f1': queued (progress 0%)
    0:00:22 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:00:32 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:00:44 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:00:59 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:01:18 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:01:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:02:12 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:02:50 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:03:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:04:35 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:05:35 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:06:35 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:07:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:08:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:09:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:10:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:11:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:12:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:13:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:14:36 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:15:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:16:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:17:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:18:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:19:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:20:37 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:21:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:22:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:23:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:24:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:25:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:26:38 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:27:39 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:28:39 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:29:39 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:30:39 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:31:39 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:32:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:33:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:34:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:35:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:36:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:37:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:38:40 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:39:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:40:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:41:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:42:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:43:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:44:41 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:45:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:46:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:47:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:48:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:49:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:50:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:51:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:52:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:53:42 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:54:43 Job 'j-260818073450443184694a65064e04f1': running (progress N/A)
    0:55:43 Job 'j-260818073450443184694a65064e04f1': finished (progress 100%)

``` python
results = job.get_results()
results.download_files("modis_example/")  # Specify your download directory
```

    [WindowsPath('modis_example/openEO_2024-01-01Z.tif'),
     WindowsPath('modis_example/openEO_2024-01-09Z.tif'),
     WindowsPath('modis_example/openEO_2024-01-17Z.tif'),
     WindowsPath('modis_example/openEO_2024-01-25Z.tif'),
     WindowsPath('modis_example/job-results.json')]

With the data downloaded locally, let us visualise it using standard python packages.

The plots shows grid of all the days we fetched to get an overview.

``` python
import os
import glob
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
import imageio.v2 as imageio
```

``` python
import warnings
warnings.filterwarnings("ignore")

folder = "modis_example/"         
pattern = "*.tif"                         

files = sorted(glob.glob(os.path.join(folder, pattern)))
print(f"Found {len(files)} files")

arrays = []
dates = []

for f in files:
    with rasterio.open(f) as src:
        data = src.read(1).astype(float)
        nodata = src.nodata
        if nodata is not None:
            data[data == nodata] = np.nan
        arrays.append(data)
        dates.append(os.path.splitext(os.path.basename(f))[0])

arrays = np.array(arrays)  # shape: (n_days, rows, cols)

# having a consistent color scale across all days
vmin = np.nanpercentile(arrays, 2)
vmax = np.nanpercentile(arrays, 98)

# subplots for each day
n = len(arrays)
ncols = 5
nrows = int(np.ceil(n / ncols))

fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3, nrows * 3))
axes = np.array(axes).reshape(-1)

for i, ax in enumerate(axes):
    if i < n:
        im = ax.imshow(arrays[i], cmap="inferno", vmin=vmin, vmax=vmax)
        ax.set_title(dates[i], fontsize=8)
    ax.axis("off")

fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
fig.colorbar(im, cax=cbar_ax, label="LST")
plt.suptitle("Daily Land Surface Temperature", y=1.02)
plt.tight_layout()
plt.savefig("lst_subplots.png", dpi=150, bbox_inches="tight")
plt.show()
```

    Found 4 files

In this notebook, we explored the MODIS collections offered in the CDSE STAC catalogue, selected one of the products of interest, fetched a subset of it using openEO, and visualised the result both as a time-series grid and as an interactive map layer. The same `load_stac` process can be used for any of the other MODIS collections, or in fact any other STAC collection offered in CDSE STAC.

Back to top
