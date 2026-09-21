# Analysing openEO-Generated Interferograms for Earthquake-Induced Surface Deformation

This notebook demonstrates how to use openEO process [`sentinel1_sar_interferogram`](https://algorithm-catalogue.apex.esa.int/apps/sentinel1_sar_interferogram) to generate interferograms over a small area in the Amatrice–Norcia earthquake zone in central Italy. The results are then used to study surface deformation caused by earthquakes.

The computationally intensive interferogram generation is submitted to the Copernicus Data Space openEO backend. The resulting wrapped phase, unwrapped phase, and coherence bands are then downloaded and analysed locally with Python. This avoids the need to download large Sentinel-1 datasets and perform interferogram processing locally, which can be resource-intensive. The workflow aligns the interferograms, filters unreliable measurements, converts unwrapped phase to LOS displacement, and estimates a linear deformation trend over the 2016 earthquake sequence.

The study area and context are inspired by investigations of the 2016 Central Italy earthquake sequence:

- Chini et al. (2017): https://doi.org/10.1002/2017GL073580
- ESA Sentinel-1 Amatrice Earthquake Example: https://step.esa.int/main/gallery/gallery_sen1amatriceearthquake/

However, please note that the notebook is merely for demonstration purposes, has been tested on a relatively small region, and does not aim to reproduce the exact results of these studies.

Let us start by importing the necessary libraries for the analysis.

``` python
# import required libraries
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import openeo
from utils import *
```

### Connect to CDSE backend

As the first step, we connect to the Copernicus Data Space openEO backend and authenticate. This allows us to submit the interferogram generation job to the backend for processing.

``` python
connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

    Authenticated using refresh token.

### Fetch Sentinel-1 interferograms

Now that we are connected to the CDSE backend, let us call the [`sentinel1_sar_interferogram`](https://algorithm-catalogue.apex.esa.int/apps/sentinel1_sar_interferogram) User-Defined-Process (UDP).

This process generates a time series of Sentinel-1 interferometric coherence, wrapped interferograms, and unwrapped interferograms for user‑defined interferometric pairs.

In the following cell, we call the `sentinel1_sar_interferogram` process with VV polarisation, IW1 sub-swath observations over a spatial area in Italy between August and November 2016, and a temporal baseline of 6 days.

A similar workflow has also been discussed in: https://doi.org/10.1002/2016GL071687.

#### CWL in openEO

Rather than reimplementing the InSAR processing chain as an openEO UDF, `sentinel1_sar_interferogram` wraps an existing [Common Workflow Language (CWL)](https://github.com/cloudinsar/s1-workflows/blob/main/sar/sar_interferogram.py) pipeline built on ESA SNAP operators. It was developed by Eurac Research within the [CloudInSAR](https://eo4society.esa.int/projects/cloudinsar/) project, which explores how CWL can package SAR workflows so they run as containerized, backend-agnostic openEO processes rather than bespoke, backend-specific code.

Please note that support for CWL-based processes in openEO remains **experimental** and is presently limited to a handful of backends, including the CDSE federation through Eurac’s implementation.

> **Current limitation:** At present, this process can only be used as the final step of an openEO workflow. The workflow returns a STAC result rather than a native openEO datacube. This means it can currently only be used as the final process-graph node

``` python
s1_interferogram = connection.datacube_from_process(
    "sentinel1_sar_interferogram",
    namespace="https://raw.githubusercontent.com/ESA-APEx/apex_algorithms/refs/heads/main/algorithm_catalog/eurac/sentinel1_sar_interferogram/openeo_udp/sentinel1_sar_interferogram.json",
    polarization="VV",
    sub_swath="IW1",
    spatial_extent={
        "west": 13.10,
        "south": 42.60,
        "east": 13.38,
        "north": 42.78
    },
    temporal_baseline=6,
    temporal_extent = ["2016-08-18", "2016-11-18"]
)
```

As a next step, let us submit the workflow as an openEO job to the CDSE backend. The backend generates interferograms using Sentinel-1 data available in the cloud. This is where the computationally expensive part of the workflow happens in the CDSE cloud environment. The resulting interferograms are then downloaded for further analysis.

``` python
job = s1_interferogram.create_job(title="SAR interferogram VV only")
job.start_and_wait()
```

``` python
result = job.get_results()
result.download_files("sar_interferogram/") 
```

### Analyse interferograms locally

Interferometric Synthetic Aperture Radar (InSAR) is a powerful remote sensing technique that can measure ground displacement with centimetric to millimetric precision. Unlike SAR intensity images, interferograms retain phase information that is sensitive to changes in the distance between the satellite and the Earth’s surface.

Traditionally, InSAR processing requires downloading large volumes of SAR data and performing computationally intensive processing steps locally. However, with the openEO platform, we can leverage cloud-based processing capabilities to generate interferograms directly in the cloud, significantly reducing the need for local resources.

At this point, we have successfully generated interferograms using the openEO backend and downloaded the results for further analysis. The next steps involve: \* loading the interferogram data and visualising it, \* aligning the interferograms to a common grid, \* converting the unwrapped phase to line-of-sight (LOS) displacement, and \* estimating a linear deformation trend over the 2016 earthquake sequence.

Let us start by defining the default settings for plots that will later be used to visualise the interferograms and displacement maps.

``` python
# plot defaults are defined once in utils.py and shared with the coherence notebook
set_plot_defaults()
```

### Load interferogram products generated using the openEO process `sentinel1_sar_interferogram`

Each Interferogram is stored as a GeoTIFF file with three bands: \* wrapped phase: representing the interferometric phase difference restricted to the interval between -π and π radians, \* unwrapped phase: where phase ambiguities have been resolved to obtain a continuous phase field that can be related to surface displacement, \* coherence: which measures the similarity between the two SAR acquisitions and provides an indication of the reliability of the interferometric signal.

The full CWL implementation, including the SNAP graph and processing steps behind these outputs, is available in the [s1-workflows repository](https://github.com/cloudinsar/s1-workflows).

``` python
# let us load all the gtifs, each pair sorted by acquisition date
pairs, crs, tif_paths = load_interferogram_pairs("sar_interferogram/phase_coh_*.tif")
print(f"Loaded {len(pairs)} interferogram pairs from {len(tif_paths)} GeoTIFFs, CRS: {crs}")
```

    Loaded sar_interferogram\phase_coh_20160822T165740_20160828T165658.tif of shape: (1914, 6520)
    Loaded sar_interferogram\phase_coh_20160828T165658_20160903T165740.tif of shape: (1914, 6521)
    Loaded sar_interferogram\phase_coh_20160927T165741_20161003T165659.tif of shape: (1914, 6521)
    Loaded sar_interferogram\phase_coh_20161003T165659_20161009T165741.tif of shape: (1856, 6291)
    Loaded sar_interferogram\phase_coh_20161009T165741_20161015T165659.tif of shape: (1914, 6520)
    Loaded sar_interferogram\phase_coh_20161015T165659_20161021T165741.tif of shape: (1863, 6339)
    Loaded sar_interferogram\phase_coh_20161021T165741_20161027T165659.tif of shape: (1914, 6521)
    Loaded sar_interferogram\phase_coh_20161027T165659_20161102T165741.tif of shape: (1863, 6339)
    Loaded sar_interferogram\phase_coh_20161102T165741_20161108T165659.tif of shape: (1914, 6521)
    Loaded sar_interferogram\phase_coh_20161108T165659_20161114T165741.tif of shape: (1863, 6340)
    Loaded 10 interferogram pairs from 10 GeoTIFFs, CRS: EPSG:4326

Since each interferogram pair has a slightly different footprint (due to orbit geometry), to be able to do pixel-wise comparision, we reproject every pair onto a shared raster grid in the following cell. This will then allow the time dimension to be stacked and later compared pixel by pixel.

``` python
# align all pairs onto a shared raster grid so the time dimension can be stacked
ds = align_interferogram_pairs(pairs, crs)

print(f"Aligned cube shape: {ds['coherence'].shape}")
print(f"Bands in the cube: {list(ds.data_vars)}")
```

    Aligned cube shape: (10, 1924, 6622)
    Bands in the cube: ['wrapped_phase', 'unwrapped_phase', 'coherence']

Before moving on to further analysis, let us quickly visualise the downloaded data:

``` python
# Quicklook: second pair in the stack
plot_interferogram_quicklook(ds, time_idx=1)
```

![](Interferogram_deformation_map_files/figure-html/cell-10-output-1.png)

    (<Figure size 1600x450 with 6 Axes>,
     array([<Axes: title={'center': 'Wrapped phase'}>,
            <Axes: title={'center': 'Unwrapped phase'}>,
            <Axes: title={'center': 'Coherence'}>], dtype=object))

As seen in the quicklook, the wrapped phase shows a characteristic fringe pattern that indicates surface displacement, while the unwrapped phase provides a continuous representation of the displacement field. The coherence map highlights areas of high and low coherence, which can be used to assess the reliability of the measurements.

### Convert unwrapped phase to line-of-sight displacement

The unwrapped phase can be converted to line-of-sight (LOS) displacement using the following formula: \\d = -(λ/4π) × Δφ\\

where, - λ (wavelength) for Sentinel-1 VV = 0.0554 m (https://pmc.ncbi.nlm.nih.gov/articles/PMC7032057/) - Negative values = motion away from the satellite - Positive values = motion toward satellite

For the detailed guide to the process and the underlying theory, please refer to: https://hyp3-docs.asf.alaska.edu/guides/insar_product_guide/

``` python
LAMBDA_M = 0.05546          
COHERENCE_THRESHOLD = 0.50  
GRADIENT_PERCENTILE = 98    

displacement = -(LAMBDA_M / (4 * np.pi)) * ds["unwrapped_phase"]  
```

Once we have converted the unwrapped phase to LOS displacement, we can filter out unreliable measurements using coherence and local phase gradients.

Therefore, in the next step, we will flag pixels with a very steep local phase gradient in each pair. These steep gradients are usually indicative of residual fringe or unwrapping errors rather than real ground motion.

``` python
# mask out pixels with low coherence or steep local phase gradients (likely unwrapping errors)
displacement, gradient_cutoff = mask_unreliable_displacement(ds, displacement, COHERENCE_THRESHOLD, GRADIENT_PERCENTILE)
print(f"Gradient cutoff (98th percentile) per pair: {gradient_cutoff.flatten()}")
print(f"Displacement cube shape: {displacement.shape}, valid fraction per pair: {displacement.notnull().mean(dim=('y', 'x')).values}")
```

    Gradient cutoff (98th percentile) per pair: [14794.885 14765.238 16752.332 17410.479 16683.742 15408.414 15845.177
     14510.612 15859.367 15214.134]
    Displacement cube shape: (10, 1924, 6622), valid fraction per pair: [0.12597459 0.12238932 0.13288314 0.10770742 0.15729062 0.15217686
     0.16145914 0.13822091 0.12489906 0.13644738]

Let us check how many pixels remain or are retained as a valid fraction after filtering based on the above criteria. This will give us an idea of how much valid displacement is available for further analysis.

``` python
# remaining valid fraction of pixels after masking
valid_fraction = displacement.notnull().mean(dim=("y", "x"))
for t, frac in zip(pd.to_datetime(displacement.time.values), valid_fraction.values):
    print(f"{t.date()}: {frac:.1%} pixels retained after coherence/gradient masking")
```

    2016-08-22: 12.6% pixels retained after coherence/gradient masking
    2016-08-28: 12.2% pixels retained after coherence/gradient masking
    2016-09-27: 13.3% pixels retained after coherence/gradient masking
    2016-10-03: 10.8% pixels retained after coherence/gradient masking
    2016-10-09: 15.7% pixels retained after coherence/gradient masking
    2016-10-15: 15.2% pixels retained after coherence/gradient masking
    2016-10-21: 16.1% pixels retained after coherence/gradient masking
    2016-10-27: 13.8% pixels retained after coherence/gradient masking
    2016-11-02: 12.5% pixels retained after coherence/gradient masking
    2016-11-08: 13.6% pixels retained after coherence/gradient masking

### Estimating a linear deformation trend

Each unwrapped interferogram represents the line-of-sight displacement difference between two acquisitions. The following regression is therefore included only as an illustrative pixel-wise analysis. It should not be interpreted as a cumulative deformation time series or as a definitive ground velocity estimate.

First let us convert the acquisition dates to a numeric time axis in days since the first acquisition.

``` python
# prepare displacement stack and time array
displacement_stack = displacement.values  
dates = pd.to_datetime(displacement.time.values)
print(f"Dates of interferogram pairs: {[d.date() for d in dates]}")

# compute the time in days since the first interferogram pair
t_days = (dates - dates[0]).days.to_numpy(dtype="float64")
```

    Dates of interferogram pairs: [datetime.date(2016, 8, 22), datetime.date(2016, 8, 28), datetime.date(2016, 9, 27), datetime.date(2016, 10, 3), datetime.date(2016, 10, 9), datetime.date(2016, 10, 15), datetime.date(2016, 10, 21), datetime.date(2016, 10, 27), datetime.date(2016, 11, 2), datetime.date(2016, 11, 8)]

Next, we will build validity masks and identify pixels with at least two usable observations for a fitted deformation trend to ensure that we have enough data points for a reliable linear fit.

As mentioned earlier, we perform a weighted per-pixel fit of a linear deformation trend over time for each pixel using the valid displacement observations. The main formula followed here is:

\\d = v \cdot t + d_0\\

where, - d = displacement at time t - v = velocity (rate of deformation) - d_0 = initial displacement at the first acquisition

``` python
# fit a per-pixel linear displacement trend over time using the valid observations
velocity, intercept, total_displacement, enough_data, solvable, det = fit_linear_deformation_trend(displacement_stack, t_days)
print(f"Pixels with enough data for linear regression: {enough_data.mean():.1%} of the area")
print(f"Determinant min: {np.nanmin(det)}, max: {np.nanmax(det)}")
print(f"Valid pixels: {np.sum(solvable)} out of {solvable.size} ({100 * np.sum(solvable) / solvable.size:.1f}%)")
print(f"Total displacement range: {np.nanmin(total_displacement):.3f} to {np.nanmax(total_displacement):.3f} m")
print(f"Peak LOS velocity: {np.nanmax(np.abs(velocity)) * 1000:.0f} mm/yr")
```

    Pixels with enough data for linear regression: 27.0% of the area
    Determinant min: 0.0, max: 61681.0
    Valid pixels: 3436696 out of 12740728 (27.0%)
    Total displacement range: -2.754 to 1.936 m
    Peak LOS velocity: 50 mm/yr

Let us now visualise the estimated cumulative LOS displacement and the underlying LOS velocity over the whole period, from the linear-trend fit above.

``` python
# Prepare extent (AOI was requested in EPSG:4326, so the axes are lon/lat)
extent = [float(displacement.x.min()), float(displacement.x.max()),
          float(displacement.y.min()), float(displacement.y.max())]
print(f"Map extent: {extent[0]:.4f} to {extent[1]:.4f}°E, {extent[2]:.4f} to {extent[3]:.4f}°N")

# convert velocity from m/day to mm/yr for easier interpretation
velocity_mm_yr = velocity*1000*365.25  

# plot the total displacement and velocity maps
plot_displacement_velocity_maps(total_displacement, velocity_mm_yr, extent, dates)
```

    Map extent: 12.7236 to 13.9131°E, 42.3933 to 42.7388°N

![](Interferogram_deformation_map_files/figure-html/cell-16-output-2.png)

    (<Figure size 1100x1300 with 4 Axes>,
     array([<Axes: title={'center': 'Total displacement estimate [mm]\n2016-08-22 to 2016-11-08'}, xlabel='Longitude [°]', ylabel='Latitude [°]'>,
            <Axes: title={'center': 'Fitted LOS velocity [mm/yr]\n2016-08-22 to 2016-11-08'}, xlabel='Longitude [°]', ylabel='Latitude [°]'>],
           dtype=object))

In the plot above, we can see the net line-of-sight displacement and the underlying LOS velocity over the entire period, as inferred from the linear-trend fit above. The red areas indicate motion toward the satellite, while the blue areas indicate motion away from the satellite. The white or blank areas represent pixels with fewer valid pairs, which have been masked by coherence or phase-gradient filtering.

Furthermore, let us briefly examine the pixel with the largest fitted displacement and show its raw per-pair measurements against the fitted linear trend. This will help us understand how the linear fit was derived from noisy, partly-masked data, rather than being a literal running total of displacements.

``` python
# find the extreme fitted pixel and its per-pair displacement series
peak_y, peak_x, pixel_displacement, pixel_velocity, pixel_intercept = find_peak_pixel(
    total_displacement, displacement_stack, velocity, intercept
)
print(f"Peak deformation pixel: row {peak_y}, col {peak_x}")
print(f"Fitted displacement over the period: {total_displacement[peak_y, peak_x]:.3f} m")
print(f"Fitted velocity: {pixel_velocity * 365.25 * 1000:.0f} mm/yr "
      f"({'toward satellite' if pixel_velocity > 0 else 'away from satellite'})")
```

    Peak deformation pixel: row 905, col 2620
    Fitted displacement over the period: -2.754 m
    Fitted velocity: -13489 mm/yr (away from satellite)

The selected pixel is the location with the largest absolute fitted displacement estimate.

This information can be useful for understanding the spatial distribution of deformation in the study area and identifying areas of significant ground movement.

To have a better understanding of the deformation trend for that specific pixel, we can also visualise the selected pixel’s valid per-pair displacement measurements along with its fitted linear trend.

``` python
# Plot the raw per-pair measurements against the fitted trend
plot_pixel_displacement_trend(dates, t_days, pixel_displacement, pixel_velocity, pixel_intercept, peak_y, peak_x)
```

![](Interferogram_deformation_map_files/figure-html/cell-18-output-1.png)

    (<Figure size 900x500 with 1 Axes>,
     <Axes: title={'center': 'Displacement trend at the peak-deformation pixel (row 905, col 2620)'}, xlabel='Date', ylabel='LOS displacement [m]'>)

This notebook was a brief demonstration of how an advanced openEO process can be used to generate interferograms and analyse earthquake-induced surface deformation using Sentinel-1 SAR data.

The main idea wasn’t to reproduce the exact results of the studies mentioned earlier, but rather to show how complex InSAR processing can be performed in the cloud using openEO, without the need to download large volumes of SAR data and perform computationally intensive processing steps locally. With openEO, users can leverage the CDSE’s cloud-based processing capabilities via the openEO API and invest resources in detailed analysis of the results, without the overhead of downloading and processing Sentinel-1 data.

Back to top
