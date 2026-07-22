# Hillshade from Copernicus 30_m DEM

Hillshade is a classic terrain visualisation technique: each pixel is assigned a brightness based on how directly its surface faces the sun. Slopes facing the sun are bright; slopes facing away go dark. The result lets the eye read terrain shape immediately, without needing a color scale.

The brightness \\H\\ at each pixel follows the Lambert illumination model:

\\\Large H \\=\\ \sin(\text{alt})\cos\beta \\+\\ \cos(\text{alt})\sin\beta\cos(\text{az}-(\alpha+\pi))\\

| Symbol | Meaning |
|----|----|
| \\H\\ | Hillshade brightness — **0** (surface faces away from the sun) to **1** (surface faces directly toward it) |
| \\\text{alt}\\ | Sun altitude — angle above the horizon; 0° = sunrise/sunset, 90° = directly overhead |
| \\\text{az}\\ | Sun azimuth — compass bearing of the sun, clockwise from North |
| \\\beta\\ | Surface slope — how steep the terrain is (radians) |
| \\\alpha\\ | Surface aspect as returned by the backend (radians) |

The \\\cos(\text{az}-(\alpha+\pi))\\ term drives the lighting: it equals 1 when the slope faces directly toward the sun, 0 when perpendicular, and −1 when facing away. The \\+\pi\\ offset is required because the backend’s `aspect` process returns values that are offset by \\\pi\\ from the downslope direction the formula expects.

## Import required Python libraries

``` python
import math                       # sun angle conversion (degrees → radians)
import numpy as np                # array operations for visualisation
import rasterio                   # read the downloaded GeoTIFF
import matplotlib.pyplot as plt   # display the result
import openeo                     # openEO client
import openeo.processes as eop    # openEO process wrappers: cos, sin, clip
```

## Set parameters

**Bounding box**: the study area (Crete, Greece) as a rectangle in geographic coordinates (WGS 84 decimal degrees).

**Sun position**: `SUN_AZIMUTH = 315` places the sun to the north-west; `SUN_ALTITUDE = 45` puts it halfway up the sky. Both values are in degrees and are converted to radians before use in the hillshade formula.

``` python
bbox = {
    "west":  23.50,   # western longitude boundary (degrees)
    "south": 34.80,   # southern latitude boundary (degrees)
    "east":  26.40,   # eastern longitude boundary (degrees)
    "north": 35.70,   # northern latitude boundary (degrees)
}

SUN_AZIMUTH  = 315   # sun compass bearing, clockwise from North (315 = north-west), in degrees
SUN_ALTITUDE =  45   # sun angle above the horizon (45 = halfway up the sky), in degrees

OUTPUT = "hillshade.tif"
```

## Connect to the backend

openEO is a client–server system: your code runs locally but all the heavy computation such as loading the DEM, deriving slope and aspect, and applying the hillshade formula across millions of pixels, happens on a remote cloud backend. `connect()` points the client at the Copernicus Data Space Ecosystem (CDSE), and `authenticate_oidc()` logs you in via your Copernicus account.

``` python
# Connect to CDSE and authenticate via browser
conn = openeo.connect("https://openeo.dataspace.copernicus.eu")
conn.authenticate_oidc()
```

## Compute hillshade

The hillshade formula needs two terrain properties at each pixel:

- **Slope** (\\\beta\\): how steep the surface is. Flat ground has slope 0; a vertical cliff has slope 90°.
- **Aspect** (\\\alpha\\): the direction the slope faces, expressed as a bearing from North.

Both are computed by the backend using native `slope` and `aspect` processes. The hillshade formula is then applied **pixel-by-pixel** using `apply` and datacube arithmetic.

``` python
# Convert sun angles from degrees to radians for the trig formula
az  = math.radians(SUN_AZIMUTH)
alt = math.radians(SUN_ALTITUDE)

# Load the Copernicus 30 m DEM
dem = conn.load_collection("COPERNICUS_30", spatial_extent=bbox)

# Collapse the time dimension by keeping the max value per pixel across all acquisitions
dem = dem.reduce_dimension(dimension="t", reducer="max")

# Derive slope (steepness in radians) and aspect
slope  = dem.process("slope",  data=dem)
aspect = dem.process("aspect", data=dem)

# Apply the hillshade formula pixel-by-pixel:
# First term: sun elevation contribution scaled by slope angle
# Second term: adjustment for how much the slope faces toward or away from the sun
# Adding π converts the backend's aspect to the downslope convention expected by the hillshade formula
hillshade = (
    math.sin(alt) * slope.apply(eop.cos)                                            # sin(alt)·cos(β)
    + math.cos(alt)
      * slope.apply(eop.sin)                                                         # cos(alt)·sin(β)·...
      * aspect.apply(lambda x: eop.cos(eop.subtract(az, eop.add(x, math.pi))))      #           ...·cos(az−(α+π))
)

# Negative values mean the surface faces away from the sun; clamp to black
hillshade = hillshade.apply(lambda x: eop.clip(x, 0.0, 1.0))
```

## Execute

The process graph built above is **lazy**: nothing has run on the backend yet. This step sends it to CDSE for execution and downloads the result.

Choose the execution mode based on the size of your bbox:

| Mode | When to use | How it works |
|----|----|----|
| **Synchronous** (`download`) | Small areas — city, valley, ~100 km² | Runs immediately; blocks until the file is downloaded. Will time out on large areas. |
| **Batch job** (`execute_batch`) | Large areas — island, region, country | Submits a job to the backend queue; `start_and_wait()` polls until done, then downloads the result. No timeout risk. |

Run **one** of the two cells below.

``` python
# ── Synchronous (small area) *** SKIP IF USING SMALL AREA AND DO NOT WANT TO DOWNLOAD IMAGE ***
# Runs the process graph immediately and saves the result to disk.
hillshade.download(OUTPUT)
```

``` python
# ── Batch job (large area) ───────────────────────────────────────────────────
# Submits the job to the backend queue and polls until complete.
job = hillshade.execute_batch(
    outputfile=OUTPUT,
    title="hillshade",
    job_options={"driver-memory": "4g"},
)
job.start_and_wait()
```

## Visualise

The output is a single-band GeoTIFF with values in \[0, 1\]. Rendered in greyscale, bright areas face the sun and dark areas face away. Mountain ridges, valleys, and the overall shape of the terrain become immediately readable.

``` python
# Read the single band from the GeoTIFF (values in [0, 1])
with rasterio.open(OUTPUT) as src:
    h = src.read(1).astype(np.float32)

fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(h, cmap="gray", vmin=0, vmax=1)   # 0 = black (shadow), 1 = white (full sun)
ax.set_title(f"Hillshade  (az={SUN_AZIMUTH}°, alt={SUN_ALTITUDE}°)")
ax.axis("off")
plt.tight_layout()
plt.show()
```
