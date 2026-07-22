# Geospatial Job Management and Visualization with OpenEO

When executing algorithms across large spatial areas, it is often necessary to divide the area of interest into smaller regions and run the algorithm on each region independently. To streamline this process and manage multiple jobs simultaneously, the `MultiBackendJobManager` was developed.

In this example, we demonstrate how to process an algorithm across a grid of smaller tiles and visualize job statuses using interactive maps. Our use case involves calculating `Best Available Pixel Composites`, using an openEO Process hosted in the [APEX repository](https://github.com/ESA-APEx).

We will go through the following steps: 1. **Import the required packages** 2. **Generate a Spatial Grid for the Antwerp Region** 3. **Prepare Jobs for Parallel Processing** 4. **Prepare Job visualization with a Custom Color Mapping** 5. **Run the Jobs with MultiBackendJobManager**

### 1. Import the required packages

Before we start, we install the required non-native packages needed this notebook example.

``` python
# %pip install -U "openeo>=0.50" shapely geopandas plotly nbformat kaleido
```

``` python
import time
import copy

import geopandas as gpd
from shapely import wkt

import openeo
from openeo.extra.job_management import (
    MultiBackendJobManager,
    create_job_db,
    get_job_db,
    split_area,
)
from openeo.extra.job_management.process_based import ProcessBasedJobCreator

import plotly.express as px
from plotly import offline
from IPython.display import clear_output
```

## 2. Generate a Spatial-Temporal Grid for the Antwerp Region

To manage our large-scale task efficiently, we split a larger area of interest into smaller tiles with the built-in `split_area()` helper from the openEO Python client.

`split_area()` returns a `GeoDataFrame` in the tiling projection. In this notebook, we convert the tiles to WGS 84 afterwards so the geometries can be visualized with Plotly and passed cleanly to the parameterized process used by `ProcessBasedJobCreator`.

``` python
TILING_PROJECTION = "EPSG:32631"
AREA_OF_INTEREST = {
    "west": 590_000.0,
    "south": 5_660_000.0,
    "east": 610_000.0,
    "north": 5_680_000.0,
    "crs": TILING_PROJECTION,
}
TILE_SIZE = 5_000

grid_df = split_area(
    aoi=AREA_OF_INTEREST,
    tile_size=TILE_SIZE,
    projection=TILING_PROJECTION,
)

# Convert tiles to WGS 84 for Plotly and GeoJSON-style process parameters.
grid_df = grid_df.to_crs("EPSG:4326")
grid_df["id"] = range(len(grid_df))

grid_df
```

### Visualize the tiling grid

We use Plotly to create an interactive visualization of the spatial grid. This allows us to examine the layout of tiles across the area of interest and ensure that the grid aligns correctly with our region.

``` python
# Convert geometries to GeoJSON serializable format
fig = px.choropleth_map(
    grid_df,
    geojson=grid_df,
    locations=grid_df.index,
    map_style="carto-positron",
    center={"lat": 51.15, "lon": 4.4},
    zoom=8,
    title="Spatial Grid for Antwerp Region",
)
fig.update_geos(fitbounds="locations")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
```

### 3. Prepare Jobs for Parallel Processing

In this example, we create Best Available Pixel composites for every tile. For the compositing workflow itself, we directly use the standardized implementation hosted in the [APEX repository](https://github.com/ESA-APEx).

The jobs database is initialized from the `GeoDataFrame` returned by `split_area()` and persisted with `create_job_db()`, which adds the bookkeeping columns needed by the `MultiBackendJobManager`.

For more details, see the cookbook sections on [Preparing the job database](https://open-eo.github.io/openeo-python-client/cookbook/job_manager.html#preparing-the-job-database), [Job Database](https://open-eo.github.io/openeo-python-client/cookbook/job_manager.html#job-database), and [Job creation based on parameterized processes](https://open-eo.github.io/openeo-python-client/cookbook/job_manager.html#job-creation-based-on-parameterized-processes).

``` python
# Make use of the Best Available Pixel openEO process to obtain Sentinel-2 composites
process_graph_url = "https://github.com/ESA-APEx/apex_algorithms/raw/refs/heads/main/algorithm_catalog/vito/bap_composite/openeo_udp/bap_composite.json"

start_job = ProcessBasedJobCreator(
    namespace=process_graph_url,
    parameter_defaults={
        "temporal_extent": ["2024-06-01", "2024-09-01"],
    },
)

# Initiate MultiBackendJobManager
job_manager = MultiBackendJobManager()
connection = openeo.connect(url="openeo.dataspace.copernicus.eu").authenticate_oidc()
job_manager.add_backend("cdse", connection=connection, parallel_jobs=2)

# Create the job tracker file
job_tracker = "jobs.csv"
job_db = create_job_db(job_tracker, df=grid_df, on_exists="skip")
```

### 4. Prepare Job visualization with a Custom Color Mapping

To effectively monitor the progress of geospatial processing tasks, we define a function to visualize job statuses on an interactive map. This visualization uses Plotly, with custom color mappings for each job status, providing a clear overview of the current state of all jobs.

``` python
colors = {
    "not_started": "lightgrey",
    "created": "gold",
    "queued": "lightsteelblue",
    "running": "navy",
    "finished": "lime",
    "error": "darkred",
    "skipped": "darkorange",
    "start_failed": "red",
    None: "grey",  # Default color for any undefined status
}
```

This color scheme makes it easy to distinguish between different statuses. The `plot_job_status` function generates an interactive map.

``` python
# Define the color mapping for job statuses


def plot_job_status(status_df, color_dict):
    status_plot = copy.deepcopy(status_df)
    if len(status_plot) > 0 and isinstance(status_plot["geometry"].iloc[0], str):
        status_plot["geometry"] = status_plot["geometry"].apply(wkt.loads)
    status_plot = gpd.GeoDataFrame(status_plot, geometry="geometry", crs="EPSG:4326")
    status_plot["color"] = (
        status_plot["status"].map(color_dict).fillna(color_dict[None])
    )

    minx, miny, maxx, maxy = status_plot.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    fig = px.choropleth_map(
        status_plot,
        geojson=status_plot.geometry.__geo_interface__,
        locations=status_plot.index,
        color="status",
        color_discrete_map=color_dict,
        map_style="carto-positron",
        center={"lat": center_lat, "lon": center_lon},
        zoom=8,
        title="Job Status Overview",
    )
    fig.update_geos(fitbounds="locations")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig
```

### 5. Running the Jobs with MultiBackendJobManager

Finally, we run the jobs using MultiBackendJobManager, which allows us to manage multiple job executions across. As a standard-user, you can run 2 parallel jobs at any time.

Threading is applied to enable the visualization of job statuses while concurrently running openEO jobs. This approach allows the jobs to execute in parallel with the status updates, ensuring that the map is refreshed regularly without blocking job execution. In total there are two threads:

- Job Execution: The jobs are initiated using the job manager that runs in its own thread. This allows the jobs to be executed asynchronously.
- Visualization: At the same time, we reopen the persisted job database and update the visualization from the current tracked statuses.

For the public thread lifecycle and stop behavior, see [Running in a Background Thread](https://open-eo.github.io/openeo-python-client/cookbook/job_manager.html#running-in-a-background-thread) and [Job Status Tracking](https://open-eo.github.io/openeo-python-client/cookbook/job_manager.html#job-status-tracking).

``` python
# Start a threaded job manager
job_manager.start_job_thread(start_job=start_job, job_db=job_db)

tracked_statuses = [
    "not_started",
    "queued_for_start",
    "created",
    "queued",
    "running",
    "finished",
    "error",
    "canceled",
    "skipped",
    "start_failed",
]
active_statuses = {"not_started", "queued_for_start", "created", "queued", "running"}

try:
    while True:
        status_df = get_job_db(job_tracker).get_by_status(statuses=tracked_statuses)
        fig = plot_job_status(status_df=status_df, color_dict=colors)
        clear_output()
        offline.iplot(fig)

        # Stop once no jobs are left in an active state.
        if status_df["status"].isin(active_statuses).sum() == 0:
            job_manager.stop_job_thread()
            break

        time.sleep(60)  # Wait before the next update

except KeyboardInterrupt:
    job_manager.stop_job_thread()
```
