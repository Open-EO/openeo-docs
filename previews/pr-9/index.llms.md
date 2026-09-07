🎉 openEO API 1.3.0 released — [read the release notes →](https://github.com/Open-EO/openeo-api/releases/tag/1.3.0)

🌍 1.3.0 now available

Open-EO Standard\
for *Earth Observation Analysis*
================================

**The openEO API** allows users to connect to Earth observation cloud back-ends in a simple and unified way.

[Get Started →](documentation/cookbook.llms.md)

100+

EO Collections

155+

Processes

9+

Backends

What is openEO

One API.\
Any cloud. Any language.
------------------------

Whether you're using Python, R , JavaScript or Julia - **openEO** lets you write your analysis once and run it on any compatible back-end. No vendor lock-in. No rewriting code.

✓

**Standardised processes** Use the same process names across different openEO back-ends

✓

**Datacube concept** Work with spatiotemporal datacubes natively

✓

**Reusable** Share and reuse EO workflows as processes

✓

**Open source** Apache 2.0: inspect, extend, contribute

s

example.py

copy

import openeo \# Connect to any openEO back-end conn = openeo.connect("BACKEND_URL") conn.authenticate_oidc() \# Load Sentinel-2 data as a datacube cube = conn.load_collection( "SENTINEL2_L2A", spatial_extent={"west": 4.0, "east": 4.5, "south": 51.0, "north": 51.5}, temporal_extent=\["2024-06-01", "2024-08-31"\], bands=\["B04", "B08"\] ) \# Compute NDVI ndvi = cube.ndvi(nir="B08", red="B04") ndvi.download("ndvi.nc")

> **CAUTION:**
>
> openEO is not to be confused with independant services that implement the specifications such as [CDSE](https://dataspace.copernicus.eu/). For a list of services built on top of openEO, please visit the [openEO Hub](https://hub.openeo.org/).

With openEO

## Are you interested in…

openEO can be used to process and analyze Earth observation data from diverse sources in a unified and efficient manner.

## Downloading RGB image

Quickly build true-color composites from Sentinel-2 and export clean visuals for maps, reports, and monitoring dashboards.

![](images/feature-explorer/rgb.png)

RGB preview

True-color Sentinel-2 composite output.

**Best for:** EO quicklooks, change communication, report-ready imagery\
**Data used:** Sentinel-2 L2A\
**Outcome:** RGB composite image

[Explore recipe →](documentation/cookbook.llms.md#load-sentinel2-rgb-composite)

## Performing Band Math

Combine spectral bands to derive vegetation and environmental indicators with reusable, cloud-executed openEO pipelines.

![](images/feature-explorer/band-math.png)

Band math preview

Spectral index style output from band combinations.

**Best for:** index workflows and environmental monitoring\
**Data used:** Sentinel-2 L2A\
**Outcome:** EVI Geotiff image

[Run band math →](documentation/cookbook.llms.md#evi-calculation)

## Bringing your own functions

Inject your domain logic with UDFs to extend standard processes while keeping your workflow portable across back-ends.

![](images/feature-explorer/udf.svg)

UDF preview

Workflow extension pattern for custom UDF logic.

**Best for:** custom algorithms and domain-specific logic\
**Data used:** Sentinel-2 L2A\
**Outcome:** custom UDF process

[Build your UDF →](documentation/cookbook.llms.md#cookbook-udfs)

## Share EO workflow as a service

Package your workflow as a user-defined process so teams can execute the same analysis at scale with one endpoint.

![](images/feature-explorer/service.png)

Service preview

API-oriented publishing view for reusable services.

**Best for:** operational teams and repeatable workflows\
**Data used:** Sentinel-2 L2A **Outcome:** reusable UDP service

[Publish workflow →](client_examples/openeo-community-examples/python/RandomForest-ForestFire/RandomForestModelInference_AsUDP.ipynb)

## Large-scale Processing

Orchestrate many jobs over large regions and time ranges while preserving reproducibility and runtime efficiency.

![](images/feature-explorer/large-scale.png)

Large scale preview

Batch processing view for multi-job execution.

**Best for:** regional to continental scale analysis\
**Data used:** Sentinel-2 L2A **Outcome:** batch job results and summaries

[Scale workloads →](client_examples/openeo-community-examples/python/ManagingMultipleLargeScaleJobs/ManagingMultipleLargeScaleJobs.ipynb)

## Using Random Forest

Train and apply machine-learning classifiers directly in your EO workflow to create reproducible land-cover intelligence.

![](images/feature-explorer/random-forest.png)

Random Forest preview

Model training output with classification-ready features.

**Best for:** classification and model-driven EO analysis\
**Data used:** Sentinel-2 L2A and Sentinel-1 GRD **Outcome:** trained model and inference maps

[View notebook →](client_examples/openeo-community-examples/python/RandomForest-ForestFire/RandomForestModelTraining.ipynb)\
[Run notebook (experimental) →](jupyterlite/lab/index.html?path=notebooks/RandomForest-ForestFire/RandomForestModelTraining.ipynb)

Get started

## Choose your path

New to openEO? Start with a guide for your preferred language or tool.

🌐

### Explore the openEO Hub

Find an openEO service and start working with Earth observation data.

→ Open the Hub

📖

### Concepts & Glossary

Understand datacubes, processes, UDFs, and the openEO data model before writing any code.

→ docs_light.html

🔧

### Cookbook

Get started with practical examples and step-by-step guides to use openEO effectively for a specific usecase.

→ Step-by-step guide

🔧

### Built-in openEO Processes

Learn how to use different openEO processes to analyze Earth observation data efficiently using either 🐍 Python, 📊 R or ⚡ JavaScript clients.

→ software list

🗺️

### QGIS Plugin

Access openEO back-ends directly from QGIS with a graphical interface to visualize openEO outputs.

→ QGIS guide

🔧

### For Developers

Build a back-end or client library. API reference, profiles, and implementation guidelines.

→ developer docs

Latest news

## What’s new

| Date | Title | Author |
|----|----|----|
| May 14, 2026 | [OGC publishes openEO as a new Community Standard](news/2026-05-14-openeo-is-an-ogc-community-standard.llms.md) | Matthias Mohr |
| Feb 3, 2026 | [openEO API 1.3.0 and openEO Processes 2.0.0 RC2 released](news/2026-02-03-new-openeo-versions-130-200rc2.llms.md) | Matthias Mohr |
| Dec 22, 2025 | [New openEO QGIS plugin has been released](news/2025-12-22-new-qgis-plugin.llms.md) | Matthias Mohr, Caro Niebl |

![](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdib3g9IjAgMCAyMiAyMiIgZmlsbD0ibm9uZSIgc3R5bGU9InZlcnRpY2FsLWFsaWduOm1pZGRsZTttYXJnaW4tcmlnaHQ6NnB4OyI+PGNpcmNsZSBjeD0iMTEiIGN5PSIxMSIgcj0iMTAiIHN0cm9rZT0iIzdkZDllOCIgc3Ryb2tlLXdpZHRoPSIxLjUiPjwvY2lyY2xlPjxwYXRoIGQ9Ik02IDExIFExMSA1IDE2IDExIFExMSAxNyA2IDExWiIgZmlsbD0iIzdkZDllOCIgb3BhY2l0eT0iMC43IiAvPjwvc3ZnPg==) openEO

The project maintains the API and process specifications, and an open-source ecosystem with clients and server implementations.

#### Documentation

- [Introduction](#)
- [Datacubes](#)
- [Processes](#)
- [Cookbook](#)
- [Authentication](#)

#### Clients

- [CRAN / R](https://cran.r-project.org/package=openeo)
- [npm / JS](https://www.npmjs.com/search?q=%40openeo%2F)
- [PyPI / Python](https://pypi.org/project/openeo/)
- [Conda Forge](https://anaconda.org/conda-forge/openeo)
- [Julia](https://github.com/Open-EO/openeo-julia-client)
- [QGIS](https://plugins.qgis.org/plugins/openeo_plugin/)

© 2026 openEO — Apache 2.0 License  ·  Built with Quarto
